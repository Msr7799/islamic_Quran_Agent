#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محلل النصوص القرآنية المتقدم
Advanced Quran Text Analyzer

تطبيق متقدم لتحليل النصوص القرآنية والعربية مع واجهة مستخدم احترافية
ومكونات ذكية للبحث والتحليل والمقارنة.

الإصدار: 2.0
المطور: فريق تطوير محلل النصوص القرآنية
"""

__version__ = "2.0.0"
__author__ = "Quran Text Analyzer Team"
__description__ = "محلل النصوص القرآنية المتقدم مع واجهة PyQt5 احترافية"

# الاستيرادات الأساسية
try:
    from .shared_imports import *
    from .data_models import AyahInfo, TextAnalysisResult, SimpleTextProcessor
    from .analysis_widgets import CharacterAnalysisWidget, StatisticsWidget
    from .svg_comparison_tools import SVGAnalyzerWidget, ComparisonWidget
    from .complete_chat_window import ProfessionalChatWindow
    from .main_window import QuranTextAnalyzer
    
    # قائمة المكونات المتاحة للاستيراد
    __all__ = [
        'AyahInfo',
        'TextAnalysisResult', 
        'SimpleTextProcessor',
        'CharacterAnalysisWidget',
        'StatisticsWidget',
        'SVGAnalyzerWidget',
        'ComparisonWidget', 
        'ProfessionalChatWindow',
        'QuranTextAnalyzer',
        # الثوابت
        'MATPLOTLIB_QT_AVAILABLE',
        'GROQ_AVAILABLE',
        'DATABASE_AVAILABLE'
    ]
    
    print(f"✅ تم تحميل محلل النصوص القرآنية إصدار {__version__}")
    
except ImportError as e:
    print(f"⚠️ تحذير في تحميل المكونات: {e}")
    # في حالة وجود مشاكل في الاستيراد، نوفر الأساسيات فقط
    __all__ = []

# معلومات التطبيق
APP_INFO = {
    'name': 'محلل النصوص القرآنية المتقدم',
    'name_en': 'Advanced Quran Text Analyzer',
    'version': __version__,
    'author': __author__,
    'description': __description__,
    'features': [
        'تحليل متقدم للنصوص العربية',
        'واجهة مستخدم احترافية بـ PyQt5',
        'دعم عدة ثيمات وخطوط عربية',
        'شات ذكي مع الذكاء الاصطناعي',
        'تحليل ملفات SVG',
        'مقارنة النصوص',
        'إحصائيات ورسوم بيانية',
        'استخراج إحداثيات من الصور'
    ],
    'requirements': [
        'PyQt5>=5.15.0',
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'arabic-reshaper>=2.1.0',
        'python-bidi>=0.4.2',
        'markdown>=3.3.0',
        'matplotlib>=3.5.0'
    ]
}

def get_app_info():
    """الحصول على معلومات التطبيق"""
    return APP_INFO

def print_welcome():
    """طباعة رسالة الترحيب"""
    print("=" * 60)
    print(f"🕌 {APP_INFO['name']}")
    print(f"📖 {APP_INFO['description']}")
    print(f"🔢 الإصدار: {APP_INFO['version']}")
    print(f"👨‍💻 المطور: {APP_INFO['author']}")
    print("=" * 60)
    print("\n🌟 الميزات المتاحة:")
    for feature in APP_INFO['features']:
        print(f"  • {feature}")
    print()

# تشغيل رسالة الترحيب عند الاستيراد
if __name__ != "__main__":
    print_welcome()
