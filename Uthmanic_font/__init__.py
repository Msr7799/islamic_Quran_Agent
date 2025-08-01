#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
حزمة خطوط المصحف العثماني
تحتوي على الخط العثماني وأدوات معالجته
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional

# المسار الأساسي للخطوط
FONT_DIR = Path(__file__).parent

# مسارات الملفات
FONT_TTF = FONT_DIR / "uthmanic_hafs_Font.ttf"
FONT_MAPPING = FONT_DIR / "uthmani_font_mapping.json"
FONT_PDF = FONT_DIR / "HafsSmart.pdf"
FONT_DOCX = FONT_DIR / "HafsSmart.docx"
FONT_OBJECTS = FONT_DIR / "UthmanicHafs_v2-0 font_OBJCS.png"
FONT_EXTRACTOR = FONT_DIR / "font_mapping_extractor.py"

def get_font_path() -> Optional[str]:
    """
    الحصول على مسار ملف الخط العثماني
    
    Returns:
        مسار ملف الخط إذا كان موجوداً، None إذا لم يكن موجوداً
    """
    if FONT_TTF.exists():
        return str(FONT_TTF)
    return None

def load_font_mapping() -> Dict:
    """
    تحميل خريطة رموز الخط العثماني
    
    Returns:
        قاموس يحتوي على خريطة الرموز
    """
    if not FONT_MAPPING.exists():
        raise FileNotFoundError("ملف خريطة الخط غير موجود")
    
    with open(FONT_MAPPING, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_font_info() -> Dict[str, any]:
    """
    الحصول على معلومات الخط العثماني
    
    Returns:
        قاموس يحتوي على معلومات الخط
    """
    info = {
        'name': 'UthmanicHafs v2.0',
        'version': '2.0',
        'type': 'TrueType Font',
        'encoding': 'Unicode',
        'description': 'خط المصحف العثماني برواية حفص',
        'files': {}
    }
    
    # فحص الملفات الموجودة
    files_to_check = {
        'font': FONT_TTF,
        'mapping': FONT_MAPPING,
        'pdf': FONT_PDF,
        'docx': FONT_DOCX,
        'objects': FONT_OBJECTS
    }
    
    for key, path in files_to_check.items():
        if path.exists():
            info['files'][key] = {
                'path': str(path),
                'size': path.stat().st_size,
                'exists': True
            }
        else:
            info['files'][key] = {
                'path': str(path),
                'exists': False
            }
    
    return info

def validate_font_setup() -> bool:
    """
    التحقق من صحة إعداد الخط
    
    Returns:
        True إذا كان الإعداد صحيحاً، False إذا كان هناك مشكلة
    """
    required_files = [FONT_TTF, FONT_MAPPING]
    return all(f.exists() for f in required_files)

class FontManager:
    """
    مدير الخط العثماني - واجهة مبسطة لاستخدام الخط
    """
    
    def __init__(self):
        self.font_path = get_font_path()
        self.mapping = None
        
        if not self.font_path:
            raise FileNotFoundError("ملف الخط العثماني غير موجود")
        
        try:
            self.mapping = load_font_mapping()
        except FileNotFoundError:
            print("تحذير: لم يتم تحميل خريطة الخط")
    
    def get_glyph_for_char(self, char: str) -> Optional[str]:
        """
        الحصول على الرمز المناسب للحرف
        
        Args:
            char: الحرف المطلوب
            
        Returns:
            الرمز المناسب أو None
        """
        if self.mapping and char in self.mapping:
            return self.mapping[char]
        return char
    
    def is_uthmani_char(self, char: str) -> bool:
        """
        التحقق من كون الحرف من الرموز العثمانية
        
        Args:
            char: الحرف المطلوب فحصه
            
        Returns:
            True إذا كان رمزاً عثمانياً
        """
        if not self.mapping:
            return False
        return char in self.mapping

# تصدير المسارات والدوال الأساسية
__all__ = [
    'FONT_DIR',
    'FONT_TTF',
    'FONT_MAPPING',
    'FONT_PDF',
    'FONT_DOCX',
    'FONT_OBJECTS',
    'get_font_path',
    'load_font_mapping',
    'get_font_info',
    'validate_font_setup',
    'FontManager'
]
