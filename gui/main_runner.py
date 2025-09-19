#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
الملف الرئيسي لتشغيل محلل النصوص القرآنية
Main runner for Quran Text Analyzer
"""

import sys
import os
from pathlib import Path

# إضافة المسار الحالي لـ Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# استيراد PyQt5 أولاً لإنشاء QApplication مبكراً
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# إنشاء QApplication في البداية لتجنب مشكلة QFontDatabase
app = QApplication(sys.argv)

# الاستيرادات الأساسية (بعد إنشاء QApplication)
import shared_imports
from main_window import QuranAnalysisMainWindow


def setup_environment():
    """إعداد البيئة والتحقق من المتطلبات"""
    print("🔧 إعداد البيئة...")
    
    # المسار الصحيح لمجلد gui
    gui_dir = Path(__file__).parent
    
    # التحقق من الملفات المطلوبة في مجلد gui (محدث للواجهة الجديدة)
    required_files = [
        gui_dir / 'shared_imports.py',
        gui_dir / 'data_models.py', 
        gui_dir / 'analysis_widgets.py',
        gui_dir / 'complete_chat_window.py',
        gui_dir / 'main_window.py',
        gui_dir / 'Agent' / 'openrouter_chat_manager.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(file_path.name)
    
    if missing_files:
        print(f"❌ ملفات مفقودة: {missing_files}")
        return False
        
    print("✅ جميع الملفات المطلوبة موجودة")
    return True


def check_dependencies():
    """التحقق من المكتبات المطلوبة"""
    print("📦 التحقق من المكتبات...")
    
    required_packages = {
        'PyQt5': 'PyQt5',
        'pandas': 'pandas',
        'numpy': 'numpy', 
        'requests': 'requests',
        'pathlib': None,  # مدمج في Python 3.4+
        'json': None,     # مدمج في Python
        'datetime': None  # مدمج في Python
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - يجب تثبيت: pip install {pip_name}")
            missing_packages.append(pip_name)
    
    # التحقق من matplotlib (اختياري)
    try:
        import matplotlib
        print("  ✅ matplotlib (اختياري)")
    except ImportError:
        print("  ⚠️ matplotlib غير متوفر - الرسوم البيانية ستكون معطلة")
    
    if missing_packages:
        print(f"\n❌ مكتبات مفقودة: {missing_packages}")
        print("لتثبيت جميع المكتبات المطلوبة:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
        
    print("✅ جميع المكتبات الأساسية متوفرة")
    return True


def create_directories():
    """إنشاء المجلدات المطلوبة للنظام الجديد"""
    # المسار الأساسي للمشروع
    base_dir = Path(__file__).parent.parent
    
    # التأكد من وجود مجلدات البيانات الأساسية
    data_directories = [
        base_dir / 'Uthmanic_data',
        base_dir / 'Uthmanic_font',
        base_dir / 'GUI_DATA',
        base_dir / 'GUI_DATA' / 'exports',
        base_dir / 'GUI_DATA' / 'temp',
        base_dir / 'GUI_DATA' / 'cache'
    ]
    
    for directory in data_directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 تم إنشاء مجلد: {directory.name}")
        else:
            print(f"✅ مجلد موجود: {directory.name}")
    
    print(f"✅ جميع المجلدات جاهزة في المشروع")


def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    global app
    
    print("🚀 بدء تشغيل محلل النصوص القرآنية المتقدم - إصدار OpenRouter")
    print("=" * 50)
    
    # التحقق من البيئة
    if not setup_environment():
        print("❌ فشل في إعداد البيئة")
        sys.exit(1)
    
    # التحقق من المكتبات
    if not check_dependencies():
        print("❌ مكتبات مفقودة - يجب تثبيتها أولاً")
        sys.exit(1)
    
    # إنشاء المجلدات
    create_directories()
    
    try:
        # إعداد خصائص التطبيق (app تم إنشاؤه في البداية)
        app.setApplicationName("محلل النصوص القرآنية المتقدم - OpenRouter")
        app.setApplicationVersion("2.0-OpenRouter")
        app.setOrganizationName("Quran Analysis Suite")
        app.setApplicationDisplayName("🕌 محلل النصوص القرآنية - إصدار OpenRouter")
        
        # تحسين الأداء والمظهر
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # تطبيق ستايل موحد (Fusion للمظهر الاحترافي)
        app.setStyle('Fusion')
        
        # تحميل وتطبيق الخط العثماني
        from PyQt5.QtGui import QFontDatabase
        font_db = QFontDatabase()
        
        # تحميل الخط العثماني
        uthmanic_font_path = os.path.join(os.path.dirname(__file__), '..', 'Uthmanic_font', 'uthmanic_hafs-Font.ttf')
        if os.path.exists(uthmanic_font_path):
            font_id = font_db.addApplicationFont(uthmanic_font_path)
            if font_id != -1:
                font_families = font_db.applicationFontFamilies(font_id)
                if font_families:
                    uthmanic_font_family = font_families[0]
                    print(f"✅ تم تحميل الخط العثماني: {uthmanic_font_family}")
                    
                    # تعيين الخط العثماني كخط افتراضي للتطبيق
                    from PyQt5.QtGui import QFont
                    app_font = QFont(uthmanic_font_family, 14)
                    app.setFont(app_font)
                else:
                    print("⚠️ لم يتم العثور على عائلة الخط العثماني")
            else:
                print("⚠️ فشل في تحميل الخط العثماني")
        else:
            print(f"⚠️ ملف الخط العثماني غير موجود: {uthmanic_font_path}")
        
        print("✅ تم إنشاء تطبيق PyQt5 بنجاح")
        
        # إنشاء النافذة الرئيسية الجديدة مع الواجهات المحدثة
        print("🖥️ إنشاء النافذة الرئيسية مع الواجهات الجديدة...")
        main_window = QuranAnalysisMainWindow()
        
        # عرض النافذة
        main_window.show()
        
        print("✅ تم عرض النافذة الرئيسية الجديدة")
        print("🎉 محلل النصوص القرآنية - إصدار OpenRouter جاهز للاستخدام!")
        print("=" * 60)
        
        # معلومات إضافية للمستخدم
        print("\n📖 الميزات الجديدة في إصدار OpenRouter:")
        print("  • 💬 شات احترافي مع نماذج ذكية متعددة")
        print("  • 📖 عارض بيانات القرآن التفاعلي")
        print("  • 📁 دعم تنسيقات متعددة للبيانات")
        print("  • 🔤 تحليل متقدم للخط العثماني")
        print("  • ⚡ واجهة محسنة وسريعة")
        print("\n🎯 الاختصارات السريعة:")
        print("  • Ctrl+T → فتح الشات الاحترافي")
        print("  • F5 → الانتقال للتحليل السريع")
        print("  • Ctrl+O → فتح ملف نصي")
        print("  • Ctrl+S → حفظ النتائج")
        print("  • تصفح التبويبات لاستكشاف جميع الميزات الجديدة")
        
        # تشغيل التطبيق
        exit_code = app.exec_()
        
        print("\n👋 شكراً لاستخدام محلل النصوص القرآنية - إصدار OpenRouter")
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    """نقطة الدخول الرئيسية"""
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚡ تم إيقاف التطبيق بواسطة المستخدم")
        sys.exit(0)
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        sys.exit(1)
