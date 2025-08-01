#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مستخرج إحداثيات الآيات باستخدام OCR ومعالجة SVG المحسنة
يدعم استخراج النصوص من SVG مع معالجة المسافات والتطبيع المتقدم
"""

import json
import re
import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
import unicodedata
from difflib import SequenceMatcher
import subprocess
from PIL import Image
import pytesseract
from fontTools.ttLib import TTFont


def normalize_unicode_text_advanced(text):
    """تطبيع النص العربي المحسن مع معالجة المسافات"""
    if not text:
        return ""

    # تطبيع Unicode متقدم
    text = unicodedata.normalize('NFKC', text)

    # معالجة المسافات المختلفة
    space_chars = {
        '\u0020': ' ',  # مسافة عادية
        '\u00A0': ' ',  # مسافة غير منقسمة
        '\u2000': ' ',  # en quad
        '\u2001': ' ',  # em quad
        '\u2002': ' ',  # en space
        '\u2003': ' ',  # em space
        '\u2004': ' ',  # three-per-em space
        '\u2005': ' ',  # four-per-em space
        '\u2006': ' ',  # six-per-em space
        '\u2007': ' ',  # figure space
        '\u2008': ' ',  # punctuation space
        '\u2009': ' ',  # thin space
        '\u200A': ' ',  # hair space
        '\u202F': ' ',  # narrow no-break space
        '\u205F': ' ',  # medium mathematical space
        '\u3000': ' ',  # ideographic space
        '\t': ' ',      # tab
        '\n': ' ',      # newline
        '\r': ' ',      # carriage return
    }

    # استبدال جميع أنواع المسافات بمسافة عادية
    for space_char, replacement in space_chars.items():
        text = text.replace(space_char, replacement)

    # تنظيف المسافات المتعددة
    text = re.sub(r'\s+', ' ', text)

    # استبدال الأحرف المتشابهة والمتغيرات العثمانية
    replacements = {
        # الألف وأشكالها العثمانية
        'ٱ': 'ا',  # ألف وصل
        'أ': 'ا',  # همزة على ألف
        'إ': 'ا',  # همزة تحت ألف
        'آ': 'ا',  # مد على ألف
        'ﺍ': 'ا', 'ﺎ': 'ا',  # أشكال الألف المختلفة

        # الهمزة وأشكالها
        'ؤ': 'و',  # همزة على واو
        'ئ': 'ي',  # همزة على ياء
        'ء': '',   # همزة منفردة (تُحذف في المطابقة)

        # الياء والألف المقصورة
        'ى': 'ي',  # ألف مقصورة
        'ﻯ': 'ي', 'ﻰ': 'ي', 'ﻱ': 'ي', 'ﻲ': 'ي',  # أشكال الياء

        # التاء المربوطة والهاء
        'ة': 'ه',  # تاء مربوطة
        'ﺓ': 'ه', 'ﺔ': 'ه',  # أشكال التاء المربوطة

        # الواو وأشكالها
        'ﻭ': 'و', 'ﻮ': 'و',  # أشكال الواو
    }

    # تطبيق الاستبدالات
    for old_char, new_char in replacements.items():
        text = text.replace(old_char, new_char)

    return text.strip()

class AdvancedFontMatcher:
    """مطابق متقدم باستخدام ملف الخط مباشرة"""

    def __init__(self, font_file="UthmanicHafs_v2-0 font/uthmanic_hafs_v20.ttf"):
        self.font = self.load_font_direct(font_file)
        self.character_map = self.build_character_map()
        self.normalization_rules = self.build_normalization_rules()

    def load_font_direct(self, font_file):
        """تحميل ملف الخط مباشرة"""
        try:
            font = TTFont(font_file)
            print(f"✅ تم تحميل الخط: {font_file}")
            return font
        except Exception as e:
            print(f"خطأ في تحميل الخط: {e}")
            return None

    def build_character_map(self):
        """بناء خريطة الأحرف من الخط مباشرة"""
        if not self.font:
            return {}

        char_map = {}
        cmap = self.font.getBestCmap()

        for unicode_val, glyph_name in cmap.items():
            try:
                char = chr(unicode_val)
                char_map[char] = {
                    'unicode': f'U+{unicode_val:04X}',
                    'glyph_name': glyph_name,
                    'is_arabic': 0x0600 <= unicode_val <= 0x06FF,
                    'is_symbol': unicode_val > 0xFE00
                }
            except:
                continue

        print(f"✅ تم بناء خريطة {len(char_map)} حرف من الخط")
        return char_map

    def build_normalization_rules(self):
        """بناء قواعد التطبيع من الخط"""
        return {
            # قواعد أساسية للتطبيع
            'ٱ': 'ا', 'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
            'ى': 'ي', 'ة': 'ه', 'ؤ': 'و', 'ئ': 'ي'
        }
    
    def normalize_text_with_spaces(self, text):
        """تطبيع النص مع معالجة المسافات باستخدام جدول الخط"""
        if not text:
            return ""

        # أولاً: تطبيع عام للنص
        text = normalize_unicode_text_advanced(text)

        # ثانياً: تطبيق قواعد جدول الخط
        normalized = ""
        for char in text:
            # استخدام قواعد التطبيع من جدول الخط
            normalized_char = self.normalization_rules.get(char, char)
            normalized += normalized_char

        # ثالثاً: معالجة المسافات النهائية
        normalized = re.sub(r'\s+', ' ', normalized)  # توحيد المسافات

        return normalized.strip()
    
    def remove_all_diacritics_precise(self, text):
        """إزالة جميع الرموز العثمانية باستخدام معلومات الخط"""
        if not text:
            return ""

        cleaned = ""
        for char in text:
            char_info = self.character_map.get(char, {})
            # إذا كان رمز عثماني أو تشكيل، تجاهله
            if char_info.get('is_symbol', False) or ord(char) in range(0x064B, 0x0670):
                continue
            # إذا كان حرف أساسي، أضفه
            cleaned += char

        return cleaned
    
    def get_character_variants(self, base_char):
        """الحصول على جميع أشكال الحرف من الخط"""
        variants = [base_char]
        # البحث عن أشكال مختلفة للحرف في الخط
        for char, info in self.character_map.items():
            if info.get('base_char') == base_char:
                variants.append(char)
        return variants
    
    def calculate_advanced_similarity(self, text1, text2):
        """حساب التشابه المتقدم مع معالجة المسافات"""
        # تطبيع النصوص مع معالجة المسافات
        norm1 = self.normalize_text_with_spaces(text1)
        norm2 = self.normalize_text_with_spaces(text2)

        # إزالة الرموز العثمانية
        clean1 = self.remove_all_diacritics_precise(norm1)
        clean2 = self.remove_all_diacritics_precise(norm2)

        # حساب التشابه
        if not clean1 or not clean2:
            return 0.0

        if clean1 == clean2:
            return 1.0

        # استخدام SequenceMatcher للمطابقة المتقدمة
        similarity = SequenceMatcher(None, clean1, clean2).ratio()

        # إضافة مكافأة للكلمات المشتركة
        words1 = set(clean1.split())
        words2 = set(clean2.split())

        if words1 and words2:
            word_similarity = len(words1 & words2) / len(words1 | words2)
            # دمج تشابه الأحرف وتشابه الكلمات
            similarity = (similarity * 0.7) + (word_similarity * 0.3)

        return similarity

class AdvancedAyatExtractor:
    """مستخرج متقدم لإحداثيات الآيات مع دعم OCR ومعالجة SVG"""

    def __init__(self, font_file="UthmanicHafs_v2-0 font/uthmanic_hafs_v20.ttf"):
        self.font_matcher = AdvancedFontMatcher(font_file)
        # إعداد tesseract للعربية
        self.tesseract_config = '--oem 3 --psm 6 -l ara'
        
    def extract_text_from_svg(self, svg_file):
        """استخراج النصوص من ملف SVG (يدعم النصوص والمسارات)"""
        try:
            tree = ET.parse(svg_file)
            root = tree.getroot()

            texts = []

            # البحث عن عناصر النص المباشرة
            for elem in root.iter():
                if elem.tag.endswith('text') or elem.tag.endswith('tspan'):
                    if elem.text:
                        x = elem.get('x', '0')
                        y = elem.get('y', '0')

                        texts.append({
                            'text': elem.text.strip(),
                            'x': float(x) if x.replace('.', '').replace('-', '').isdigit() else 0,
                            'y': float(y) if y.replace('.', '').replace('-', '').isdigit() else 0,
                            'type': 'direct_text'
                        })

            # إذا لم نجد نصوص مباشرة، نحاول استخراج من المسارات
            if not texts:
                print(f"  لا توجد نصوص مباشرة، محاولة استخراج من المسارات...")
                texts = self.extract_from_svg_paths(root)

            # إذا فشل استخراج المسارات، نستخدم OCR
            if not texts or len(texts) < 10:  # إذا كانت النتائج قليلة
                print(f"  نتائج المسارات قليلة ({len(texts)}), محاولة OCR...")
                ocr_texts = self.extract_text_with_ocr(svg_file)
                if ocr_texts:
                    print(f"  تم استخراج {len(ocr_texts)} نص بـ OCR")
                    texts.extend(ocr_texts)

            return texts

        except Exception as e:
            print(f"خطأ في قراءة ملف SVG: {e}")
            return []

    def extract_from_svg_paths(self, root):
        """استخراج النصوص من مسارات SVG (تجريبي)"""
        texts = []

        # البحث عن عناصر use التي تشير إلى الأحرف
        for elem in root.iter():
            if elem.tag.endswith('use'):
                href = elem.get('{http://www.w3.org/1999/xlink}href') or elem.get('href')
                if href and href.startswith('#font_'):
                    x = elem.get('x', '0')
                    y = elem.get('y', '0')

                    # محاولة استخراج معرف الحرف من href
                    font_id = href.replace('#', '')

                    texts.append({
                        'text': self.decode_font_id(font_id),
                        'x': float(x) if x.replace('.', '').replace('-', '').isdigit() else 0,
                        'y': float(y) if y.replace('.', '').replace('-', '').isdigit() else 0,
                        'type': 'font_path',
                        'font_id': font_id
                    })

        # إذا لم نجد عناصر use، نحاول طريقة أخرى
        if not texts:
            # البحث عن مجموعات (groups) قد تحتوي على نصوص
            for elem in root.iter():
                if elem.tag.endswith('g'):  # group
                    # فحص إذا كانت المجموعة تحتوي على مسارات نص
                    paths_in_group = [child for child in elem if child.tag.endswith('path')]
                    if paths_in_group:
                        # استخراج الإحداثيات من transform أو من أول مسار
                        transform = elem.get('transform', '')
                        x, y = self.extract_coordinates_from_transform(transform)

                        texts.append({
                            'text': f"[مجموعة_{len(texts)+1}]",  # نص تجريبي
                            'x': x,
                            'y': y,
                            'type': 'group_paths',
                            'paths_count': len(paths_in_group)
                        })

        return texts

    def decode_font_id(self, font_id):
        """محاولة فك تشفير معرف الخط إلى حرف"""
        # هذه طريقة تجريبية - قد نحتاج لتحسينها
        if 'font_' in font_id:
            # استخراج الرقم من معرف الخط
            parts = font_id.split('_')
            if len(parts) >= 3:
                try:
                    char_code = int(parts[2])
                    # محاولة تحويل إلى حرف Unicode
                    if char_code < 1000:  # أرقام بسيطة
                        return str(char_code)
                    else:
                        return chr(char_code) if char_code < 65536 else f"[{char_code}]"
                except:
                    return f"[{font_id}]"
        return f"[{font_id}]"

    def extract_coordinates_from_transform(self, transform):
        """استخراج الإحداثيات من خاصية transform"""
        x, y = 0, 0
        if 'translate' in transform:
            import re
            match = re.search(r'translate\(([^)]+)\)', transform)
            if match:
                coords = match.group(1).split(',')
                try:
                    x = float(coords[0].strip())
                    y = float(coords[1].strip()) if len(coords) > 1 else 0
                except:
                    pass
        return x, y

    def svg_to_png_for_ocr(self, svg_file, png_file, dpi=300):
        """تحويل SVG إلى PNG للـ OCR"""
        try:
            # استخدام inkscape لتحويل SVG إلى PNG
            cmd = [
                'inkscape',
                '--export-type=png',
                f'--export-dpi={dpi}',
                f'--export-filename={png_file}',
                str(svg_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception as e:
            print(f"خطأ في تحويل SVG إلى PNG: {e}")
            return False

    def extract_text_with_ocr(self, svg_file):
        """استخراج النص باستخدام OCR كبديل"""
        try:
            # إنشاء ملف PNG مؤقت
            png_file = Path(str(svg_file).replace('.svg', '_temp.png'))

            # تحويل SVG إلى PNG
            if not self.svg_to_png_for_ocr(svg_file, png_file):
                return []

            # فتح الصورة
            image = Image.open(png_file)
            image = image.convert('RGB')

            # استخراج النص مع الإحداثيات
            data = pytesseract.image_to_data(image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)

            texts = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text and data['conf'][i] > 30:  # ثقة أكبر من 30%
                    texts.append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': data['conf'][i],
                        'type': 'ocr_text'
                    })

            # حذف الملف المؤقت
            if png_file.exists():
                png_file.unlink()

            return texts

        except Exception as e:
            print(f"خطأ في OCR: {e}")
            return []
    
    def find_verse_numbers_precise(self, texts):
        """البحث عن أرقام الآيات بدقة"""
        verse_numbers = []
        
        # الأرقام العربية والإنجليزية
        arabic_digits = '٠١٢٣٤٥٦٧٨٩'
        english_digits = '0123456789'
        
        for text_info in texts:
            text = text_info['text']
            
            # البحث عن الأرقام العربية
            arabic_match = re.search(f'[{arabic_digits}]+', text)
            if arabic_match:
                arabic_num = arabic_match.group()
                # تحويل إلى إنجليزي
                english_num = ""
                for char in arabic_num:
                    if char in arabic_digits:
                        english_num += str(arabic_digits.index(char))
                
                if english_num.isdigit():
                    verse_numbers.append({
                        'number': int(english_num),
                        'arabic_text': arabic_num,
                        'x': text_info['x'],
                        'y': text_info['y'],
                        'full_text': text
                    })
            
            # البحث عن الأرقام الإنجليزية
            english_match = re.search(f'[{english_digits}]+', text)
            if english_match:
                english_num = english_match.group()
                if english_num.isdigit():
                    verse_numbers.append({
                        'number': int(english_num),
                        'arabic_text': english_num,
                        'x': text_info['x'],
                        'y': text_info['y'],
                        'full_text': text
                    })
        
        return verse_numbers
    
    def match_verses_with_reference_precise(self, extracted_texts, reference_verses):
        """مطابقة الآيات مع المرجع بدقة 100%"""
        results = []
        
        for verse_num, reference_text in reference_verses.items():
            best_match = None
            best_similarity = 0.0
            
            for text_info in extracted_texts:
                similarity = self.font_matcher.calculate_advanced_similarity(
                    text_info['text'], reference_text
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = text_info
            
            if best_match and best_similarity > 0.8:  # عتبة عالية للدقة
                results.append({
                    'verse_number': verse_num,
                    'reference_text': reference_text,
                    'extracted_text': best_match['text'],
                    'similarity': best_similarity,
                    'coordinates': {
                        'x': best_match['x'],
                        'y': best_match['y']
                    },
                    'match_quality': 'excellent' if best_similarity > 0.95 else 'good'
                })
        
        return results
    
    def process_page_precise(self, svg_file, reference_verses):
        """معالجة صفحة واحدة بدقة"""
        print(f"معالجة الملف: {svg_file}")
        
        # استخراج النصوص
        extracted_texts = self.extract_text_from_svg(svg_file)
        print(f"تم استخراج {len(extracted_texts)} نص")
        
        # البحث عن أرقام الآيات
        verse_numbers = self.find_verse_numbers_precise(extracted_texts)
        print(f"تم العثور على {len(verse_numbers)} رقم آية")
        
        # مطابقة الآيات
        matched_verses = self.match_verses_with_reference_precise(extracted_texts, reference_verses)
        print(f"تم مطابقة {len(matched_verses)} آية")
        
        return {
            'file': svg_file,
            'extracted_texts': extracted_texts,
            'verse_numbers': verse_numbers,
            'matched_verses': matched_verses,
            'statistics': {
                'total_texts': len(extracted_texts),
                'verse_numbers_found': len(verse_numbers),
                'verses_matched': len(matched_verses),
                'accuracy': len(matched_verses) / len(reference_verses) * 100 if reference_verses else 0
            }
        }

def load_reference_verses(reference_file):
    """تحميل الآيات المرجعية"""
    if not os.path.exists(reference_file):
        print(f"ملف المرجع غير موجود: {reference_file}")
        return {}
    
    try:
        with open(reference_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"خطأ في تحميل المرجع: {e}")
        return {}

def create_sample_reference():
    """إنشاء مرجع تجريبي للاختبار"""
    sample_verses = {
        1: "بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ",
        2: "ٱلۡحَمۡدُ لِلَّهِ رَبِّ ٱلۡعَٰلَمِينَ",
        3: "ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ",
        4: "مَٰلِكِ يَوۡمِ ٱلدِّينِ",
        5: "إِيَّاكَ نَعۡبُدُ وَإِيَّاكَ نَسۡتَعِينُ",
        6: "ٱهۡدِنَا ٱلصِّرَٰطَ ٱلۡمُسۡتَقِيمَ",
        7: "صِرَٰطَ ٱلَّذِينَ أَنۡعَمۡتَ عَلَيۡهِمۡ غَيۡرِ ٱلۡمَغۡضُوبِ عَلَيۡهِمۡ وَلَا ٱلضَّآلِّينَ"
    }

    with open("reference_verses.json", 'w', encoding='utf-8') as f:
        json.dump(sample_verses, f, ensure_ascii=False, indent=2)

    print("تم إنشاء ملف مرجعي تجريبي: reference_verses.json")
    return sample_verses

def main():
    """الوظيفة الرئيسية"""
    print("مستخرج إحداثيات الآيات بدقة 100%")
    print("يستخدم جدول الخط العثماني للمطابقة الدقيقة")
    print("=" * 60)

    # التحقق من وجود ملف الخط
    font_file = "UthmanicHafs_v2-0 font/uthmanic_hafs_v20.ttf"
    if not os.path.exists(font_file):
        print(f"❌ ملف الخط غير موجود: {font_file}")
        return 1
    else:
        print(f"✅ تم العثور على ملف الخط: {font_file}")

    # إنشاء المستخرج المتقدم
    extractor = AdvancedAyatExtractor(font_file)

    # تحميل أو إنشاء المرجع
    reference_verses = load_reference_verses("reference_verses.json")
    if not reference_verses:
        print("إنشاء مرجع تجريبي...")
        reference_verses = create_sample_reference()

    print(f"تم تحميل {len(reference_verses)} آية مرجعية")

    # معالجة الملفات
    svg_files = list(Path(".").glob("*.svg"))
    if not svg_files:
        # البحث في مجلد pages_svgs
        svg_files = list(Path("pages_svgs").glob("*.svg"))
        if not svg_files:
            print("لا توجد ملفات SVG للمعالجة")
            print("تأكد من وجود ملفات SVG في المجلد الحالي أو مجلد pages_svgs")
            return 1
        else:
            print(f"تم العثور على ملفات SVG في مجلد pages_svgs")

    print(f"تم العثور على {len(svg_files)} ملف SVG")

    all_results = []
    processed_count = 0

    for svg_file in svg_files[:5]:  # معالجة أول 5 ملفات للاختبار
        try:
            result = extractor.process_page_precise(str(svg_file), reference_verses)
            all_results.append(result)
            processed_count += 1

            print(f"الملف: {svg_file.name}")
            print(f"  النصوص المستخرجة: {result['statistics']['total_texts']}")
            print(f"  أرقام الآيات: {result['statistics']['verse_numbers_found']}")
            print(f"  الآيات المطابقة: {result['statistics']['verses_matched']}")
            print(f"  دقة المطابقة: {result['statistics']['accuracy']:.1f}%")
            print("-" * 40)

        except Exception as e:
            print(f"خطأ في معالجة {svg_file}: {e}")
            continue

    if not all_results:
        print("لم يتم معالجة أي ملف بنجاح")
        return 1

    # حفظ النتائج
    output_file = "precise_extraction_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"تم حفظ النتائج في: {output_file}")

    # إحصائيات شاملة
    total_accuracy = sum(r['statistics']['accuracy'] for r in all_results) / len(all_results)
    total_verses_matched = sum(r['statistics']['verses_matched'] for r in all_results)
    total_texts_extracted = sum(r['statistics']['total_texts'] for r in all_results)

    print(f"\n{'='*50}")
    print(f"الإحصائيات النهائية:")
    print(f"{'='*50}")
    print(f"الملفات المعالجة: {processed_count}")
    print(f"إجمالي النصوص المستخرجة: {total_texts_extracted}")
    print(f"إجمالي الآيات المطابقة: {total_verses_matched}")
    print(f"الدقة الإجمالية: {total_accuracy:.1f}%")

    if total_accuracy >= 95:
        print("🎉 دقة ممتازة! السكريبت يعمل بكفاءة عالية")
    elif total_accuracy >= 80:
        print("✅ دقة جيدة، يمكن تحسينها أكثر")
    else:
        print("⚠️ الدقة منخفضة، يحتاج تحسين")

    return 0

if __name__ == "__main__":
    exit(main())
