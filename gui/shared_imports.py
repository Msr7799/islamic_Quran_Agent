#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
الاستيرادات المشتركة لمحلل النصوص القرآنية
Shared imports for Quran Text Analyzer
"""

import sys
import json
import os
import re
import unicodedata
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# PyQt5 imports
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
    QComboBox, QPushButton, QDialog, QListWidget, QListWidgetItem, QMessageBox, 
    QGroupBox, QRadioButton, QTextBrowser, QSpinBox, QCheckBox, QProgressBar, 
    QFileDialog, QScrollArea, QSizePolicy, QSpacerItem, QMainWindow, QTextEdit, 
    QApplication, QTabWidget, QTreeWidget, QTreeWidgetItem, QStatusBar, 
    QLineEdit, QAction, QDialogButtonBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QEvent
from PyQt5.QtGui import QColor, QFont, QTextCharFormat, QTextCursor

# Data processing imports
import pandas as pd
import numpy as np

# Matplotlib with error handling - الحفاظ على المعالجة الحالية للأخطاء
try:
    # محاولة آمنة لاستيراد matplotlib
    import matplotlib
    matplotlib.use('Agg')  # استخدام backend بدون GUI
    
    # اختبار استيراد Qt backend
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    
    # إذا وصلنا هنا، فكل شيء يعمل
    MATPLOTLIB_QT_AVAILABLE = True
    print("✅ تم تحميل matplotlib بنجاح")
    
except Exception as e:
    print(f"⚠️ تعطيل matplotlib بسبب: {e}")
    # تعطيل matplotlib بالكامل
    FigureCanvas = None
    Figure = None
    plt = None
    MATPLOTLIB_QT_AVAILABLE = False
    
    # إنشاء فئات بديلة - نفس الكود الحالي
    class DummyFigure:
        def clear(self): 
            # دالة فارغة - لا حاجة لتنفيذ عندما matplotlib غير متوفر
            pass
        def add_subplot(self, *_): 
            # إرجاع كائن DummyAxes بدلاً من matplotlib axes
            return DummyAxes()
        def colorbar(self, *_, **__): 
            # إرجاع كائن DummyColorbar بدلاً من matplotlib colorbar
            return DummyColorbar()
        def savefig(self, *_, **__): 
            # دالة فارغة - لا يمكن حفظ الرسم عندما matplotlib غير متوفر
            pass
    
    class DummyAxes:
        def pie(self, *_, **__): 
            # إرجاع قوائم فارغة بدلاً من بيانات matplotlib pie chart
            return [], [], []
        def bar(self, *_, **__): 
            # إرجاع قائمة فارغة بدلاً من matplotlib bar objects
            return []
        def plot(self, *_, **__): 
            # إرجاع قائمة فارغة بدلاً من matplotlib line objects
            return []
        def fill_between(self, *_, **__): 
            # دالة فارغة - لا يمكن رسم المنطقة عندما matplotlib غير متوفر
            pass
        def imshow(self, *_, **__): 
            # إرجاع كائن DummyImage بدلاً من matplotlib image
            return DummyImage()
        def set_title(self, *_, **__): 
            # دالة فارغة - لا يمكن تعيين العنوان عندما matplotlib غير متوفر
            pass
        def set_xlabel(self, *_, **__): 
            # دالة فارغة - لا يمكن تعيين تسمية المحور السيني عندما matplotlib غير متوفر
            pass
        def set_ylabel(self, *_, **__): 
            # دالة فارغة - لا يمكن تعيين تسمية المحور الصادي عندما matplotlib غير متوفر
            pass
        def set_xticks(self, *_, **__): 
            # دالة فارغة - لا يمكن تعيين علامات المحور السيني عندما matplotlib غير متوفر
            pass
        def set_xticklabels(self, *_, **__): 
            # دالة فارغة - لا يمكن تعيين تسميات علامات المحور السيني عندما matplotlib غير متوفر
            pass
        def legend(self, *_, **__): 
            # دالة فارغة - لا يمكن إضافة وسيلة الإيضاح عندما matplotlib غير متوفر
            pass
        def grid(self, *_, **__): 
            # دالة فارغة - لا يمكن إضافة الشبكة عندما matplotlib غير متوفر
            pass
        def axvline(self, *_, **__): 
            # دالة فارغة - لا يمكن رسم خط عمودي عندما matplotlib غير متوفر
            pass
        def set_yticks(self, *_, **__): 
            # دالة فارغة - لا يمكن تعيين علامات المحور الصادي عندما matplotlib غير متوفر
            pass
        def set_yticklabels(self, *_, **__): 
            # دالة فارغة - لا يمكن تعيين تسميات علامات المحور الصادي عندما matplotlib غير متوفر
            pass
        def text(self, *_, **__): 
            # دالة فارغة - لا يمكن إضافة نص عندما matplotlib غير متوفر
            pass
    
    class DummyColorbar:
        def set_label(self, *_, **__): 
            # دالة فارغة - لا يمكن تعيين تسمية شريط الألوان عندما matplotlib غير متوفر
            pass
    
    class DummyImage:
        # فئة فارغة لتمثيل كائن الصورة عندما matplotlib غير متوفر
        pass
    
    class DummyCanvas:
        def draw(self): 
            # دالة فارغة - لا يمكن رسم اللوحة عندما matplotlib غير متوفر
            pass
    
    if not MATPLOTLIB_QT_AVAILABLE:
        Figure = DummyFigure
        FigureCanvas = DummyCanvas

# Arabic text processing imports
import arabic_reshaper
from bidi.algorithm import get_display
import markdown
from markdown.extensions import codehilite
import xml.etree.ElementTree as ET

# تحميل متغيرات البيئة من ملف .env - نفس الكود الحالي
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ تم تحميل متغيرات البيئة من .env")
except ImportError:
    # إذا لم تكن مكتبة python-dotenv مثبتة، نقرأ الملف يدوياً
    def load_env_file():
        env_file = '.env'
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print("✅ تم تحميل متغيرات البيئة يدوياً من .env")
        else:
            print("⚠️ ملف .env غير موجود")
    load_env_file()

# تكوين matplotlib للعربية
if MATPLOTLIB_QT_AVAILABLE and plt:
    plt.rcParams['font.family'] = ['Arial Unicode MS', 'Tahoma', 'DejaVu Sans']

# استيراد إعدادات واجهة المستخدم المحسنة للشاشات الكبيرة
from ui_settings import (
    get_theme_settings, get_font_size, get_font_family,
    get_all_themes, get_all_font_sizes, get_all_font_families,
    create_stylesheet, WINDOW_SETTINGS, get_font_size_range,
    QUICK_FONT_SIZES
)

# استيراد الثوابت المشتركة - نفس المعالجة الحالية
try:
    import sys
    import os
    # إضافة المسار الأب للنظام
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    gui_path = os.path.join(parent_dir, 'gui')
    if gui_path not in sys.path:
        sys.path.insert(0, gui_path)
    
    from shared_constants import (
        SYSTEM_MESSAGES, APP_CONFIG, get_system_message
    )
    # استيراد الألوان والخطوط من ui_settings بدلاً من shared_constants
    try:
        from ui_settings import THEMES, FONT_FAMILIES, get_font_size
        COLORS = THEMES.get('dark', {}).get('colors', {})
        FONTS = FONT_FAMILIES
    except ImportError:
        COLORS = {}
        FONTS = {}
        def get_font_size(_): 
            # إرجاع حجم خط افتراضي عندما ui_settings غير متوفر
            return 14
    
    # الثوابت المحلية من الثوابت المشتركة المحدثة
    TITLE_STYLE = "font-size: 16px; font-weight: bold; padding: 10px;"  # ثابت مباشر
    ARABIC_CHAR_TYPE = get_system_message('arabic_char_type')
    CHAR_TYPE_LABEL = get_system_message('char_type_label')
    WARNING_TITLE = get_system_message('warning_title')
    NO_FILE_SELECTED = get_system_message('no_file_selected')
    COMPARE_TEXTS_TITLE = get_system_message('compare_texts_title')
except ImportError:
    # الثوابت الاحتياطية في حالة عدم توفر الملف المشترك
    TITLE_STYLE = "font-size: 16px; font-weight: bold; padding: 10px;"
    ARABIC_CHAR_TYPE = "حرف عربي"
    CHAR_TYPE_LABEL = "النوع"
    WARNING_TITLE = "تنبيه"
    NO_FILE_SELECTED = "لم يتم تحديد ملف"
    COMPARE_TEXTS_TITLE = "مقارنة النصوص"

# محاولة استيراد المكونات الإضافية - نفس الكود الحالي
try:
    from Agent.groq_chat_manager import GroqChatManager
    from Agent.chat_history_manager import ChatHistoryManager
    GROQ_AVAILABLE = True
except ImportError:
    print("⚠️ مكونات الذكاء الاصطناعي غير متوفرة")
    GroqChatManager = None
    ChatHistoryManager = None
    GROQ_AVAILABLE = False

try:
    import sqlite3
    DATABASE_AVAILABLE = True
except ImportError:
    print("⚠️ قاعدة البيانات غير متوفرة")
    DATABASE_AVAILABLE = False
