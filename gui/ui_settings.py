# ui_settings.py - إعدادات واجهة المستخدم المحسنة للشاشات الكبيرة
# أستيرادات للخطوط محليا وكتابت مسار الخط

import os
import sys
from pathlib import Path
from PyQt5.QtGui import QFontDatabase

# إضافة مسار الخطوط العثمانية
FONT_DIR = Path(__file__).parent.parent / "Uthmanic_font"
UTHMANIC_FONT_PATH = FONT_DIR / "uthmanic_hafs-Font.ttf"

def load_uthmanic_font():
    """تحميل الخط العثماني إلى النظام"""
    try:
        if UTHMANIC_FONT_PATH.exists():
            font_db = QFontDatabase()
            font_id = font_db.addApplicationFont(str(UTHMANIC_FONT_PATH))
            
            if font_id != -1:
                font_families = font_db.applicationFontFamilies(font_id)
                if font_families:
                    actual_font_name = font_families[0]
                    print(f"✅ تم تحميل الخط العثماني: {actual_font_name}")
                    return actual_font_name
                else:
                    print("❌ فشل في الحصول على اسم الخط")
                    return None
            else:
                print("❌ فشل في تحميل الخط العثماني")
                return None
        else:
            print(f"❌ ملف الخط غير موجود: {UTHMANIC_FONT_PATH}")
            return None
    except Exception as e:
        print(f"❌ خطأ في تحميل الخط العثماني: {e}")
        return None

# تحميل الخط العثماني عند استيراد الوحدة
LOADED_UTHMANIC_FONT = load_uthmanic_font()

THEME_SETTINGS = {
    "light": {
        "name": "🌞 فاتح",
        "background_color": "#f5f5f5",
        "text_color": "#262626",
        "highlight_color": "#6b91f0",
        "secondary_bg": "#ffffff",
        "border_color": "#e0e0e0",
        "hover_color": "#5a7bc8"
    },
    "dark": {
        "name": "🌙 داكن",
        "background_color": "#3C3737",
        "text_color": "#f5f5f5",
        "highlight_color": "#0C7C40",
        "secondary_bg": "#1c232b",  # لون خلفية خانات النتائج في الوضع الليلي
        "border_color": "#555555",
        "hover_color": "#0a6535",
        "input_bg": "#1c232b",      # خلفية مربعات الإدخال
        "results_bg": "#1c232b"     # خلفية خانات النتائج
    },
    "red_dark": {
        "name": "🔴 أحمر داكن",
        "background_color": "#212121",
        "text_color": "#f5f5f5",
        "highlight_color": "#F53838",
        "secondary_bg": "#1c232b",
        "border_color": "#444444",
        "hover_color": "#d32f2f",
        "input_bg": "#1c232b",
        "results_bg": "#1c232b"
    },
    "orange_light": {
        "name": "🟠 برتقالي فاتح",
        "background_color": "#0d1014",
        "text_color": "#f5f5f5",
        "highlight_color": "#e78427",
        "secondary_bg": "#1c232b",
        "border_color": "#444444",
        "hover_color": "#d32f2f",
        "input_bg": "#1c232b",
        "results_bg": "#1c232b"
    },
    "neon_dark": {
        "name": "📚 نيون داكن",
        "background_color": "#212121",
        "text_color": "#f5f5f5",
        "highlight_color": "#38F571",
        "secondary_bg": "#1c232b",
        "border_color": "#444444",
        "hover_color": "#2ed65f",
        "input_bg": "#1c232b",
        "results_bg": "#1c232b"
    },
    "auto": {
        "name": "🔄 تلقائي",
        "background_color": "#d5d5d5",
        "text_color": "#262626",
        "highlight_color": "#6c919e",
        "secondary_bg": "#e8e8e8",
        "border_color": "#c0c0c0",
        "hover_color": "#5a7d8a"
    },
    "blue_ocean": {
        "name": "🌊 أزرق محيطي",
        "background_color": "#1e3a5f",
        "text_color": "#e8f4f8",
        "highlight_color": "#4fc3f7",
        "secondary_bg": "#2c5282",
        "border_color": "#3182ce",
        "hover_color": "#3ba3d4"
    },
    "purple_royal": {
        "name": "👑 بنفسجي ملكي",
        "background_color": "#2d1b69",
        "text_color": "#f0e6ff",
        "highlight_color": "#9c27b0",
        "secondary_bg": "#3f2a7a",
        "border_color": "#7b1fa2",
        "hover_color": "#8e24aa"
    },
    "green_forest": {
        "name": "🌲 أخضر غابات",
        "background_color": "#1b4332",
        "text_color": "#e8f5e8",
        "highlight_color": "#52b788",
        "secondary_bg": "#2d5a3d",
        "border_color": "#40916c",
        "hover_color": "#4a9d7a"
    },
    "gold_luxury": {
        "name": "✨ ذهبي فاخر",
        "background_color": "#2c1810",
        "text_color": "#f5f1e8",
        "highlight_color": "#ffd700",
        "secondary_bg": "#3d2317",
        "border_color": "#8b6914",
        "hover_color": "#e6c200"
    }
}

# إعدادات حجم الخط - نظام مرن بالبكسل للشاشات الكبيرة
FONT_SIZE_SETTINGS = {
    "min_size": 8,       # الحد الأدنى
    "max_size": 128,     # الحد الأقصى للشاشات الكبيرة جداً
    "default_size": 18,  # الحجم الافتراضي محسن
    "step": 1,           # خطوة التغيير
    "big_step": 4        # خطوة كبيرة للتغيير السريع
}

# أحجام سريعة مقترحة للشاشات المختلفة
QUICK_FONT_SIZES = {
    "صغير جداً (8px)": 8,
    "صغير (12px)": 12,
    "عادي (16px)": 16,
    "متوسط (20px)": 20,
    "كبير (24px)": 24,
    "كبير جداً (32px)": 32,
    "عملاق (48px)": 48,
    "للشاشات الكبيرة (64px)": 64,
    "للشاشات العملاقة (96px)": 96
}

# خطوط محسنة مع الخط العثماني
FONT_FAMILIES = {
    "default": "Arial",
    "arabic_uthmani": LOADED_UTHMANIC_FONT or "KFGQPC Uthmanic Script HAFS",     # الخط العثماني الأصلي
    "arabic_uthmani_alt": "Uthmanic Hafs",               # خط عثماني بديل
    "arabic_uthmani_simple": "Al Qalam Quran Majeed",    # خط عثماني مبسط
    "arabic": "UthmanicHafs",                            # الخط العربي الأساسي
    "arabic_naskh": "Noto Naskh Arabic",                 # خط النسخ
    "arabic_kufi": "Amiri Quran",                        # خط كوفي
    "arabic_traditional": "Traditional Arabic",          # عربي تقليدي
    "arabic_modern": "Dubai",                            # عربي حديث
    "english": "Segoe UI",                               # إنجليزي أساسي
    "english_modern": "Calibri",                         # إنجليزي حديث
    "english_classic": "Times New Roman",                # إنجليزي كلاسيكي
    "english_elegant": "Georgia",                        # إنجليزي أنيق
    "monospace": "Consolas",                             # خط أحادي المسافة
    "monospace_alt": "Courier New",                      # خط أحادي بديل
    "system_default": "System"                           # خط النظام الافتراضي
}

# إعدادات إضافية للواجهة
UI_ANIMATIONS = {
    "enabled": True,
    "duration": 200,
    "easing": "ease-in-out"
}

WINDOW_SETTINGS = {
    "default_width": 1200,
    "default_height": 800,
    "min_width": 800,
    "min_height": 600,
    "remember_size": True,
    "remember_position": True
}

def get_theme_settings(theme):
    """الحصول على إعدادات الثيم مع التحقق من الصحة"""
    if theme in THEME_SETTINGS:
        return THEME_SETTINGS[theme]
    else:
        print(f"⚠️ ثيم غير موجود: {theme}، استخدام الثيم الافتراضي")
        return THEME_SETTINGS["light"]

def validate_theme(theme):
    """التحقق من صحة الثيم"""
    return theme in THEME_SETTINGS

def validate_font_family(font_family):
    """التحقق من صحة نوع الخط"""
    return font_family in FONT_FAMILIES

def validate_font_size(font_size):
    """التحقق من صحة حجم الخط"""
    if isinstance(font_size, (int, float)):
        return FONT_SIZE_SETTINGS["min_size"] <= font_size <= FONT_SIZE_SETTINGS["max_size"]
    elif isinstance(font_size, str):
        return font_size in QUICK_FONT_SIZES
    return False

def get_font_size(size):
    """الحصول على حجم الخط - يدعم الأرقام المباشرة والأحجام السريعة"""
    if isinstance(size, (int, float)):
        # إذا كان رقماً مباشراً، تحقق من الحدود
        return max(FONT_SIZE_SETTINGS["min_size"],
                  min(FONT_SIZE_SETTINGS["max_size"], int(size)))
    elif isinstance(size, str):
        # إذا كان نصاً، ابحث في الأحجام السريعة
        return QUICK_FONT_SIZES.get(size, FONT_SIZE_SETTINGS["default_size"])
    else:
        return FONT_SIZE_SETTINGS["default_size"]

def get_font_family(family):
    """الحصول على نوع الخط"""
    return FONT_FAMILIES.get(family, FONT_FAMILIES["default"])

def get_all_themes():
    """الحصول على قائمة جميع الثيمات مع أسمائها"""
    return [(key, value["name"]) for key, value in THEME_SETTINGS.items()]

def get_all_font_sizes():
    """الحصول على قائمة الأحجام السريعة"""
    return list(QUICK_FONT_SIZES.keys())

def get_all_font_families():
    """الحصول على قائمة جميع أنواع الخطوط مع أسماء محسنة"""
    font_names = {
        "default": "Arial (افتراضي)",
        "arabic_uthmani": "🕌 الخط العثماني الأصلي",
        "arabic_uthmani_alt": "🕌 الخط العثماني البديل",
        "arabic_uthmani_simple": "🕌 الخط العثماني المبسط",
        "arabic": "📖 الخط العربي الأساسي",
        "arabic_naskh": "✍️ خط النسخ العربي",
        "arabic_kufi": "🎨 الخط الكوفي",
        "arabic_traditional": "📜 العربي التقليدي",
        "arabic_modern": "🌟 العربي الحديث",
        "english": "🔤 الإنجليزي الأساسي",
        "english_modern": "💼 الإنجليزي الحديث",
        "english_classic": "📚 الإنجليزي الكلاسيكي",
        "english_elegant": "✨ الإنجليزي الأنيق",
        "monospace": "⌨️ أحادي المسافة",
        "monospace_alt": "🖥️ أحادي المسافة البديل",
        "system_default": "🖥️ خط النظام"
    }
    return [(key, font_names.get(key, key)) for key in FONT_FAMILIES.keys()]

def get_font_size_range():
    """الحصول على نطاق أحجام الخطوط"""
    return {
        "min": FONT_SIZE_SETTINGS["min_size"],
        "max": FONT_SIZE_SETTINGS["max_size"],
        "default": FONT_SIZE_SETTINGS["default_size"],
        "step": FONT_SIZE_SETTINGS["step"],
        "big_step": FONT_SIZE_SETTINGS["big_step"]
    }

def create_stylesheet(theme_key, font_family_key, font_size):
    """إنشاء stylesheet كامل للتطبيق مع دعم الأحجام المرنة"""
    theme = get_theme_settings(theme_key)
    font_family = get_font_family(font_family_key)
    font_size_px = get_font_size(font_size)  # يدعم الأرقام المباشرة

    return f"""
    /* الستايل الرئيسي للتطبيق - محسن للشاشات الكبيرة */
    QMainWindow, QWidget {{
        background-color: {theme['background_color']};
        color: {theme['text_color']};
        font-family: '{font_family}';
        font-size: {font_size_px}px;
    }}

    /* الأزرار */
    QPushButton {{
        background-color: {theme['highlight_color']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: {font_size_px}px;
    }}

    QPushButton:hover {{
        background-color: {theme['hover_color']};
    }}

    QPushButton:pressed {{
        background-color: {theme['highlight_color']};
        transform: translateY(1px);
    }}

    /* النصوص والتسميات */
    QLabel {{
        color: {theme['text_color']};
        font-size: {font_size_px}px;
    }}

    /* الجداول */
    QTableWidget {{
        background-color: {theme['secondary_bg']};
        border: 1px solid {theme['border_color']};
        border-radius: 5px;
        gridline-color: {theme['border_color']};
        font-size: {font_size_px}px;
    }}

    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {theme['border_color']};
    }}

    QTableWidget::item:selected {{
        background-color: {theme['highlight_color']};
        color: white;
    }}

    /* مربعات النص */
    QTextEdit, QLineEdit {{
        background-color: {theme['secondary_bg']};
        border: 2px solid {theme['border_color']};
        border-radius: 5px;
        padding: 8px;
        font-size: {font_size_px}px;
    }}

    QTextEdit:focus, QLineEdit:focus {{
        border-color: {theme['highlight_color']};
    }}

    /* القوائم المنسدلة */
    QComboBox {{
        background-color: {theme['secondary_bg']};
        border: 2px solid {theme['border_color']};
        border-radius: 5px;
        padding: 8px;
        font-size: {font_size_px}px;
    }}

    QComboBox:focus {{
        border-color: {theme['highlight_color']};
    }}

    /* شريط الأرقام */
    QSpinBox {{
        background-color: {theme['secondary_bg']};
        border: 2px solid {theme['border_color']};
        border-radius: 5px;
        padding: 8px;
        font-size: {font_size_px}px;
        min-width: 80px;
    }}

    QSpinBox:focus {{
        border-color: {theme['highlight_color']};
    }}

    /* المجموعات */
    QGroupBox {{
        font-weight: bold;
        border: 2px solid {theme['border_color']};
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 10px;
        font-size: {font_size_px}px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }}
    """

def get_all_themes():
    """الحصول على جميع الثيمات المتاحة"""
    return list(THEME_SETTINGS.keys())

def get_all_font_sizes():
    """الحصول على جميع أحجام الخطوط المتاحة"""
    return list(QUICK_FONT_SIZES.keys())

def get_all_font_families():
    """الحصول على جميع عائلات الخطوط المتاحة"""
    return list(FONT_FAMILIES.keys())

def get_font_size_range():
    """الحصول على نطاق أحجام الخطوط"""
    return (FONT_SIZE_SETTINGS["min_size"], FONT_SIZE_SETTINGS["max_size"])

def get_current_effective_theme(theme=None):
    """الحصول على الثيم الحالي الفعال"""
    # إذا لم يتم تمرير ثيم، استخدم الثيم الافتراضي
    if theme is None:
        return "dark"

    # إذا كان الثيم "auto"، حدد الثيم بناءً على وقت النهار
    if theme == "auto":
        import datetime
        current_hour = datetime.datetime.now().hour
        # من 6 صباحاً إلى 6 مساءً = فاتح، باقي الوقت = داكن
        if 6 <= current_hour < 18:
            return "light"
        else:
            return "dark"

    # إذا كان الثيم موجود، أرجعه
    if theme in THEME_SETTINGS:
        return theme

    # إذا لم يكن موجود، أرجع الثيم الافتراضي
    return "dark"

def get_current_effective_font_size():
    """الحصول على حجم الخط الحالي الفعال"""
    # يمكن إضافة منطق لقراءة حجم الخط من الإعدادات المحفوظة
    # لكن حالياً نرجع الحجم الافتراضي
    return FONT_SIZE_SETTINGS["default_size"]

def get_current_effective_font_family():
    """الحصول على عائلة الخط الحالية الفعالة"""
    # يمكن إضافة منطق لقراءة عائلة الخط من الإعدادات المحفوظة
    # لكن حالياً نرجع العائلة الافتراضية
    return "default"
