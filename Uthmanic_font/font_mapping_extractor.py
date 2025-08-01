#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مستخرج جدول الخط العثماني
يقوم بقراءة ملف الخط العثماني واستخراج جدول الأحرف والرموز
لإنشاء مرجع دقيق للمطابقة
"""

import json
import os
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
    from fontTools.unicode import Unicode
    FONTTOOLS_AVAILABLE = True
except ImportError:
    FONTTOOLS_AVAILABLE = False
    print("تحذير: مكتبة fontTools غير متوفرة. سيتم إنشاء جدول أساسي.")

def extract_font_character_map(font_path):
    """استخراج جدول الأحرف من ملف الخط"""
    if not FONTTOOLS_AVAILABLE:
        return create_basic_uthmani_mapping()
    
    try:
        font = TTFont(font_path)
        cmap = font.getBestCmap()
        
        character_map = {}
        for unicode_value, glyph_name in cmap.items():
            try:
                char = chr(unicode_value)
                character_map[char] = {
                    'unicode': f'U+{unicode_value:04X}',
                    'unicode_value': unicode_value,
                    'glyph_name': glyph_name,
                    'char': char
                }
            except ValueError:
                # تجاهل القيم غير الصالحة
                continue
        
        return character_map
        
    except Exception as e:
        print(f"خطأ في قراءة الخط: {e}")
        return create_basic_uthmani_mapping()

def create_basic_uthmani_mapping():
    """إنشاء جدول أساسي للأحرف العثمانية"""
    
    # الأحرف العربية الأساسية مع أشكالها المختلفة
    basic_mapping = {}
    
    # الأحرف العربية الأساسية
    arabic_letters = {
        # الألف وأشكالها
        'ا': ['ا', 'أ', 'إ', 'آ', 'ٱ', 'ﺍ', 'ﺎ'],
        'ب': ['ب', 'ﺏ', 'ﺐ', 'ﺑ', 'ﺒ'],
        'ت': ['ت', 'ﺕ', 'ﺖ', 'ﺗ', 'ﺘ'],
        'ث': ['ث', 'ﺙ', 'ﺚ', 'ﺛ', 'ﺜ'],
        'ج': ['ج', 'ﺝ', 'ﺞ', 'ﺟ', 'ﺠ'],
        'ح': ['ح', 'ﺡ', 'ﺢ', 'ﺣ', 'ﺤ'],
        'خ': ['خ', 'ﺥ', 'ﺦ', 'ﺧ', 'ﺨ'],
        'د': ['د', 'ﺩ', 'ﺪ'],
        'ذ': ['ذ', 'ﺫ', 'ﺬ'],
        'ر': ['ر', 'ﺭ', 'ﺮ'],
        'ز': ['ز', 'ﺯ', 'ﺰ'],
        'س': ['س', 'ﺱ', 'ﺲ', 'ﺳ', 'ﺴ'],
        'ش': ['ش', 'ﺵ', 'ﺶ', 'ﺷ', 'ﺸ'],
        'ص': ['ص', 'ﺹ', 'ﺺ', 'ﺻ', 'ﺼ'],
        'ض': ['ض', 'ﺽ', 'ﺾ', 'ﺿ', 'ﻀ'],
        'ط': ['ط', 'ﻁ', 'ﻂ', 'ﻃ', 'ﻄ'],
        'ظ': ['ظ', 'ﻅ', 'ﻆ', 'ﻇ', 'ﻈ'],
        'ع': ['ع', 'ﻉ', 'ﻊ', 'ﻋ', 'ﻌ'],
        'غ': ['غ', 'ﻍ', 'ﻎ', 'ﻏ', 'ﻐ'],
        'ف': ['ف', 'ﻑ', 'ﻒ', 'ﻓ', 'ﻔ'],
        'ق': ['ق', 'ﻕ', 'ﻖ', 'ﻗ', 'ﻘ'],
        'ك': ['ك', 'ﻙ', 'ﻚ', 'ﻛ', 'ﻜ'],
        'ل': ['ل', 'ﻝ', 'ﻞ', 'ﻟ', 'ﻠ'],
        'م': ['م', 'ﻡ', 'ﻢ', 'ﻣ', 'ﻤ'],
        'ن': ['ن', 'ﻥ', 'ﻦ', 'ﻧ', 'ﻨ'],
        'ه': ['ه', 'ﻩ', 'ﻪ', 'ﻫ', 'ﻬ', 'ة', 'ﺓ', 'ﺔ'],
        'و': ['و', 'ﻭ', 'ﻮ', 'ؤ'],
        'ي': ['ي', 'ﻱ', 'ﻲ', 'ﻳ', 'ﻴ', 'ى', 'ﻯ', 'ﻰ', 'ئ'],
        'لا': ['لا', 'ﻻ', 'ﻼ']
    }
    
    # إنشاء الجدول
    for base_char, variants in arabic_letters.items():
        for variant in variants:
            try:
                unicode_value = ord(variant)
                basic_mapping[variant] = {
                    'unicode': f'U+{unicode_value:04X}',
                    'unicode_value': unicode_value,
                    'base_char': base_char,
                    'char': variant,
                    'is_variant': variant != base_char
                }
            except:
                continue
    
    # إضافة الرموز العثمانية
    uthmani_symbols = {
        # التشكيل
        'َ': 'فتحة', 'ً': 'تنوين فتح', 'ُ': 'ضمة', 'ٌ': 'تنوين ضم',
        'ِ': 'كسرة', 'ٍ': 'تنوين كسر', 'ْ': 'سكون', 'ّ': 'شدة',
        'ٰ': 'ألف خنجرية', 'ٓ': 'مد', 'ٔ': 'همزة فوق', 'ٕ': 'همزة تحت',
        
        # علامات الوقف
        'ۖ': 'وقف صلى', 'ۗ': 'وقف قل', 'ۘ': 'وقف قلي', 'ۙ': 'وقف قلى',
        'ۚ': 'وقف ميم', 'ۛ': 'وقف جيم', 'ۜ': 'وقف خفيف', '۝': 'نهاية آية',
        '۞': 'زخرفة', '۩': 'سجدة',
        
        # الأرقام العربية
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    
    for symbol, name in uthmani_symbols.items():
        try:
            unicode_value = ord(symbol)
            basic_mapping[symbol] = {
                'unicode': f'U+{unicode_value:04X}',
                'unicode_value': unicode_value,
                'name': name,
                'char': symbol,
                'is_symbol': True
            }
        except:
            continue
    
    return basic_mapping

def create_reverse_mapping(character_map):
    """إنشاء جدول عكسي للبحث السريع"""
    reverse_map = {}
    
    for char, info in character_map.items():
        base_char = info.get('base_char', char)
        if base_char not in reverse_map:
            reverse_map[base_char] = []
        reverse_map[base_char].append(char)
    
    return reverse_map

def create_normalization_rules(character_map):
    """إنشاء قواعد التطبيع للمطابقة الدقيقة"""
    normalization_rules = {}
    
    for char, info in character_map.items():
        if 'base_char' in info:
            normalization_rules[char] = info['base_char']
        else:
            normalization_rules[char] = char
    
    return normalization_rules

def save_font_mapping_to_json(character_map, output_file="uthmani_font_mapping.json"):
    """حفظ جدول الخط في ملف JSON"""
    
    # إنشاء البيانات الشاملة
    font_data = {
        'metadata': {
            'description': 'جدول الخط العثماني للمطابقة الدقيقة',
            'total_characters': len(character_map),
            'version': '1.0'
        },
        'character_map': character_map,
        'reverse_mapping': create_reverse_mapping(character_map),
        'normalization_rules': create_normalization_rules(character_map)
    }
    
    # حفظ الملف
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(font_data, f, ensure_ascii=False, indent=2)
    
    print(f"تم حفظ جدول الخط في: {output_file}")
    print(f"عدد الأحرف: {len(character_map)}")
    
    return font_data

def main():
    """الوظيفة الرئيسية"""
    print("مستخرج جدول الخط العثماني")
    print("=" * 40)
    
    # البحث عن ملف الخط العثماني
    font_paths = [
        "UthmanicHafs.ttf",
        "fonts/UthmanicHafs.ttf",
        "UthmanicHafs_v2-0.ttf",
        "fonts/UthmanicHafs_v2-0.ttf",
        "UthmanicHafs_v2-0 font/uthmanic_hafs_v20.ttf",
        "uthmanic_hafs_v20.ttf"
    ]
    
    font_path = None
    for path in font_paths:
        if os.path.exists(path):
            font_path = path
            break
    
    if font_path and FONTTOOLS_AVAILABLE:
        print(f"تم العثور على ملف الخط: {font_path}")
        character_map = extract_font_character_map(font_path)
    else:
        print("لم يتم العثور على ملف الخط، سيتم إنشاء جدول أساسي")
        character_map = create_basic_uthmani_mapping()
    
    # حفظ الجدول
    font_data = save_font_mapping_to_json(character_map)
    
    # عرض إحصائيات
    print(f"\nإحصائيات الجدول:")
    print(f"إجمالي الأحرف: {len(character_map)}")
    
    # عرض عينة من الأحرف
    print(f"\nعينة من الأحرف:")
    for i, (char, info) in enumerate(list(character_map.items())[:10]):
        name = info.get('name', info.get('base_char', 'غير محدد'))
        print(f"  {char} ({info['unicode']}) - {name}")
    
    return 0

if __name__ == "__main__":
    exit(main())
