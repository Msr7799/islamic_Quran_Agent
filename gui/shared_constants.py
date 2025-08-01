#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف الثوابت المشتركة المحسن لمشروع مساعد القرآن الكريم الذكي
يحتوي على الثوابت الأساسية والمسارات المستخدمة فعلياً في المشروع
تم تنظيفه من التكرارات وتحديث المسارات للهيكل الجديد
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional

# معلومات التطبيق المحدثة
APP_INFO = {
    'name': 'مساعد القرآن الكريم الذكي',
    'version': '3.0.0',
    'author': 'فريق التطوير',
    'description': 'نظام متكامل لتحليل ومعالجة النصوص القرآنية مع الذكاء الاصطناعي',
    'copyright': '© 2025 جميع الحقوق محفوظة',
    'website': 'قريباً',
    'build_date': '2025-01-01',
    'license': 'MIT'
}

# المسارات الأساسية
PROJECT_ROOT = Path(__file__).parent.parent  # الجذر الرئيسي للمشروع
GUI_ROOT = Path(__file__).parent  # مجلد الواجهة

# المجلدات الجديدة المنظمة
GUI_DATA_DIR = PROJECT_ROOT / "GUI_DATA"  # بيانات الواجهة
TESTS_DIR = PROJECT_ROOT / "tests"  # ملفات الاختبار
DOCS_DIR = PROJECT_ROOT / "docs"  # التوثيق والملفات النصية

# المجلدات الموجودة
DATA_DIR = PROJECT_ROOT / "Uthmanic_data"
FONT_DIR = PROJECT_ROOT / "Uthmanic_font"
CACHE_DIR = GUI_DATA_DIR / "cache"
LOGS_DIR = GUI_DATA_DIR / "logs"
REPORTS_DIR = GUI_DATA_DIR / "reports"
EXPORTS_DIR = GUI_DATA_DIR / "exports"
TEMP_DIR = GUI_DATA_DIR / "temp"

# أسماء الملفات الافتراضية مع المسارات الجديدة
DEFAULT_FILES = {
    'hafs_csv': DATA_DIR / 'hafs_smart.csv',
    'font_ttf': FONT_DIR / 'uthmanic_hafs_Font.ttf',
    'font_mapping': FONT_DIR / 'uthmani_font_mapping.json',
    'config': GUI_DATA_DIR / 'config.json',
    'env': GUI_DATA_DIR / '.env',
    'gui_settings': GUI_DATA_DIR / 'gui_settings.json',  # في GUI_DATA
    'project_check_results': TESTS_DIR / 'project_check_results.json',  # في tests
}

# ملاحظة: تم نقل إعدادات الألوان والخطوط إلى ui_settings.py لتجنب التكرار
# يمكن الوصول إليها من خلال استيراد ui_settings

# أنماط النصوص القرآنية
QURAN_PATTERNS = {
    # أرقام الآيات
    'verse_number': r'[﴾﴿]\s*(?:\d+|[٠-٩]+)\s*[﴾﴿]',
    'verse_marker': r'[﴾﴿]',
    
    # البسملة
    'basmala': r'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
    'basmala_short': r'بسم الله الرحمن الرحيم',
    
    # علامات الوقف
    'waqf_marks': r'[ۛۚۖۗۘۙ]',
    'sajda_mark': r'۩',
    
    # التشكيل
    'tashkeel': r'[\u064B-\u0652\u0670\u0640]',
    'harakat': r'[\u064B-\u0650\u0652]',
    
    # الأرقام
    'arabic_numbers': r'[٠-٩]+',
    'english_numbers': r'\d+',
    
    # أسماء السور
    'sura_prefix': r'سورة\s+',
    'sura_name': r'سورة\s+(\w+)',
    
    # المراجع
    'aya_reference': r'(\d+):(\d+)',
    'sura_aya_reference': r'سورة\s+(\w+)\s+آية\s+(\d+)'
}

# رموز القرآن الخاصة
QURAN_SYMBOLS = {
    'verse_start': '﴿',
    'verse_end': '﴾',
    'sajda': '۩',
    'waqf_lazim': 'ۘ',
    'waqf_mutlaq': 'ۙ',
    'waqf_jaiz': 'ۚ',
    'waqf_mujawwaz': 'ۛ',
    'waqf_mamnu': 'ۖ',
    'waqf_sakt': 'ۜ',
    'ruku': '۝'
}

# نطاقات يونيكود للأحرف العربية
UNICODE_RANGES = {
    'arabic_letters': (0x0621, 0x064A),
    'arabic_supplement': (0x0671, 0x06DC),
    'arabic_extended': (0x06DE, 0x06FF),
    'arabic_presentation_a': (0xFB50, 0xFDFF),
    'arabic_presentation_b': (0xFE70, 0xFEFF),
    'tashkeel': (0x064B, 0x0652),
    'arabic_numbers': (0x0660, 0x0669),
    'quranic_symbols': (0x06D0, 0x06ED)
}

# إعدادات النماذج المحدثة
MODEL_CONFIGS = {
    'groq': {
        'default_model': 'llama-3.3-70b-versatile',  # النموذج الحالي المستخدم
        'alternative_models': [
            'llama3-70b-8192',
            'llama3-8b-8192', 
            'llama-3.1-8b-instant'
        ],
        'temperature': 0.7,
        'max_tokens': 4096,
        'top_p': 0.9,
        'timeout': 30
    },
    'tavily': {
        'search_depth': 'basic',
        'max_results': 5,
        'include_answer': True,
        'include_raw_content': False
    }
}

# إعدادات البحث
SEARCH_CONFIG = {
    'max_results': 10,
    'search_timeout': 10,
    'window': {
        'default_width': 1200,
        'default_height': 800,
        'min_width': 800,
        'min_height': 600
    },
    'performance': {
        'max_concurrent_requests': 3,
        'request_timeout': 30,
        'cache_size_mb': 100,
        'max_file_size_mb': 50
    },
    'features': {
        'auto_save': True,
        'auto_backup': True,
        'debug_mode': False
    }
}

# إعدادات التطبيق العامة
APP_CONFIG = {
    'debug_mode': False,
    'auto_save': True,
    'theme': 'dark',
    'font_size': 18,
    'font_family': 'default',
    'language': 'ar',
    'window_settings': {
        'default_width': 1200,
        'default_height': 800,
        'min_width': 800,
        'min_height': 600
    }
}

# رسائل النظام
SYSTEM_MESSAGES = {
    'welcome': 'مرحباً! أنا مساعدك الذكي للقرآن الكريم. كيف يمكنني مساعدتك اليوم؟',
    'loading': 'جاري التحميل...',
    'processing': 'جاري المعالجة...',
    'error': 'حدث خطأ. الرجاء المحاولة مرة أخرى.',
    'no_results': 'لم يتم العثور على نتائج.',
    'connection_error': 'خطأ في الاتصال. تحقق من اتصالك بالإنترنت.',
    'api_error': 'خطأ في الخدمة. الرجاء المحاولة لاحقاً.',
    'session_expired': 'انتهت صلاحية الجلسة. الرجاء إعادة تسجيل الدخول.',
    'rate_limit': 'تم تجاوز حد الاستخدام. الرجاء الانتظار قليلاً.',
    'invalid_input': 'الرجاء إدخال بيانات صحيحة.',
    'feature_unavailable': 'هذه الميزة غير متاحة حالياً.',
    # الثوابت المضافة لحل مشاكل SonarLint
    'warning_title': 'تنبيه',
    'no_file_selected': 'لم يتم تحديد ملف',
    'compare_texts_title': 'مقارنة النصوص',
    'char_type_label': 'النوع',
    'arabic_char_type': 'حرف عربي'
}

# قوائم الأخطاء الشائعة
COMMON_ERRORS = {
    'E001': 'مفتاح API غير صحيح',
    'E002': 'انتهت صلاحية مفتاح API',
    'E003': 'تجاوز حد الاستخدام',
    'E004': 'خطأ في الشبكة',
    'E005': 'ملف غير موجود',
    'E006': 'صيغة ملف غير مدعومة',
    'E007': 'ذاكرة غير كافية',
    'E008': 'خطأ في قاعدة البيانات',
    'E009': 'خطأ في التحليل',
    'E010': 'نموذج غير متاح'
}

# أنواع الملفات المدعومة
SUPPORTED_FILE_TYPES = {
    'documents': ['.txt', '.pdf', '.docx', '.rtf'],
    'data': ['.csv', '.json', '.xml', '.xlsx'],
    'images': ['.png', '.jpg', '.jpeg', '.svg'],
    'fonts': ['.ttf', '.otf', '.woff', '.woff2'],
    'config': ['.json', '.yaml', '.yml', '.ini']
}

# حدود النظام
SYSTEM_LIMITS = {
    'max_file_size': 50 * 1024 * 1024,  # 50 MB
    'max_text_length': 1000000,  # حرف
    'max_search_results': 100,
    'max_history_items': 1000,
    'max_cache_age_days': 7,
    'max_concurrent_users': 10,
    'session_timeout_minutes': 30
}

# دوال مساعدة للمسارات والثوابت
def ensure_directory(path: Path) -> Path:
    """التأكد من وجود المجلد وإنشاؤه إذا لم يكن موجوداً"""
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_file_path(file_key: str) -> Optional[Path]:
    """الحصول على مسار ملف من قاموس الملفات الافتراضية"""
    return DEFAULT_FILES.get(file_key)

def get_app_info(key: str) -> str:
    """الحصول على معلومة من معلومات التطبيق"""
    return APP_INFO.get(key, '')

def get_model_config(provider: str, key: str = None):
    """الحصول على إعدادات النموذج"""
    config = MODEL_CONFIGS.get(provider, {})
    if key:
        return config.get(key)
    return config

def get_system_message(key: str) -> str:
    """الحصول على رسالة نظام"""
    return SYSTEM_MESSAGES.get(key, '')

def format_error(error_code: str, details: str = '') -> str:
    """تنسيق رسالة خطأ"""
    error_msg = COMMON_ERRORS.get(error_code, 'خطأ غير معروف')
    if details:
        return f"{error_msg}: {details}"
    return error_msg

def is_arabic_text(text: str) -> bool:
    """التحقق من كون النص عربياً"""
    if not text:
        return False
    arabic_count = sum(1 for c in text if 0x0600 <= ord(c) <= 0x06FF)
    return arabic_count > len(text) * 0.5

# تصدير الثوابت والدوال المحدثة
__all__ = [
    # معلومات التطبيق والمسارات
    'APP_INFO',
    'PROJECT_ROOT',
    'GUI_ROOT',
    'GUI_DATA_DIR',
    'TESTS_DIR',
    'DOCS_DIR',
    'DATA_DIR',
    'FONT_DIR',
    'CACHE_DIR',
    'LOGS_DIR',
    'REPORTS_DIR',
    'EXPORTS_DIR',
    'TEMP_DIR',
    'DEFAULT_FILES',
    
    # الثوابت الأساسية
    'QURAN_PATTERNS',
    'QURAN_SYMBOLS',
    'UNICODE_RANGES',
    'MODEL_CONFIGS',
    'SEARCH_CONFIG',
    'APP_CONFIG',
    'SYSTEM_MESSAGES',
    'COMMON_ERRORS',
    'SUPPORTED_FILE_TYPES',
    'SYSTEM_LIMITS',
    
    # الدوال المساعدة
    'ensure_directory',
    'get_file_path',
    'get_app_info',
    'get_model_config',
    'get_system_message',
    'format_error',
    'is_arabic_text'
]
