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
from main_window import QuranTextAnalyzer


def setup_environment():
    """إعداد البيئة والتحقق من المتطلبات"""
    print("🔧 إعداد البيئة...")
    
    # المسار الصحيح لمجلد gui
    gui_dir = Path(__file__).parent
    
    # التحقق من الملفات المطلوبة في مجلد gui
    required_files = [
        gui_dir / 'shared_imports.py',
        gui_dir / 'data_models.py', 
        gui_dir / 'analysis_widgets.py',
        gui_dir / 'svg_comparison_tools.py',
        gui_dir / 'main_window.py',
        gui_dir / 'ui_settings.py'
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
        'arabic_reshaper': 'arabic-reshaper',
        'bidi': 'python-bidi',
        'markdown': 'markdown'
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
    """إنشاء المجلدات المطلوبة في GUI_DATA"""
    # المسار الصحيح للمجلدات في GUI_DATA
    base_dir = Path(__file__).parent.parent / "GUI_DATA"
    
    directories = [
        base_dir / 'logs',
        base_dir / 'exports', 
        base_dir / 'temp',
        base_dir / 'user_data',
        base_dir / 'cache',
        base_dir / 'reports'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"📁 مجلد {directory.name} جاهز في GUI_DATA")
    
    print(f"✅ جميع المجلدات جاهزة في: {base_dir}")


def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    global app
    
    print("🚀 بدء تشغيل محلل النصوص القرآنية المتقدم")
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
        app.setApplicationName("محلل النصوص القرآنية المتقدم")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Quran Text Analyzer")
        app.setApplicationDisplayName("🕌 محلل النصوص القرآنية")
        
        # تحسين الأداء والمظهر
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # تطبيق ستايل موحد (Fusion للمظهر الاحترافي)
        app.setStyle('Fusion')
        
        print("✅ تم إنشاء تطبيق PyQt5 بنجاح")
        
        # إنشاء النافذة الرئيسية
        print("🖥️ إنشاء النافذة الرئيسية...")
        main_window = QuranTextAnalyzer()
        
        # عرض النافذة
        main_window.show()
        
        print("✅ تم عرض النافذة الرئيسية")
        print("🎉 محلل النصوص القرآنية جاهز للاستخدام!")
        print("=" * 50)
        
        # معلومات إضافية للمستخدم
        print("\n📖 نصائح الاستخدام:")
        print("  • استخدم Ctrl+T لفتح الشات الذكي")
        print("  • استخدم F5 للتحليل السريع")
        print("  • استخدم Ctrl+O لفتح ملف نصي")
        print("  • استخدم Ctrl+S لحفظ النتائج")
        print("  • تصفح التبويبات لاستكشاف جميع الميزات")
        
        # تشغيل التطبيق
        exit_code = app.exec_()
        
        print("\n👋 شكراً لاستخدام محلل النصوص القرآنية")
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
