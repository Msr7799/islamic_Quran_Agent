#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
استخراج النصوص من ملفات SVG باستخدام OCR
"""

import os
import json
import subprocess
from pathlib import Path
from PIL import Image
import pytesseract

class SVGToTextOCR:
    """مستخرج النصوص من SVG باستخدام OCR"""
    
    def __init__(self):
        # إعداد tesseract للعربية
        self.tesseract_config = '--oem 3 --psm 6 -l ara'
        
    def svg_to_png(self, svg_file, png_file, dpi=300):
        """تحويل SVG إلى PNG"""
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
            
            if result.returncode == 0:
                return True
            else:
                print(f"خطأ في تحويل SVG: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"خطأ في تحويل SVG إلى PNG: {e}")
            return False
    
    def extract_text_from_image(self, image_path):
        """استخراج النص من الصورة باستخدام OCR"""
        try:
            # فتح الصورة
            image = Image.open(image_path)
            
            # تحسين الصورة للـ OCR
            image = image.convert('RGB')
            
            # استخراج النص
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            
            return text.strip()
            
        except Exception as e:
            print(f"خطأ في استخراج النص من الصورة: {e}")
            return ""
    
    def get_text_with_coordinates(self, image_path):
        """استخراج النص مع الإحداثيات"""
        try:
            image = Image.open(image_path)
            image = image.convert('RGB')
            
            # استخراج النص مع الإحداثيات
            data = pytesseract.image_to_data(image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)
            
            texts = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text:  # تجاهل النصوص الفارغة
                    texts.append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': data['conf'][i]
                    })
            
            return texts
            
        except Exception as e:
            print(f"خطأ في استخراج النص مع الإحداثيات: {e}")
            return []
    
    def process_svg_file(self, svg_file):
        """معالجة ملف SVG واحد"""
        print(f"معالجة الملف: {svg_file}")
        
        # إنشاء ملف PNG مؤقت
        png_file = svg_file.with_suffix('.png')
        
        try:
            # تحويل SVG إلى PNG
            if not self.svg_to_png(svg_file, png_file):
                return None
            
            # استخراج النص مع الإحداثيات
            texts = self.get_text_with_coordinates(png_file)
            
            print(f"  تم استخراج {len(texts)} نص")
            
            # حذف الملف المؤقت
            if png_file.exists():
                png_file.unlink()
            
            return {
                'file': str(svg_file),
                'texts': texts,
                'total_texts': len(texts)
            }
            
        except Exception as e:
            print(f"خطأ في معالجة {svg_file}: {e}")
            # حذف الملف المؤقت في حالة الخطأ
            if png_file.exists():
                png_file.unlink()
            return None
    
    def find_verse_numbers(self, texts):
        """البحث عن أرقام الآيات في النصوص"""
        import re
        
        verse_numbers = []
        arabic_digits = '٠١٢٣٤٥٦٧٨٩'
        
        for text_info in texts:
            text = text_info['text']
            
            # البحث عن الأرقام العربية
            arabic_matches = re.findall(f'[{arabic_digits}]+', text)
            for match in arabic_matches:
                # تحويل إلى إنجليزي
                english_num = ""
                for char in match:
                    if char in arabic_digits:
                        english_num += str(arabic_digits.index(char))
                
                if english_num.isdigit():
                    verse_numbers.append({
                        'number': int(english_num),
                        'arabic_text': match,
                        'full_text': text,
                        'x': text_info['x'],
                        'y': text_info['y'],
                        'confidence': text_info['confidence']
                    })
            
            # البحث عن الأرقام الإنجليزية
            english_matches = re.findall(r'\d+', text)
            for match in english_matches:
                verse_numbers.append({
                    'number': int(match),
                    'arabic_text': match,
                    'full_text': text,
                    'x': text_info['x'],
                    'y': text_info['y'],
                    'confidence': text_info['confidence']
                })
        
        return verse_numbers

def check_dependencies():
    """فحص المتطلبات"""
    print("فحص المتطلبات...")
    
    # فحص inkscape
    try:
        result = subprocess.run(['inkscape', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Inkscape متوفر")
        else:
            print("❌ Inkscape غير متوفر")
            return False
    except:
        print("❌ Inkscape غير مثبت")
        return False
    
    # فحص tesseract
    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract متوفر")
        else:
            print("❌ Tesseract غير متوفر")
            return False
    except:
        print("❌ Tesseract غير مثبت")
        return False
    
    return True

def main():
    """الوظيفة الرئيسية"""
    print("مستخرج النصوص من SVG باستخدام OCR")
    print("=" * 50)
    
    # فحص المتطلبات
    if not check_dependencies():
        print("\nيرجى تثبيت المتطلبات:")
        print("sudo apt install inkscape tesseract-ocr tesseract-ocr-ara")
        return 1
    
    # إنشاء المستخرج
    extractor = SVGToTextOCR()
    
    # اختبار صفحة واحدة
    svg_file = Path("pages_svgs/page_001.svg")
    
    if not svg_file.exists():
        print(f"الملف غير موجود: {svg_file}")
        return 1
    
    # معالجة الملف
    result = extractor.process_svg_file(svg_file)
    
    if result:
        # البحث عن أرقام الآيات
        verse_numbers = extractor.find_verse_numbers(result['texts'])
        result['verse_numbers'] = verse_numbers
        
        print(f"تم العثور على {len(verse_numbers)} رقم آية")
        
        # حفظ النتائج
        output_file = "ocr_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"تم حفظ النتائج في: {output_file}")
        
        # عرض عينة من النتائج
        print(f"\nعينة من النصوص المستخرجة:")
        for i, text_info in enumerate(result['texts'][:10]):
            print(f"  {i+1}. '{text_info['text']}' (ثقة: {text_info['confidence']})")
        
        if verse_numbers:
            print(f"\nأرقام الآيات:")
            for num_info in verse_numbers[:5]:
                print(f"  {num_info['number']} - '{num_info['full_text']}'")
    
    return 0

if __name__ == "__main__":
    exit(main())
