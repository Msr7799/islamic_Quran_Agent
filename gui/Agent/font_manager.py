#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدير الخط العثماني المتطور
يوفر إدارة شاملة لملف الخط TTF مع معالجة متقدمة للرموز العثمانية

المميزات:
- تحميل وتحليل ملف الخط TTF مباشرة
- بناء خريطة الأحرف والرموز العثمانية
- معالجة الرموز المركبة والمتداخلة
- حساب معلومات العرض والتخطيط
- تحليل خصائص الخط المتقدمة
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode
import unicodedata
from collections import defaultdict
import pickle
from datetime import datetime

class AdvancedFontManager:
    """مدير الخط العثماني المتطور"""
    
    # نطاقات الرموز العثمانية
    UTHMANI_RANGES = [
        (0x064B, 0x0652),  # تشكيل أساسي
        (0x0653, 0x065F),  # رموز عثمانية خاصة
        (0x0670, 0x0671),  # ألف خنجرية وألف وصل
        (0x06D6, 0x06ED),  # علامات وقف وتجويد
        (0x08D3, 0x08FF),  # رموز عربية ممتدة
        (0xFBB2, 0xFBC1),  # رموز عثمانية في Presentation Forms
    ]
    
    def __init__(self, font_file: str = "UthmanicHafs_v2-0 font/uthmanic_hafs_v20.ttf",
                 cache_dir: str = "font_cache", logger=None):
        """
        تهيئة مدير الخط
        
        Args:
            font_file: مسار ملف الخط TTF
            cache_dir: مجلد التخزين المؤقت
            logger: كائن التسجيل
        """
        self.font_file = Path(font_file)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        
        # تحميل الخط
        self.font = None
        self.character_map = {}
        self.glyph_map = {}
        self.uthmani_symbols = set()
        self.rendering_cache = {}
        
        self._load_font()
        self._build_character_maps()
        self._identify_uthmani_symbols()
        
    def _load_font(self):
        """تحميل ملف الخط"""
        try:
            if not self.font_file.exists():
                raise FileNotFoundError(f"ملف الخط غير موجود: {self.font_file}")
                
            self.font = TTFont(str(self.font_file))
            self.logger.info(f"✅ تم تحميل الخط: {self.font_file.name}")
            
            # معلومات الخط
            font_info = self._extract_font_info()
            self.logger.info(f"📝 معلومات الخط: {font_info['family_name']} - {font_info['version']}")
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحميل الخط: {e}")
            raise
            
    def _extract_font_info(self) -> Dict[str, Any]:
        """استخراج معلومات الخط"""
        info = {
            'family_name': 'Unknown',
            'version': 'Unknown',
            'designer': 'Unknown',
            'description': 'Unknown'
        }
        
        if 'name' in self.font:
            name_table = self.font['name']
            
            # البحث عن المعلومات المختلفة
            for record in name_table.names:
                if record.nameID == 1:  # Family name
                    info['family_name'] = str(record)
                elif record.nameID == 5:  # Version
                    info['version'] = str(record)
                elif record.nameID == 9:  # Designer
                    info['designer'] = str(record)
                elif record.nameID == 10:  # Description
                    info['description'] = str(record)
                    
        return info
        
    def _build_character_maps(self):
        """بناء خرائط الأحرف والرموز"""
        if not self.font:
            return
            
        # الحصول على خريطة Unicode
        cmap = self.font.getBestCmap()
        
        for unicode_val, glyph_name in cmap.items():
            try:
                char = chr(unicode_val)
                
                # معلومات الحرف
                char_info = {
                    'unicode': f'U+{unicode_val:04X}',
                    'glyph_name': glyph_name,
                    'category': unicodedata.category(char),
                    'name': unicodedata.name(char, 'UNNAMED'),
                    'is_arabic': 0x0600 <= unicode_val <= 0x06FF,
                    'is_uthmani': self._is_uthmani_range(unicode_val),
                    'is_diacritic': unicodedata.category(char) in ['Mn', 'Me'],
                    'combining_class': unicodedata.combining(char)
                }
                
                self.character_map[char] = char_info
                self.glyph_map[glyph_name] = char_info
                
            except ValueError:
                # تجاهل القيم غير الصالحة
                continue
                
        self.logger.info(f"🔤 تم بناء خريطة {len(self.character_map)} حرف")
        
    def _is_uthmani_range(self, unicode_val: int) -> bool:
        """فحص إذا كان الحرف في نطاق الرموز العثمانية"""
        return any(start <= unicode_val <= end for start, end in self.UTHMANI_RANGES)
        
    def _identify_uthmani_symbols(self):
        """تحديد الرموز العثمانية"""
        for char, info in self.character_map.items():
            if info['is_uthmani'] or info['is_diacritic']:
                self.uthmani_symbols.add(char)
                
        self.logger.info(f"🕌 تم تحديد {len(self.uthmani_symbols)} رمز عثماني")
        
    def is_uthmani_symbol(self, char: str) -> bool:
        """فحص إذا كان الحرف رمز عثماني"""
        return char in self.uthmani_symbols
        
    def get_character_info(self, char: str) -> Dict[str, Any]:
        """الحصول على معلومات حرف"""
        return self.character_map.get(char, {})
        
    def get_glyph_info(self, glyph_name: str) -> Dict[str, Any]:
        """الحصول على معلومات glyph"""
        return self.glyph_map.get(glyph_name, {})
        
    def analyze_text_composition(self, text: str) -> Dict[str, Any]:
        """تحليل تركيب النص"""
        analysis = {
            'total_chars': len(text),
            'arabic_chars': 0,
            'uthmani_symbols': 0,
            'diacritics': 0,
            'letters': 0,
            'spaces': 0,
            'unknown_chars': 0,
            'character_breakdown': defaultdict(int),
            'symbol_details': []
        }
        
        for char in text:
            char_info = self.get_character_info(char)
            
            if char == ' ':
                analysis['spaces'] += 1
            elif char_info:
                if char_info['is_arabic']:
                    analysis['arabic_chars'] += 1
                if char_info['is_uthmani']:
                    analysis['uthmani_symbols'] += 1
                    analysis['symbol_details'].append({
                        'char': char,
                        'name': char_info['name'],
                        'unicode': char_info['unicode']
                    })
                if char_info['is_diacritic']:
                    analysis['diacritics'] += 1
                if char_info['category'].startswith('L'):  # Letter categories
                    analysis['letters'] += 1
                    
                analysis['character_breakdown'][char_info['category']] += 1
            else:
                analysis['unknown_chars'] += 1
                
        return analysis
        
    def get_rendering_info(self, text: str) -> Dict[str, Any]:
        """الحصول على معلومات العرض للنص"""
        cache_key = hash(text)
        
        if cache_key in self.rendering_cache:
            return self.rendering_cache[cache_key]
            
        # تقدير معلومات العرض
        info = {
            'estimated_width': len(text) * 12,  # تقدير بسيط
            'estimated_height': 20,
            'character_count': len(text),
            'complexity_score': self._calculate_complexity(text),
            'has_complex_shapes': self._has_complex_shapes(text)
        }
        
        self.rendering_cache[cache_key] = info
        return info
        
    def _calculate_complexity(self, text: str) -> float:
        """حساب درجة تعقيد النص"""
        complexity = 0.0
        
        for char in text:
            char_info = self.get_character_info(char)
            if char_info:
                # الرموز العثمانية أكثر تعقيداً
                if char_info['is_uthmani']:
                    complexity += 2.0
                elif char_info['is_diacritic']:
                    complexity += 1.5
                elif char_info['is_arabic']:
                    complexity += 1.0
                else:
                    complexity += 0.5
                    
        return complexity / len(text) if text else 0.0
        
    def _has_complex_shapes(self, text: str) -> bool:
        """فحص وجود أشكال معقدة في النص"""
        complex_chars = {'ﷲ', '﷽', 'ﷺ', 'ﷻ'}  # أمثلة على أشكال معقدة
        return any(char in complex_chars for char in text)
        
    def export_font_analysis(self, output_file: str):
        """تصدير تحليل الخط"""
        analysis = {
            'metadata': {
                'font_file': str(self.font_file),
                'generated_at': datetime.now().isoformat(),
                'total_characters': len(self.character_map),
                'uthmani_symbols': len(self.uthmani_symbols)
            },
            'character_map': {
                char: info for char, info in self.character_map.items()
                if info['is_arabic'] or info['is_uthmani']
            },
            'uthmani_symbols': list(self.uthmani_symbols),
            'font_info': self._extract_font_info()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"📊 تم تصدير تحليل الخط إلى: {output_file}")
        
    def save_cache(self):
        """حفظ التخزين المؤقت"""
        cache_file = self.cache_dir / "font_cache.pkl"
        
        cache_data = {
            'character_map': self.character_map,
            'glyph_map': self.glyph_map,
            'uthmani_symbols': self.uthmani_symbols,
            'rendering_cache': self.rendering_cache
        }
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            self.logger.debug("💾 تم حفظ التخزين المؤقت")
        except Exception as e:
            self.logger.error(f"خطأ في حفظ التخزين المؤقت: {e}")
            
    def load_cache(self) -> bool:
        """تحميل التخزين المؤقت"""
        cache_file = self.cache_dir / "font_cache.pkl"
        
        if not cache_file.exists():
            return False
            
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                
            self.character_map = cache_data.get('character_map', {})
            self.glyph_map = cache_data.get('glyph_map', {})
            self.uthmani_symbols = cache_data.get('uthmani_symbols', set())
            self.rendering_cache = cache_data.get('rendering_cache', {})
            
            self.logger.debug("📂 تم تحميل التخزين المؤقت")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في تحميل التخزين المؤقت: {e}")
            return False

# للاستخدام المباشر
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python font_manager.py <font_file.ttf>")
        sys.exit(1)
        
    font_file = sys.argv[1]
    
    # إنشاء مدير الخط
    manager = AdvancedFontManager(font_file)
    
    # تصدير التحليل
    output_file = Path(font_file).stem + "_analysis.json"
    manager.export_font_analysis(output_file)
    
    print(f"✅ تم تحليل الخط وحفظ النتائج في: {output_file}")
