#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
حزمة بيانات المصحف العثماني - رواية حفص
تحتوي على جميع البيانات المرجعية للقرآن الكريم
"""

import os
from pathlib import Path

# المسار الأساسي للبيانات
DATA_DIR = Path(__file__).parent

# مسارات الملفات
HAFS_CSV = DATA_DIR / "hafs_smart.csv"
HAFS_JSON = DATA_DIR / "hafs_smart.json"
HAFS_XML = DATA_DIR / "hafs_smart.xml"
HAFS_HTML = DATA_DIR / "hafs_smart.html"
HAFS_TXT = DATA_DIR / "hafs_smart.txt"
HAFS_XLSX = DATA_DIR / "hafs_smart.xlsx"
HAFS_SQL = DATA_DIR / "hafs_smart.sql"
SYMBOLS_DOC = DATA_DIR / "رموز_الضبط والتشكيل.md"

def get_hafs_data_path(format='csv'):
    """
    الحصول على مسار ملف البيانات بالصيغة المطلوبة
    
    Args:
        format: صيغة الملف ('csv', 'json', 'xml', 'html', 'txt', 'xlsx', 'sql')
        
    Returns:
        مسار الملف إذا كان موجوداً، None إذا لم يكن موجوداً
    """
    paths = {
        'csv': HAFS_CSV,
        'json': HAFS_JSON,
        'xml': HAFS_XML,
        'html': HAFS_HTML,
        'txt': HAFS_TXT,
        'xlsx': HAFS_XLSX,
        'sql': HAFS_SQL
    }
    
    file_path = paths.get(format.lower())
    if file_path and file_path.exists():
        return str(file_path)
    return None

def load_hafs_data(format='csv'):
    """
    تحميل بيانات حفص بالصيغة المطلوبة
    
    Args:
        format: صيغة الملف المطلوب تحميله
        
    Returns:
        البيانات المحملة أو None في حالة الفشل
    """
    file_path = get_hafs_data_path(format)
    if not file_path:
        raise FileNotFoundError(f"ملف البيانات بصيغة {format} غير موجود")
    
    if format == 'csv':
        import pandas as pd
        return pd.read_csv(file_path)
    elif format == 'json':
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif format == 'xml':
        import xml.etree.ElementTree as ET
        return ET.parse(file_path)
    elif format == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif format == 'xlsx':
        import pandas as pd
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"صيغة غير مدعومة: {format}")

# تصدير المسارات والدوال الأساسية
__all__ = [
    'DATA_DIR',
    'HAFS_CSV',
    'HAFS_JSON',
    'HAFS_XML',
    'HAFS_HTML',
    'HAFS_TXT',
    'HAFS_XLSX',
    'HAFS_SQL',
    'SYMBOLS_DOC',
    'get_hafs_data_path',
    'load_hafs_data'
]
