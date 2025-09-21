#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة الشات الاحترافية المحسنة - Enhanced Professional Chat Window
مع إمكانيات تحديد النصوص والنسخ والتحكم الكامل في الواجهة
"""

from shared_imports import *
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QDialog, QSplitter
from data_models import SimpleTextProcessor
import json
import os
from datetime import datetime
import re

# استيراد مكونات الذكاء الاصطناعي والتاريخ
try:
    from Agent.openrouter_chat_manager import OpenRouterChatManager, ChatConfig
    from Agent.chat_history_manager import ChatHistoryManager
    from Agent.ai_analyzer import AIAnalyzer
    # لا نستورد analysis_widgets هنا لتجنب مشكلة QFontDatabase
    OPENROUTER_AVAILABLE = True
    print("🟢 OPENROUTER_AVAILABLE = True")
except ImportError as e:
    OPENROUTER_AVAILABLE = False
    print(f"🔴 OPENROUTER_AVAILABLE = False: {e}")
    ChatHistoryManager = None
    OpenRouterChatManager = None
    ChatConfig = None
    AIAnalyzer = None

# استيراد مدير MCP بشكل منفصل
try:
    from gui.mcp_manager import MCPManagerSidebar
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ مدير MCP غير متوفر: {e}")
    MCPManagerSidebar = None
    MCP_AVAILABLE = False

# استيراد محرك Markdown المتطور
try:
    from gui.markdown_renderer import MessageContentRenderer
    MARKDOWN_AVAILABLE = True
    print("🟢 MARKDOWN_AVAILABLE = True")
except ImportError as e:
    print(f"🔴 MARKDOWN_AVAILABLE = False: {e}")
    MessageContentRenderer = None
    MARKDOWN_AVAILABLE = False

# ثوابت
NO_FILE_SELECTED = "لم يتم اختيار ملف"

class FontSettingsDialog(QDialog):
    """نافذة إعدادات الخط"""
    
    def __init__(self, parent=None, current_size=14, current_family="Arial Unicode MS"):
        super().__init__(parent)
        self.font_size = current_size
        self.font_family = current_family
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم للحوار"""
        self.setWindowTitle("⚙️ إعدادات الخط")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # تعيين النافذة في الوسط
        self.center_on_parent()
        
        # تخطيط رئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # عنوان
        title_label = QLabel("🔤 تخصيص إعدادات الخط:")
        title_label.setStyleSheet("""
            QLabel {
                color: #2E7D32;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
        """)
        
        # حجم الخط
        size_group = QGroupBox("حجم الخط")
        size_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding-top: 10px;
            }
        """)
        
        size_layout = QVBoxLayout(size_group)
        
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(10, 24)
        self.size_slider.setValue(self.font_size)
        self.size_slider.setTickInterval(2)
        self.size_slider.setTickPosition(QSlider.TicksBelow)
        
        self.size_label = QLabel(f"الحجم الحالي: {self.font_size}px")
        self.size_label.setAlignment(Qt.AlignCenter)
        
        self.size_slider.valueChanged.connect(self.update_size_label)
        
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_label)
        
        # عائلة الخط
        family_group = QGroupBox("نوع الخط")
        family_group.setStyleSheet(size_group.styleSheet())
        
        family_layout = QVBoxLayout(family_group)
        
        self.font_combo = QComboBox()
        self.font_combo.addItems([
            "Arial Unicode MS",
            "Tahoma",
            "Arial",
            "Times New Roman",
            "Calibri",
            "Segoe UI"
        ])
        
        # تعيين الخط الحالي
        if self.font_family in [self.font_combo.itemText(i) for i in range(self.font_combo.count())]:
            self.font_combo.setCurrentText(self.font_family)
        
        family_layout.addWidget(self.font_combo)
        
        # معاينة
        preview_group = QGroupBox("معاينة")
        preview_group.setStyleSheet(size_group.styleSheet())
        
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("نص تجريبي - Sample Text - 123")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                padding: 20px;
                border-radius: 5px;
            }
        """)
        
        self.update_preview()
        
        preview_layout.addWidget(self.preview_label)
        
        # ربط التغييرات بالمعاينة
        self.size_slider.valueChanged.connect(self.update_preview)
        self.font_combo.currentTextChanged.connect(self.update_preview)
        
        # أزرار
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton("✅ تطبيق")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        # إضافة العناصر للتخطيط
        main_layout.addWidget(title_label)
        main_layout.addWidget(size_group)
        main_layout.addWidget(family_group)
        main_layout.addWidget(preview_group)
        main_layout.addLayout(button_layout)
        
        # تطبيق نمط الحوار
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
    
    def center_on_parent(self):
        """توسيط النافذة على النافذة الأم"""
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def update_size_label(self, value):
        """تحديث تسمية الحجم"""
        self.size_label.setText(f"الحجم الحالي: {value}px")
        self.font_size = value
    
    def update_preview(self):
        """تحديث المعاينة"""
        font = QFont(self.font_combo.currentText(), self.size_slider.value())
        self.preview_label.setFont(font)
        self.font_family = self.font_combo.currentText()
    
    def get_font_settings(self):
        """الحصول على إعدادات الخط"""
        return {
            'size': self.font_size,
            'family': self.font_family
        }

class InternetSearchDialog(QDialog):
    """نافذة حوار البحث في الإنترنت"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_query = ""
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم للحوار"""
        self.setWindowTitle("🌐 بحث في الإنترنت")
        self.setFixedSize(500, 200)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # تعيين النافذة في الوسط
        self.center_on_parent()
        
        # تخطيط رئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # عنوان
        title_label = QLabel("🔍 أدخل استعلام البحث:")
        title_label.setStyleSheet("""
            QLabel {
                color: #2E7D32;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
        """)
        
        # حقل الإدخال
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("اكتب ما تريد البحث عنه...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                font-family: 'Arial Unicode MS', 'Tahoma';
                background-color: #FAFAFA;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                background-color: white;
            }
        """)
        
        # أزرار
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # زر الإلغاء
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # زر البحث
        search_btn = QPushButton("🔍 بحث")
        search_btn.setFixedHeight(40)
        search_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #66BB6A, stop:1 #4CAF50);
            }
        """)
        search_btn.clicked.connect(self.accept_search)
        search_btn.setDefault(True)
        
        # ربط Enter بالبحث
        self.search_input.returnPressed.connect(self.accept_search)
        
        # إضافة العناصر للتخطيط
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.search_input)
        main_layout.addStretch()
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(search_btn)
        
        main_layout.addLayout(button_layout)
        
        # تعيين التركيز على حقل الإدخال
        self.search_input.setFocus()
        
        # تطبيق نمط الحوار
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
            }
        """)
    
    def center_on_parent(self):
        """توسيط النافذة على النافذة الأم"""
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        else:
            # توسيط على الشاشة
            screen = QApplication.desktop().screenGeometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)
    
    def accept_search(self):
        """قبول البحث وحفظ الاستعلام"""
        query = self.search_input.text().strip()
        if query:
            self.search_query = query
            self.accept()
    
    def get_search_query(self):
        """الحصول على استعلام البحث"""
        return self.search_query


class SelectableTextLabel(QLabel):
    """QLabel قابل للتحديد والنسخ مع تحسينات إضافية"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.setWordWrap(True)
        self.setOpenExternalLinks(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        """عرض قائمة السياق للنسخ والتحديد"""
        context_menu = QMenu(self)
        
        # نسخ النص المحدد
        copy_action = context_menu.addAction("📋 نسخ النص المحدد")
        copy_action.triggered.connect(self.copy_selected_text)
        copy_action.setEnabled(bool(self.selectedText()))
        
        # نسخ كامل النص
        copy_all_action = context_menu.addAction("📄 نسخ كامل النص")
        copy_all_action.triggered.connect(self.copy_all_text)
        
        # تحديد الكل
        select_all_action = context_menu.addAction("🎯 تحديد الكل")
        select_all_action.triggered.connect(self.select_all_text)
        
        context_menu.addSeparator()
        
        # بحث في Google (إذا كان هناك نص محدد)
        if self.selectedText().strip():
            search_action = context_menu.addAction("🔍 بحث في Google")
            search_action.triggered.connect(self.search_selected_text)
        
        context_menu.exec_(self.mapToGlobal(position))
    
    def copy_selected_text(self):
        """نسخ النص المحدد"""
        clipboard = QApplication.clipboard()
        if self.selectedText():
            clipboard.setText(self.selectedText())
            self.show_copy_notification("تم نسخ النص المحدد")
    
    def copy_all_text(self):
        """نسخ كامل النص"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text())
        self.show_copy_notification("تم نسخ كامل النص")
    
    def select_all_text(self):
        """تحديد كامل النص"""
        self.setSelection(0, len(self.text()))
    
    def search_selected_text(self):
        """البحث عن النص المحدد في Google"""
        import webbrowser
        selected = self.selectedText().strip()
        if selected:
            search_url = f"https://www.google.com/search?q={selected}"
            webbrowser.open(search_url)
    
    def show_copy_notification(self, message):
        """عرض إشعار النسخ"""
        # إشعار مؤقت
        notification = QLabel(message, self)
        notification.setStyleSheet("""
            QLabel {
                background-color: rgba(46, 125, 50, 0.9);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        notification.setAlignment(Qt.AlignCenter)
        notification.resize(150, 30)
        notification.move(self.width()//2 - 75, 10)
        notification.show()
        
        # إخفاء الإشعار بعد 2 ثانية
        QTimer.singleShot(2000, notification.deleteLater)

class MessageBubble(QWidget):
    """فقاعة رسالة محسنة مع تأثيرات بصرية وتحكم كامل"""
    
    def __init__(self, sender, message, timestamp=None, parent=None):
        super().__init__(parent)
        self.sender = sender
        self.message = message
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")
        self.is_user = sender == "user"
        
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """إعداد واجهة فقاعة الرسالة"""
        self.setContentsMargins(0, 5, 0, 5)
        
        # الحاوية الرئيسية - تأخذ العرض كاملاً
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 0, 10, 0)  # تقليل الهوامش
        
        # فقاعة المحتوى - تأخذ المساحة المتبقية (بدون أيقونات خارجية)
        bubble_container = self.create_bubble_container()
        main_layout.addWidget(bubble_container, 1)  # stretch factor = 1
    
    def create_avatar(self):
        """إنشاء صورة رمزية للمساعد"""
        avatar_container = QWidget()
        avatar_container.setFixedSize(45, 45)
        
        avatar_label = QLabel("🤖")
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet("""
            QLabel {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e4e4e4, stop:1 #e4e4e4);
                border-radius: 12px;
                color: white;
                font-size: 24px;
                border: 3px solid rgba(255, 255, 255, 0.3);
            }
        """)
        avatar_label.setFixedSize(45, 45)
        
        layout = QVBoxLayout(avatar_container)
        layout.setContentsMargins(5, 0, 0, 0)
        layout.addWidget(avatar_label)
        
        return avatar_container
    
    def create_bubble_container(self):
        """إنشاء حاوية فقاعة الرسالة"""
        container = QWidget()
        # إزالة تحديد العرض الأقصى لتأخذ المساحة كاملة
        # container.setMaximumWidth(600)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # فقاعة المحتوى الرئيسية
        bubble = self.create_message_bubble()
        layout.addWidget(bubble)
        
        # معلومات الوقت
        time_info = self.create_time_info()
        layout.addWidget(time_info)
        
        return container
    
    def create_message_bubble(self):
        """إنشاء فقاعة الرسالة الفعلية"""
        bubble = QFrame()
        bubble.setFrameStyle(QFrame.Box)
        
        # تحديد الألوان والاتجاه حسب المرسل
        if self.is_user:
            bubble_style = """
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #677770, stop:1 #677777);
                    border: 2px solid rgba(15,15,55);
                    border-radius: 6px;
                    border-bottom-right-radius: 6px;
                    margin: 5px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }
            """
            text_color = "white"
            alignment = Qt.AlignRight
        else:
            bubble_style = """
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #f5f5f5, stop:1 #e0e0e0);
                    border: 1px solid rgba(15,15,55);
                    border-radius: 8px;
                    margin: 2px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                }
            """
            text_color = "#D9D9D9"
            alignment = Qt.AlignLeft
        
        bubble.setStyleSheet(bubble_style)
        
        # تخطيط المحتوى
        content_layout = QVBoxLayout(bubble)
        content_layout.setContentsMargins(15, 12, 15, 12)
        
        # إضافة حاوية للأيقونة والنص
        message_container = QWidget()
        message_layout = QHBoxLayout(message_container)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(10)
        
        # إضافة الأيقونة داخل الفقاعة
        if self.is_user:
            # أيقونة المستخدم
            user_icon = QLabel("👤")
            user_icon.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    background-color: rgba(255, 255, 255, 0.8);
                    padding: 5px;
                    margin-left: 10px;
                    min-width: 30px;
                    max-width: 30px;
                    min-height: 30px;
                    max-height: 30px;
                }
            """)
            user_icon.setAlignment(Qt.AlignCenter)
            message_layout.addWidget(user_icon)
        else:
            # أيقونة الذكاء الاصطناعي من الملف
            ai_icon = QLabel()
            try:
                import os
                icon_path = os.path.join(os.path.dirname(__file__), "assets", "ai_icon.png")
                if os.path.exists(icon_path):
                    from PyQt5.QtGui import QPixmap
                    pixmap = QPixmap(icon_path)
                    # تحجيم الصورة
                    scaled_pixmap = pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    ai_icon.setPixmap(scaled_pixmap)
                else:
                    ai_icon.setText("🤖")
                    ai_icon.setStyleSheet("font-size: 20px;")
            except:
                ai_icon.setText("🤖")
                ai_icon.setStyleSheet("font-size: 20px;")
            
            ai_icon.setStyleSheet(ai_icon.styleSheet() + """
                QLabel {
                    background-color: rgba(255, 255, 255, 0.8);
                    padding: 5px;
                    margin-right: 10px;
                    min-width: 30px;
                    max-width: 30px;
                    min-height: 30px;
                    max-height: 30px;
                }
            """)
            ai_icon.setAlignment(Qt.AlignCenter)
            message_layout.addWidget(ai_icon)
        
        # معالجة النص باستخدام محرك Markdown المتطور للذكاء الاصطناعي
        if not self.is_user and MARKDOWN_AVAILABLE:
            # استخدام محرك Markdown المتطور للذكاء الاصطناعي
            markdown_widget = MessageContentRenderer(self.message)
            markdown_widget.setStyleSheet(f"""
                MessageContentRenderer {{
                    background: transparent;
                    color: {text_color};
                }}
            """)
            message_layout.addWidget(markdown_widget, 1)
        else:
            # معالجة النص العادي للمستخدم أو إذا لم يكن Markdown متوفراً
            processed_message = self.process_message_content(self.message)
            
            # النص الرئيسي
            message_label = SelectableTextLabel(processed_message)
            message_label.setAlignment(alignment)
            message_label.setStyleSheet(f"""
                SelectableTextLabel {{
                    color: {text_color};
                    background: transparent;
                    font-size: 14px;
                    line-height: 1.4;
                    font-family: 'Arial Unicode MS', 'Tahoma', 'Segoe UI';
                    font-weight: 500;
                }}
            """)
            message_label.setTextFormat(Qt.RichText)
            
            # إضافة النص إلى التخطيط
            message_layout.addWidget(message_label, 1)  # stretch factor = 1
        
        # إضافة حاوية الرسالة إلى التخطيط الرئيسي
        content_layout.addWidget(message_container)
        
        # إضافة أزرار التحكم للرسائل الطويلة
        if len(self.message) > 500:
            controls = self.create_message_controls()
            content_layout.addWidget(controls)
        
        return bubble
    
    def create_message_controls(self):
        """إنشاء أزرار التحكم في الرسالة"""
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(5, 5, 5, 5)
        controls_layout.setSpacing(8)
        
        # زر النسخ
        copy_btn = QPushButton("📋")
        copy_btn.setFixedSize(30, 25)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(250, 108, 71, 0.4);
                border-radius: 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(250, 100, 71, 0.7);
            }
        """)
        copy_btn.setToolTip("نسخ النص")
        copy_btn.clicked.connect(self.copy_message)
        
        # زر المشاركة
        share_btn = QPushButton("🔗")
        share_btn.setFixedSize(30, 25)
        share_btn.setStyleSheet(copy_btn.styleSheet())
        share_btn.setToolTip("مشاركة")
        share_btn.clicked.connect(self.share_message)
        
        controls_layout.addWidget(copy_btn)
        controls_layout.addWidget(share_btn)
        controls_layout.addStretch()
        
        return controls_widget
    
    def create_time_info(self):
        """إنشاء معلومات الوقت"""
        time_container = QWidget()
        time_layout = QHBoxLayout(time_container)
        time_layout.setContentsMargins(15, 0, 15, 5)
        
        time_label = QLabel(f"🕒 {self.timestamp}")
        time_label.setStyleSheet("""
            QLabel {
                color: rgba(20, 20, 10, 05);
                font-size: 14px;
                font-style: italic;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
        """)
        
        if self.is_user:
            time_layout.addStretch()
            time_layout.addWidget(time_label)
        else:
            time_layout.addWidget(time_label)
            time_layout.addStretch()
        
        return time_container
    
    def process_message_content(self, message):
        """معالجة محتوى الرسالة لدعم تنسيق بسيط"""
        # تحويل النص العادي إلى HTML مع دعم الروابط والتنسيق
        processed = message
        
        # تحويل الروابط
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        processed = re.sub(url_pattern, r'<a href="\g<0>" style="color: #4CAF50; text-decoration: none;">\g<0></a>', processed)
        
        # تحويل **النص** إلى نص عريض
        processed = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', processed)
        
        # تحويل *النص* إلى نص مائل  
        processed = re.sub(r'\*(.*?)\*', r'<em>\1</em>', processed)
        
        # تحويل الأسطر الجديدة
        processed = processed.replace('\n', '<br>')
        
        # إضافة تحسينات للنصوص العربية
        if any('\u0600' <= char <= '\u06FF' for char in processed):
            processed = f'<div dir="rtl" style="text-align: right; font-family: \'Arial Unicode MS\', \'Tahoma\';">{processed}</div>'
        
        return processed
    
    def copy_message(self):
        """نسخ محتوى الرسالة"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.message)
        
        # إظهار إشعار النسخ
        self.show_notification("تم نسخ الرسالة")
    
    def share_message(self):
        """مشاركة الرسالة"""
        # يمكن تطوير هذه الوظيفة لاحقاً
        self.show_notification("وظيفة المشاركة قيد التطوير")
    
    def show_notification(self, message):
        """عرض إشعار مؤقت"""
        notification = QLabel(message, self)
        notification.setStyleSheet("""
            QLabel {
                background-color: rgba(76, 175, 80, 0.9);
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        notification.setAlignment(Qt.AlignCenter)
        notification.adjustSize()
        
        # وضع الإشعار في المنتصف
        x = (self.width() - notification.width()) // 2
        y = 10
        notification.move(x, y)
        notification.show()
        
        # إخفاء الإشعار بعد ثانيتين
        QTimer.singleShot(2000, notification.deleteLater)
    
    def setup_animations(self):
        """إعداد التأثيرات والحركات"""
        # تأثير الظهور التدريجي
        self.fade_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.fade_effect)
        
        self.fade_animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        
        # بدء التأثير
        QTimer.singleShot(50, self.fade_animation.start)

class ProfessionalChatWindow(QMainWindow):
    """واجهة الشات الاحترافية المحسنة مع تحكم كامل وتأثيرات بصرية"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversation_history = []
        self.chat_manager = None
        self.input_history = []
        self.input_history_index = -1
        self.current_theme = "dark"
        self.sidebar_visible = True
        
        # إعدادات واجهة المستخدم - ستأخذ من النافذة الأب
        self.theme = "dark"
        self.font_size = 14
        self.font_family = "Arial Unicode MS"

        # إذا كان هناك نافذة أب، خذ الإعدادات منها
        if parent and hasattr(parent, 'theme'):
            self.theme = parent.theme
            self.font_size = parent.font_size
            self.font_family = parent.font_family

        # إعداد مدير تاريخ المحادثات
        self.setup_history_manager()
        
        # إعداد الواجهة والمكونات
        self.setup_ui()
        self.setup_ai_components()
        self.setup_shortcuts()
        
        # تحميل المحادثة الحالية
        self.load_current_conversation()
        
        # تطبيق الثيم
        self.apply_theme()

    def setup_history_manager(self):
        """إعداد مدير تاريخ المحادثات"""
        try:
            if ChatHistoryManager:
                self.history_manager = ChatHistoryManager()
                print("✅ تم تهيئة مدير تاريخ المحادثات")
            else:
                self.history_manager = None
        except Exception as e:
            print(f"❌ خطأ في تهيئة مدير التاريخ: {e}")
            self.history_manager = None

    def setup_ui(self):
        """إعداد واجهة الشات المحسنة"""
        self.setWindowTitle("💬 المساعد الذكي للقرآن الكريم - محسن")
        self.setGeometry(100, 100, 1400, 900)
        
        # تفعيل تغيير الحجم
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # تطبيق أيقونة مخصصة
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # إعداد الويدجت المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # استخدام QSplitter مع إمكانية إخفاء/إظهار الشريط الجانبي
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setHandleWidth(6)
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #555555;
                width: 6px;
                border: 1px solid #777777;
                border-radius: 3px;
            }
            QSplitter::handle:hover {
                background-color: #f36d0b;
            }
            QSplitter::handle:pressed {
                background-color: #f86d06;
            }
        """)
        
        # إنشاء الشريط الجانبي
        self.sidebar_widget = QWidget()
        sidebar_layout = QHBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.create_sidebar(sidebar_layout)
        
        # إنشاء منطقة الشات
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        # إنشاء منطقة الشات الرئيسية  
        self.create_main_chat_area(chat_layout)
        
        # إضافة العناصر للـ splitter
        self.main_splitter.addWidget(self.sidebar_widget)
        self.main_splitter.addWidget(chat_widget)
        
        # تعيين الأحجام الافتراضية - عرض مرن للشريط الجانبي
        self.main_splitter.setSizes([300, 1100])
        self.main_splitter.setStretchFactor(0, 0)  # الشريط الجانبي ثابت
        self.main_splitter.setStretchFactor(1, 1)  # منطقة الشات مرنة
        
        # التخطيط الرئيسي
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main_splitter)
        
        # تطبيق الستايل العام
        self.apply_global_styles()

    def toggle_sidebar(self):
        """تبديل إخفاء/إظهار الشريط الجانبي"""
        if self.sidebar_visible:
            # إخفاء الشريط الجانبي
            self.sidebar_widget.hide()
            self.sidebar_toggle_btn.setText("▶")
            self.sidebar_toggle_btn.setToolTip("إظهار القائمة الجانبية")
            self.sidebar_visible = False
        else:
            # إظهار الشريط الجانبي
            self.sidebar_widget.show()
            self.sidebar_toggle_btn.setText("◀")
            self.sidebar_toggle_btn.setToolTip("إخفاء القائمة الجانبية")
            self.sidebar_visible = True

    def create_sidebar(self, main_layout):
        """إنشاء الشريط الجانبي للتحكم مع سكرول وأحجام محسنة"""
        sidebar = QFrame()
        sidebar.setMinimumWidth(280)  # حد أدنى أكبر
        sidebar.setMaximumWidth(400)  # حد أقصى للعرض
        sidebar.setFrameStyle(QFrame.StyledPanel)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #222;
                border-right: 2px solid #2a2a2a;
            }
        """)
        
        # إنشاء ScrollArea للشريط الجانبي
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        sidebar_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #303030;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.1);
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #585858;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #030303;
            }
        """)
        
        sidebar_content = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_content)
        sidebar_layout.setContentsMargins(8, 8, 8, 8)
        sidebar_layout.setSpacing(6)
        
        # عنوان الشريط الجانبي
        title = QLabel("🎛️ لوحة التحكم")
        title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                padding: 6px 4px;
                background-color: #101010;
                border-radius: 4px;
                text-align: center;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(28)
        sidebar_layout.addWidget(title)
        
        # قسم إدارة المحادثات
        self.create_chat_management_section(sidebar_layout)
        
        # قسم إعدادات النموذج
        self.create_model_settings_section(sidebar_layout)
        
        # قسم إدارة MCP Servers
        self.create_mcp_manager_section(sidebar_layout)
        
        # قسم ملفات التعليمات
        self.create_instructions_section(sidebar_layout)
        
        # قسم المؤشرات والحالة
        self.create_status_section(sidebar_layout)
        
        # قسم الإعدادات العامة
        self.create_settings_section(sidebar_layout)
        
        sidebar_layout.addStretch()
        
        sidebar_scroll.setWidget(sidebar_content)
        
        sidebar_main_layout = QVBoxLayout(sidebar)
        sidebar_main_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_main_layout.addWidget(sidebar_scroll)
        
        main_layout.addWidget(sidebar)

    def create_mcp_manager_section(self, layout):
        """إنشاء قسم إدارة MCP Servers بحجم محسن"""
        # مجموعة إدارة MCP Servers
        group = QGroupBox("🔧 إدارة MCP Servers")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                color: #ffffff;
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 6px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 6px 0 6px;
                color: #ffffff;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 12, 8, 6)
        group_layout.setSpacing(4)
        
        # قائمة خوادم MCP محسنة
        mcp_info = QLabel("🟢 Tavily Search\n🟢 Time MCP\n🔴 Filesystem\n🔴 Memory")
        mcp_info.setStyleSheet("""
            QLabel {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px 6px;
                font-size: 12px;
                color: #ffffff;
                line-height: 1.2;
                word-wrap: break-word;
                white-space: pre-wrap;
            }
        """)
        mcp_info.setWordWrap(True)
        mcp_info.setMinimumHeight(60)
        group_layout.addWidget(mcp_info)
        
        # أزرار إدارة محسنة
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕")
        add_btn.setMinimumSize(24, 24)
        add_btn.setToolTip("إضافة خادم")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666;
                border-radius: 4px;
                color: #ffffff;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        btn_layout.addWidget(add_btn)
        
        settings_btn = QPushButton("⚙️")
        settings_btn.setMinimumSize(24, 24)
        settings_btn.setToolTip("إعدادات")
        settings_btn.setStyleSheet(add_btn.styleSheet())
        btn_layout.addWidget(settings_btn)
        
        btn_layout.addStretch()
        group_layout.addLayout(btn_layout)
        
        layout.addWidget(group)

    def on_mcp_changed(self, server_name: str, enabled: bool):
        """استدعى عند تغيير حالة MCP server"""
        status = "تفعيل" if enabled else "إلغاء تفعيل"
        print(f"🔄 تم {status} MCP Server: {server_name}")
        if self.chat_manager:
            self.chat_manager.refresh_mcp_tools()

    def on_mcp_updated(self):
        """استدعى عند تحديث تكوين MCP"""
        print("🔄 تم تحديث تكوين MCP servers")
        if self.chat_manager:
            self.chat_manager.refresh_mcp_tools()

    def create_chat_management_section(self, layout):
        """إنشاء قسم إدارة المحادثات بحجم محسن"""
        group = QGroupBox("💬 إدارة المحادثات")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 6px;
                padding-top: 12px;
                color: #ffffff;
                background-color: #303030;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                border-radius: 2px;
                background-color: #505050;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 12, 8, 6)
        group_layout.setSpacing(4)
        
        # أزرار إدارة المحادثات بحجم محسن
        new_chat_btn = self.create_sidebar_button("🆕 محادثة جديدة", "#4CAF50")
        new_chat_btn.clicked.connect(self.start_new_chat)
        
        history_btn = self.create_sidebar_button("📂 سجل المحادثات", "#2196F3")
        history_btn.clicked.connect(self.show_chat_history)
        
        clear_btn = self.create_sidebar_button("🗑️ مسح المحادثة", "#f44336")
        clear_btn.clicked.connect(self.clear_current_chat)
        
        export_btn = self.create_sidebar_button("💾 تصدير المحادثة", "#FF9800")
        export_btn.clicked.connect(self.export_conversation)
        
        group_layout.addWidget(new_chat_btn)
        group_layout.addWidget(history_btn)
        group_layout.addWidget(clear_btn)
        group_layout.addWidget(export_btn)
        
        layout.addWidget(group)

    def create_model_settings_section(self, layout):
        """إنشاء قسم إعدادات النموذج بحجم محسن"""
        group = QGroupBox("🤖 إعدادات النموذج")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 6px;
                padding-top: 12px;
                color: #ffffff;
                background-color: #404040;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                border-radius: 2px;
                background-color: #505050;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 12, 8, 6)
        group_layout.setSpacing(4)
        
        # اختيار النموذج
        model_label = QLabel("النموذج الحالي:")
        model_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        
        self.model_selector = QComboBox()
        self.model_selector.setMinimumHeight(28)
        self.model_selector.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                color: white;
            }
            QComboBox QAbstractItemView {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                selection-background-color: #555;
            }
        """)
        
        # أزرار التحكم في الميزات
        self.db_toggle = self.create_toggle_button("📚 قاعدة البيانات", True)
        self.internet_toggle = self.create_toggle_button("🌐 بحث الإنترنت", True)
        self.ai_toggle = self.create_toggle_button("🧠 الذكاء الاصطناعي", True)
        
        group_layout.addWidget(model_label)
        group_layout.addWidget(self.model_selector)
        group_layout.addWidget(self.db_toggle)
        group_layout.addWidget(self.internet_toggle)
        group_layout.addWidget(self.ai_toggle)
        
        # تحميل النماذج وربط الأحداث
        self.load_models_to_selector()
        
        # ربط حدث تغيير النموذج بطريقة محسنة
        self.model_selector.currentTextChanged.connect(self.on_model_changed)
        self.model_selector.currentIndexChanged.connect(self.on_model_changed)
        
        # تحديث فوري للعرض
        QTimer.singleShot(500, self.update_model_display)
        
        layout.addWidget(group)

    def create_instructions_section(self, layout):
        """إنشاء قسم ملفات التعليمات بحجم محسن"""
        group = QGroupBox("📋 ملفات التعليمات")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 6px;
                padding-top: 12px;
                color: #ffffff;
                background-color: #404040;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                border-radius: 2px;
                background-color: #505050;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 12, 8, 6)
        group_layout.setSpacing(4)
        
        # إنشاء 4 أزرار لملفات التعليمات
        self.instruction_files = [
            {"name": f"📄 تعليمات {i+1}", "file": None, "mode": "auto"}
            for i in range(4)
        ]
        
        for i, instruction in enumerate(self.instruction_files):
            btn = self.create_sidebar_button(instruction["name"], "#9C27B0")
            btn.clicked.connect(lambda checked, idx=i: self.manage_instruction_file(idx))
            group_layout.addWidget(btn)
        
        layout.addWidget(group)

    def create_status_section(self, layout):
        """إنشاء قسم المؤشرات والحالة بحجم محسن"""
        group = QGroupBox("📊 حالة النظام")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                background-color: #404040;
                margin-top: 6px;
                padding-top: 12px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                border-radius: 2px;
                background-color: #505050;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 12, 8, 6)
        group_layout.setSpacing(4)
        
        # مؤشرات الحالة
        self.create_status_indicators(group_layout)
        
        # عداد الرسائل
        self.message_counter = QLabel("0 رسالة")
        self.message_counter.setAlignment(Qt.AlignCenter)
        self.message_counter.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 13px;
                font-weight: bold;
                padding: 6px;
                background-color: rgba(76, 175, 80, 0.2);
                border-radius: 4px;
            }
        """)
        group_layout.addWidget(self.message_counter)
        
        layout.addWidget(group)

    def create_settings_section(self, layout):
        """إنشاء قسم الإعدادات العامة بحجم محسن"""
        group = QGroupBox("⚙️ الإعدادات")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 6px;
                padding-top: 12px;
                color: #ffffff;
                background-color: #404040;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                background-color: #505050;
                border-radius: 2px;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 12, 8, 6)
        group_layout.setSpacing(4)
        
        # أزرار الإعدادات
        theme_btn = self.create_sidebar_button("🎨 تغيير الثيم", "#607D8B")
        theme_btn.clicked.connect(self.toggle_theme)
        
        font_btn = self.create_sidebar_button("🔤 إعدادات الخط", "#795548")
        font_btn.clicked.connect(self.show_font_settings)
        
        about_btn = self.create_sidebar_button("ℹ️ حول البرنامج", "#9E9E9E")
        about_btn.clicked.connect(self.show_about_dialog)
        
        # أزرار إضافية
        attachment_btn = self.create_sidebar_button("📎 إرفاق ملف", "#2196F3")
        attachment_btn.clicked.connect(self.attach_file)
        
        voice_btn = self.create_sidebar_button("🎤 تسجيل صوتي", "#FF9800")
        voice_btn.clicked.connect(self.voice_input)
        
        search_btn = self.create_sidebar_button("🌐 بحث الإنترنت", "#009688")
        search_btn.clicked.connect(self.show_internet_search_dialog)
        
        group_layout.addWidget(theme_btn)
        group_layout.addWidget(font_btn)
        group_layout.addWidget(attachment_btn)
        group_layout.addWidget(voice_btn)
        group_layout.addWidget(search_btn)
        group_layout.addWidget(about_btn)
        
        layout.addWidget(group)

    def create_main_chat_area(self, main_layout):
        """إنشاء منطقة الشات الرئيسية"""
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        # شريط علوي مع معلومات الشات والنموذج
        self.create_top_bar(chat_layout)
        
        # شريط معلومات النموذج والمستخدم
        self.create_model_info_bar(chat_layout)
        
        # منطقة الرسائل
        self.create_messages_area(chat_layout)
        
        # منطقة الإدخال المحسنة
        self.create_enhanced_input_area(chat_layout)
        
        main_layout.addWidget(chat_container)

    def create_top_bar(self, layout):
        """إنشاء الشريط العلوي المحسن"""
        top_bar = QFrame()
        top_bar.setFixedHeight(70)
        top_bar.setFrameStyle(QFrame.StyledPanel)
        
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 10, 20, 10)
        
        # العنوان مع الأيقونة وزر التبديل
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)

        # إضافة زر إخفاء/إظهار الشريط الجانبي بجانب أيقونة الروبوت
        self.sidebar_toggle_btn = QPushButton("◀")
        self.sidebar_toggle_btn.setFixedSize(30, 30)
        self.sidebar_toggle_btn.setToolTip("إخفاء/إظهار القائمة الجانبية")
        self.sidebar_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(243, 109, 11, 0.8);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(243, 109, 11, 1.0);
            }
        """)
        self.sidebar_toggle_btn.clicked.connect(self.toggle_sidebar)

        title_icon = QLabel("🤖")
        title_icon.setStyleSheet("font-size: 32px;")

        title_text = QLabel("المساعد الذكي للقرآن الكريم")
        title_text.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
        """)

        title_layout.addWidget(self.sidebar_toggle_btn)
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        top_layout.addWidget(title_container)
        top_layout.addStretch()
        
        # معلومات الاتصال
        connection_info = self.create_connection_info()
        top_layout.addWidget(connection_info)
        
        layout.addWidget(top_bar)

    def create_connection_info(self):
        """إنشاء معلومات الاتصال"""
        info_container = QWidget()
        info_layout = QHBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(15)
        
        # حالة الاتصال
        status_dot = QLabel("●")
        status_dot.setStyleSheet("color: #4CAF50; font-size: 20px;")
        status_dot.setToolTip("متصل")
        
        # معلومات النموذج الحالي - سيتم تحديثها ديناميكياً
        self.model_info = QLabel("جاري التحميل...")
        self.model_info.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                background-color: rgba(76, 175, 80, 0.3);
                padding: 4px 8px;
                border-radius: 10px;
            }
        """)
        
        info_layout.addWidget(status_dot)
        info_layout.addWidget(self.model_info)
        
        # حفظ مرجع للتحديث لاحقاً
        self.connection_info_model = self.model_info
        
        return info_container

    def create_model_info_bar(self, layout):
        """إنشاء شريط معلومات النموذج والمستخدم"""
        model_info_container = QFrame()
        model_info_container.setFixedHeight(35)
        model_info_container.setStyleSheet("""
            QFrame {
                background-color: #444;
                border-bottom: 1px solid #555;
            }
        """)
        
        model_info_layout = QHBoxLayout(model_info_container)
        model_info_layout.setContentsMargins(15, 5, 15, 5)
        model_info_layout.setSpacing(15)
        
        # معلومات المستخدم
        user_info = QLabel("💬 مستخدم")
        user_info.setStyleSheet("""
            QLabel {
                color: #f36d0b;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        # فاصل
        separator1 = QLabel("|")
        separator1.setStyleSheet("QLabel { color: #777; }")
        
        # معلومات النموذج
        self.current_model_label = QLabel("🤖 النموذج: غير محدد")
        self.current_model_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
        """)
        
        # فاصل
        separator2 = QLabel("|")
        separator2.setStyleSheet("QLabel { color: #777; }")
        
        # حالة الاتصال
        self.connection_status = QLabel("✅ متصل")
        self.connection_status.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 12px;
            }
        """)
        
        model_info_layout.addWidget(user_info)
        model_info_layout.addWidget(separator1)
        model_info_layout.addWidget(self.current_model_label)
        model_info_layout.addWidget(separator2)
        model_info_layout.addWidget(self.connection_status)
        model_info_layout.addStretch()
        
        layout.addWidget(model_info_container)

    def create_messages_area(self, layout):
        """إنشاء منطقة الرسائل المحسنة"""
        # منطقة التمرير
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # الويدجت الذي يحتوي على الرسائل
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(0, 20, 0, 20)
        self.messages_layout.setSpacing(10)
        self.messages_layout.addStretch()  # دفع الرسائل لأعلى
        
        self.scroll_area.setWidget(self.messages_widget)
        
        # تطبيق ستايل منطقة التمرير
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #232739;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.1);
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #585858;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #00F5CC;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # تطبيق خلفية منطقة الرسائل
        self.messages_widget.setStyleSheet("""
            QWidget {
                background-color: #333;
            }
        """)
        
        # إنشاء حاوي للمنطقة الرسائل مع زر السهم
        messages_container = QWidget()
        messages_container_layout = QVBoxLayout(messages_container)
        messages_container_layout.setContentsMargins(0, 0, 0, 0)
        messages_container_layout.addWidget(self.scroll_area)
        
        # إضافة زر السهم للأعلى
        self.create_scroll_to_top_button(messages_container)
        
        layout.addWidget(messages_container)
        
        # رسالة الترحيب سيتم إضافتها في load_current_conversation

    def create_scroll_to_top_button(self, parent):
        """إنشاء زر التمرير إلى الأعلى"""
        self.scroll_to_top_btn = QPushButton("↑")
        self.scroll_to_top_btn.setFixedSize(40, 40)
        self.scroll_to_top_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 212, 170, 0.8);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 245, 204, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(0, 180, 145, 0.8);
            }
        """)
        
        # وضع الزر في الزاوية اليمنى السفلى
        self.scroll_to_top_btn.setParent(parent)
        self.scroll_to_top_btn.move(parent.width() - 60, parent.height() - 60)
        
        # إخفاء الزر في البداية
        self.scroll_to_top_btn.hide()
        
        # ربط الزر بالحدث
        self.scroll_to_top_btn.clicked.connect(self.scroll_to_top)
        
        # ربط حدث التمرير لإظهار/إخفاء الزر
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.toggle_scroll_button)
        
        # ربط حدث تغيير حجم النافذة لإعادة وضع الزر
        parent.resizeEvent = lambda event: self.reposition_scroll_button(parent)

    def scroll_to_top(self):
        """تمرير منطقة الرسائل إلى الأعلى"""
        self.scroll_area.verticalScrollBar().setValue(0)

    def toggle_scroll_button(self, value):
        """إظهار/إخفاء زر التمرير حسب موقع التمرير"""
        if value > 100:  # إظهار الزر عند التمرير لأسفل
            self.scroll_to_top_btn.show()
        else:
            self.scroll_to_top_btn.hide()

    def reposition_scroll_button(self, parent):
        """إعادة وضع زر التمرير عند تغيير حجم النافذة"""
        if hasattr(self, 'scroll_to_top_btn'):
            self.scroll_to_top_btn.move(parent.width() - 60, parent.height() - 60)

    def create_enhanced_input_area(self, layout):
        """إنشاء منطقة الإدخال المحسنة مع مقبض تغيير الحجم"""
        # حاوي عام لمنطقة الإدخال
        input_main_container = QWidget()
        input_main_layout = QVBoxLayout(input_main_container)
        input_main_layout.setContentsMargins(0, 0, 0, 0)
        input_main_layout.setSpacing(0)
        
        # مقبض تغيير الحجم
        self.resize_handle = QFrame()
        self.resize_handle.setFixedHeight(8)
        self.resize_handle.setCursor(Qt.SizeVerCursor)
        self.resize_handle.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 212, 170, 0.3);
                border-radius: 4px;
            }
            QFrame:hover {
                background-color: rgba(0, 212, 170, 0.6);
            }
        """)
        
        # متغيرات السحب
        self.dragging = False
        self.drag_start_pos = None
        self.initial_height = 140
        
        # ربط أحداث السحب
        self.resize_handle.mousePressEvent = self.start_resize
        self.resize_handle.mouseMoveEvent = self.do_resize
        self.resize_handle.mouseReleaseEvent = self.end_resize
        
        input_main_layout.addWidget(self.resize_handle)
        
        self.input_container = QFrame()
        self.input_container.setMinimumHeight(140)
        self.input_container.setMaximumHeight(400)
        self.input_container.setFrameStyle(QFrame.StyledPanel)
        self.input_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        input_layout = QVBoxLayout(self.input_container)
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(10)
        
        # شريط الأدوات
        toolbar = self.create_input_toolbar()
        input_layout.addWidget(toolbar)
        
        # منطقة الإدخال الرئيسية
        main_input_layout = QHBoxLayout()
        
        # حقل الإدخال المحسن
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("اكتب رسالتك هنا... (Enter للإرسال، Shift+Enter لسطر جديد)")
        self.message_input.setMinimumHeight(60)
        # سيتم تحديد الحد الأقصى ديناميكياً
        self.message_input.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.95);
                color: #333333;
                border: 2px solid rgba(76, 175, 80, 0.3);
                border-radius: 20px;
                padding: 12px 18px;
                font-size: 14px;
                font-family: 'Arial Unicode MS', 'Tahoma';
                font-weight: 500;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
                background-color: white;
            }
        """)
        
        # تطبيق فلتر الأحداث للتحكم في الإدخال
        self.message_input.installEventFilter(self)
        
        # ربط تحديث عداد الأحرف
        self.message_input.textChanged.connect(self.update_char_counter)
        
        # أزرار الإرسال والإجراءات
        buttons_container = self.create_input_buttons()
        
        main_input_layout.addWidget(self.message_input)
        main_input_layout.addWidget(buttons_container)
        
        input_layout.addLayout(main_input_layout)
        
        input_main_layout.addWidget(self.input_container)
        layout.addWidget(input_main_container)
        
    def start_resize(self, event):
        """بدء عملية تغيير الحجم"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.globalY()
            self.initial_height = self.input_container.height()
            
    def do_resize(self, event):
        """تنفيذ تغيير الحجم أثناء السحب"""
        if self.dragging and self.drag_start_pos is not None:
            delta = self.drag_start_pos - event.globalY()
            new_height = max(140, min(400, self.initial_height + delta))
            self.input_container.setFixedHeight(new_height)
            
            # تحديث حجم حقل الإدخال ديناميكياً
            # احتساب المساحة المتاحة (الارتفاع - الشريط العلوي - الهوامش)
            available_height = new_height - 60  # 60 للشريط العلوي والهوامش
            input_height = max(60, min(available_height, 200))
            self.message_input.setMaximumHeight(input_height)
            
    def end_resize(self, event):
        """إنهاء عملية تغيير الحجم"""
        self.dragging = False
        self.drag_start_pos = None

    def create_input_toolbar(self):
        """إنشاء شريط أدوات الإدخال"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(8)
        
        # أزرار سريعة
        quick_buttons = [
            ("🔍", "بحث في القرآن", self.quick_quran_search),
            ("📊", "تحليل نص", self.quick_text_analysis),
            ("🌐", "بحث الإنترنت", self.show_internet_search_dialog),
            ("📝", "تلخيص", self.quick_summarize)
        ]
        
        for icon, tooltip, callback in quick_buttons:
            btn = QPushButton(icon)
            btn.setFixedSize(35, 25)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(284, 109, 8, 0.2);
                    border: 1px solid rgba(284, 109, 8, 0.7);
                    border-radius: 12px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(248, 109, 6, 0.9);
                }
                QPushButton:pressed {
                    background-color: rgba(248, 185, 6, 0.9);
                }
            """)
            btn.clicked.connect(callback)
            toolbar_layout.addWidget(btn)
        
        toolbar_layout.addStretch()
        
        # عداد الأحرف
        self.char_counter = QLabel("0")
        self.char_counter.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 11px;
                padding: 2px 8px;
                background-color: #121823;
                border-radius: 10px;
            }
        """)
        toolbar_layout.addWidget(self.char_counter)
        
        return toolbar

    def create_input_buttons(self):
        """إنشاء أزرار منطقة الإدخال"""
        container = QWidget()
        container.setFixedWidth(120)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # زر الإرسال الرئيسي
        send_btn = QPushButton("إرسال")
        send_btn.setFixedHeight(40)
        send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #d75c01, stop:1 #f86d06);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #d75c01, stop:1 #f86d06);
            }
        """)
        send_btn.clicked.connect(self.send_message)
        
        # أزرار إضافية
        attachment_btn = QPushButton("📎")
        attachment_btn.setFixedSize(35, 30)
        attachment_btn.setToolTip("إرفاق ملف")
        attachment_btn.setStyleSheet("""
            QPushButton {
                       background-color: rgba(284, 109, 8, 0.2);
                    border: 1px solid rgba(284, 109, 8, 0.7);
                    border-radius: 12px;
                    font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 0.5);
            }
        """)
        attachment_btn.clicked.connect(self.attach_file)
        
        voice_btn = QPushButton("🎤")
        voice_btn.setFixedSize(35, 30)
        voice_btn.setToolTip("تسجيل صوتي")
        voice_btn.setStyleSheet(attachment_btn.styleSheet().replace("33, 150, 243", "255, 152, 0"))
        voice_btn.clicked.connect(self.voice_input)
        
        layout.addWidget(send_btn)
        
        buttons_row = QHBoxLayout()
        buttons_row.addWidget(attachment_btn)
        buttons_row.addWidget(voice_btn)
        layout.addLayout(buttons_row)
        
        return container

    def create_toolbar_button(self, icon, tooltip, callback):
        """إنشاء زر شريط الأدوات"""
        button = QPushButton(icon)
        button.setFixedSize(35, 35)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(76, 175, 80, 0.2);
                border: 1px solid rgba(76, 175, 80, 0.5);
                border-radius: 6px;
                font-size: 16px;
                color: #4CAF50;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.3);
                border-color: #4CAF50;
            }
            QPushButton:pressed {
                background-color: rgba(76, 175, 80, 0.4);
            }
        """)
        if callback:
            button.clicked.connect(callback)
        return button

    def create_sidebar_button(self, text, color=None):
        """إنشاء زر بدون خلفية للشريط الجانبي بحجم محسن"""
        button = QPushButton(text)
        button.setMinimumHeight(26)
        button.setMaximumWidth(250)
        
        # تغيير مؤشر الماوس في PyQt5
        button.setCursor(Qt.PointingHandCursor)
        
        button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 4px 6px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
                max-width: 250px;
            }
            QPushButton:hover {
                background: rgba(243, 109, 11, 0.3);
                color: #ffffff;
                border: 1px solid #f36d0b;
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        return button

    # === وظائف البحث في الإنترنت ===
    
    def perform_internet_search(self):
        """تنفيذ بحث الإنترنت"""
        query = self.search_input.text().strip()
        if not query:
            return
        
        # إضافة رسالة البحث للمحادثة
        self.add_message("user", f"🔍 بحث في الإنترنت: {query}")
        
        try:
            # استيراد Tavily client
            from tavily_search import TavilySearchClient
            
            # إظهار رسالة تحميل
            loading_message = self.add_message("assistant", "🔄 جاري البحث في الإنترنت...")
            
            # تنفيذ البحث
            client = TavilySearchClient()
            results = client.search(query, max_results=5)
            
            # حذف رسالة التحميل
            if loading_message and hasattr(loading_message, 'setParent'):
                loading_message.setParent(None)
            
            # تنسيق وعرض النتائج
            formatted_results = client.format_search_results(results)
            self.add_message("assistant", formatted_results)
            
            # مسح حقل البحث
            self.search_input.clear()
            
        except Exception as e:
            # حذف رسالة التحميل في حالة الخطأ
            if 'loading_message' in locals() and loading_message and hasattr(loading_message, 'setParent'):
                loading_message.setParent(None)
            
            error_msg = f"❌ خطأ في بحث الإنترنت: {str(e)}"
            self.add_message("assistant", error_msg)
            print(f"❌ خطأ في البحث: {e}")
    
    def show_internet_search_dialog(self):
        """عرض نافذة حوار البحث في الإنترنت"""
        dialog = InternetSearchDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            query = dialog.get_search_query()
            if query.strip():
                self.perform_direct_internet_search(query.strip())
    
    def perform_direct_internet_search(self, query):
        """تنفيذ بحث مباشر في الإنترنت"""
        # إضافة رسالة البحث للمحادثة
        self.add_message("user", f"🔍 بحث في الإنترنت: {query}")
        
        try:
            # استيراد Tavily client
            from tavily_search import TavilySearchClient
            
            # إظهار رسالة تحميل
            loading_message = self.add_message("assistant", "🔄 جاري البحث في الإنترنت...")
            
            # تنفيذ البحث
            client = TavilySearchClient()
            results = client.search(query, max_results=5)
            
            # حذف رسالة التحميل
            if loading_message and hasattr(loading_message, 'setParent'):
                loading_message.setParent(None)
            
            # تنسيق وعرض النتائج
            formatted_results = client.format_search_results(results)
            self.add_message("assistant", formatted_results)
            
        except Exception as e:
            # حذف رسالة التحميل في حالة الخطأ
            if 'loading_message' in locals() and loading_message and hasattr(loading_message, 'setParent'):
                loading_message.setParent(None)
            
            error_msg = f"❌ خطأ في بحث الإنترنت: {str(e)}"
            self.add_message("assistant", error_msg)
            print(f"❌ خطأ في البحث: {e}")
    
    def quick_internet_search(self):
        """بحث سريع في الإنترنت (متوافق مع السابق)"""
        self.show_internet_search_dialog()

    def create_toggle_button(self, text, initial_state=True):
        """إنشاء زر تبديل محسن"""
        button = QPushButton(text)
        button.setCheckable(True)
        button.setChecked(initial_state)
        button.setMinimumHeight(28)
        
        self.update_toggle_style(button)
        button.toggled.connect(lambda: self.update_toggle_style(button))
        
        return button

    def update_toggle_style(self, button):
        """تحديث نمط زر التبديل"""
        if button.isChecked():
            button.setStyleSheet("""
                QPushButton {
                    background-color:  #744444;
                    color: white;
                    border: 2px solid #771111;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    font-family: 'Arial Unicode MS', 'Tahoma';
                    text-align: left;
                    padding-left: 10px;
                }
            """)

    def create_status_indicators(self, layout):
        """إنشاء مؤشرات الحالة"""
        indicators_data = [
            ("📚", "قاعدة البيانات", "#4CAF50"),
            ("🤖", "OpenRouter", "#4CAF50"),
            ("🧠", "النموذج", "#4CAF50"),
            ("🌐", "الإنترنت", "#4CAF50")
        ]
        
        for icon, text, color in indicators_data:
            indicator = self.create_status_indicator(icon, text, color)
            layout.addWidget(indicator)

    def create_status_indicator(self, icon, text, color):
        """إنشاء مؤشر حالة واحد"""
        container = QWidget()
        container.setFixedHeight(28)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(6)
        
        # الأيقونة
        icon_label = QLabel(icon)
        icon_label.setFixedSize(18, 18)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 12px;")
        
        # النص
        text_label = QLabel(text)
        text_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        status_dot = QLabel("●")
        status_dot.setFixedSize(10, 10)
        status_dot.setAlignment(Qt.AlignCenter)
        status_dot.setStyleSheet(f"QLabel {{ color: {color}; font-size: 12px; }}")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        layout.addWidget(status_dot)
        
        # حفظ مرجع للنقطة لتحديث اللون لاحقاً
        container.status_dot = status_dot
        
        return container

    def add_welcome_message(self):
        """إضافة رسالة الترحيب"""
        welcome_text = """
🤖 **مرحباً! أنا مساعدك الذكي للقرآن الكريم المحسن**

يمكنني مساعدتك في:
- 🔍 البحث في القرآن الكريم
- 📊 تحليل النصوص العربية
- 🌐 البحث في الإنترنت
- 💬 الإجابة على أي سؤال
- 🖼️ تحليل ملفات SVG

**ميزات جديدة:**
- ✨ تحديد ونسخ النصوص بسهولة
- 🎨 واجهة محسنة وأكثر جمالاً
- 🔧 تحكم كامل في الإعدادات
- ⚡ أداء سريع ومحسن

**اكتب رسالتك وابدأ المحادثة!**
        """
        self.add_message("assistant", welcome_text.strip())

    def add_message(self, sender, message, save_to_history=True):
        """إضافة رسالة محسنة للمحادثة"""
        print(f"📝 إضافة رسالة من {sender}: {message[:50]}...")
        
        # حفظ في تاريخ المحادثات
        if save_to_history:
            self.conversation_history.append({
                "sender": sender, 
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
        
        # إنشاء فقاعة رسالة محسنة
        message_bubble = MessageBubble(sender, message)
        
        # إضافة الفقاعة قبل الـ stretch
        insert_index = self.messages_layout.count() - 1
        self.messages_layout.insertWidget(insert_index, message_bubble)
        
        # التمرير للأسفل
        QTimer.singleShot(100, self.scroll_to_bottom)
        
        # تحديث عداد الرسائل
        self.update_message_counter()
        
        # حفظ في تاريخ المحادثات إذا كان متوفراً
        if self.history_manager and save_to_history:
            try:
                self.history_manager.add_message(sender, message)
            except Exception as e:
                print(f"خطأ في حفظ الرسالة: {e}")

    def send_message(self):
        """إرسال رسالة محسن"""
        message = self.message_input.toPlainText().strip()
        if not message:
            return

        # إضافة للتاريخ المحلي للإدخال
        self.input_history.append(message)
        self.input_history_index = len(self.input_history)

        # إضافة رسالة المستخدم
        self.add_message("user", message)
        self.message_input.clear()

        # معالجة الرسالة
        QTimer.singleShot(100, lambda: self.process_message(message))

    def process_message(self, message):
        """معالجة الرسالة وإنتاج الرد"""
        try:
            # تشخيص مفصل
            print(f"🔍 حالة chat_manager: {self.chat_manager is not None}")
            if self.chat_manager:
                print(f"🔍 وجود get_response: {hasattr(self.chat_manager, 'get_response')}")
            
            if self.chat_manager and hasattr(self.chat_manager, 'get_response'):
                # استخدام مدير الشات إذا كان متاحاً
                print("🤖 استخدام OpenRouter...")
                response = self.chat_manager.get_response(message)
                self.add_message("assistant", response)
            else:
                # رد احتياطي محسن
                print("🔄 استخدام الرد الاحتياطي...")
                response = self.enhanced_fallback_response(message)
                self.add_message("assistant", response)
                
        except Exception as e:
            print(f"❌ خطأ في معالجة الرسالة: {e}")
            print(f"📊 نوع الخطأ: {type(e).__name__}")
            error_response = f"❌ حدث خطأ في معالجة طلبك: {str(e)}"
            self.add_message("assistant", error_response)

    def enhanced_fallback_response(self, message):
        """رد احتياطي محسن"""
        message_lower = message.lower()

        # تحيات بسيطة
        if any(word in message_lower for word in ['مرحبا', 'السلام', 'أهلا', 'hello', 'hi']):
            return "🤖 أهلاً وسهلاً! عذراً، الخدمة المتقدمة غير متاحة حالياً. يمكنك تجربة الأوامر السريعة من شريط الأدوات."

        # البحث في القرآن
        if any(word in message_lower for word in ['آية', 'سورة', 'قرآن', 'ابحث']):
            return self.search_quran_fallback(message)

        # طلبات التحليل
        if any(word in message_lower for word in ['تحليل', 'اشرح', 'وضح']):
            return f"📊 **طلب تحليل:** {message[:100]}...\n\n⚠️ عذراً، خدمة التحليل المتقدم غير متاحة حالياً. يمكنك استخدام الأزرار السريعة للوصول للميزات المتاحة."

        # رد عام
        return """
🤖 **عذراً، لم أتمكن من فهم طلبك بوضوح.**

💡 **اقتراحات:**
- استخدم الأزرار السريعة في شريط الأدوات
- جرب البحث في القرآن بكتابة "ابحث عن الفاتحة"
- تأكد من إعدادات الاتصال في الشريط الجانبي

⚙️ **تحقق من الإعدادات إذا كنت تواجه مشاكل في الاتصال.**
        """

    def search_quran_fallback(self, query):
        """بحث احتياطي في القرآن"""
        try:
            if 'الفاتحة' in query.lower():
                return """
🕌 **سورة الفاتحة:**

بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
الرَّحْمَٰنِ الرَّحِيمِ
مَالِكِ يَوْمِ الدِّينِ
إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ
اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ
صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ

📍 **ملاحظة:** هذا مثال توضيحي. للبحث المتقدم، تأكد من إعدادات قاعدة البيانات.
                """
            else:
                return f"""
🔍 **البحث عن:** {query}

⚠️ **عذراً، البحث المتقدم غير متاح حالياً.**

💡 **للحصول على نتائج أفضل:**
- تأكد من تفعيل قاعدة البيانات من الشريط الجانبي
- تحقق من إعدادات الاتصال
- جرب استخدام الأزرار السريعة

🔧 **يمكنك أيضاً تجربة البحث اليدوي في ملفات القرآن المحلية.**
                """
        except Exception as e:
            return f"❌ خطأ في البحث: {str(e)}"

    def scroll_to_bottom(self):
        """التمرير لأسفل المحادثة"""
        if hasattr(self, 'scroll_area'):
            scroll_bar = self.scroll_area.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())

    def update_message_counter(self):
        """تحديث عداد الرسائل"""
        try:
            if hasattr(self, 'message_counter'):
                count = len(self.conversation_history)
                self.message_counter.setText(f"{count} رسالة")
        except Exception as e:
            print(f"خطأ في تحديث عداد الرسائل: {e}")

    def update_char_counter(self):
        """تحديث عداد الأحرف"""
        if hasattr(self, 'char_counter'):
            char_count = len(self.message_input.toPlainText())
            self.char_counter.setText(str(char_count))
            
            # تغيير اللون حسب العدد
            if char_count > 1000:
                color = "#f44336"  # أحمر
            elif char_count > 500:
                color = "#FF9800"  # برتقالي
            else:
                color = "rgba(255, 255, 255, 0.7)"  # أبيض شفاف
                
            self.char_counter.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: 11px;
                    padding: 2px 8px;
                    background-color: #121823;
                    border-radius: 10px;
                }}
            """)

    def eventFilter(self, obj, event):
        """فلتر الأحداث للتحكم في مدخلات المستخدم"""
        if obj == self.message_input and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                if event.modifiers() & Qt.ShiftModifier:
                    return False  # يسمح بإدراج سطر جديد
                else:
                    self.send_message()
                    return True
            elif event.key() == Qt.Key_Up and event.modifiers() & Qt.ControlModifier:
                # استرجاع الرسالة السابقة
                self.navigate_input_history(-1)
                return True
            elif event.key() == Qt.Key_Down and event.modifiers() & Qt.ControlModifier:
                # الانتقال للرسالة التالية
                self.navigate_input_history(1)
                return True
                
        return super().eventFilter(obj, event)

    def navigate_input_history(self, direction):
        """التنقل في تاريخ الإدخال"""
        if not self.input_history:
            return
            
        self.input_history_index += direction
        
        if self.input_history_index < 0:
            self.input_history_index = 0
        elif self.input_history_index >= len(self.input_history):
            self.input_history_index = len(self.input_history)
            self.message_input.clear()
            return
            
        if 0 <= self.input_history_index < len(self.input_history):
            self.message_input.setText(self.input_history[self.input_history_index])

    def setup_shortcuts(self):
        """إعداد اختصارات لوحة المفاتيح"""
        # Ctrl+N - محادثة جديدة
        new_chat_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_chat_shortcut.activated.connect(self.start_new_chat)
        
        # Ctrl+H - عرض التاريخ
        history_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        history_shortcut.activated.connect(self.show_chat_history)
        
        # Ctrl+L - مسح المحادثة
        clear_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        clear_shortcut.activated.connect(self.clear_current_chat)
        
        # Ctrl+S - حفظ المحادثة
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.export_conversation)
        
        # Ctrl+T - تبديل الثيم
        theme_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        theme_shortcut.activated.connect(self.toggle_theme)
        
        # F1 - عرض المساعدة
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.show_help)
        
        # Ctrl+Shift+S - إخفاء/إظهار الشريط الجانبي
        sidebar_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        sidebar_shortcut.activated.connect(self.toggle_sidebar)

    def setup_ai_components(self):
        """إعداد مكونات الذكاء الاصطناعي"""
        try:
            print(f"🔍 OPENROUTER_AVAILABLE = {OPENROUTER_AVAILABLE}")
            if OPENROUTER_AVAILABLE:
                print("🔧 محاولة إعداد OpenRouter Chat Manager...")
                self.chat_manager = OpenRouterChatManager()
                print("✅ تم إعداد OpenRouter Chat Manager بنجاح")
                print(f"🔍 نوع chat_manager: {type(self.chat_manager)}")
                print(f"🔍 وجود get_response: {hasattr(self.chat_manager, 'get_response')}")
                
                # اختبار توفر مفاتيح API
                if hasattr(self.chat_manager, 'current_api_key') and self.chat_manager.current_api_key:
                    print(f"🔑 مفتاح API متوفر: {self.chat_manager.current_api_key[:10]}...")
                else:
                    print("⚠️ مفتاح API غير متوفر")
                    
                # اختبار الاتصال السريع
                try:
                    models = self.chat_manager.get_available_models()
                    print(f"📋 تم تحميل {len(models)} نموذج مجاني")
                except Exception as model_error:
                    print(f"⚠️ خطأ في تحميل النماذج: {model_error}")
                    
            else:
                self.chat_manager = None
                print("⚠️ OpenRouter غير متوفر - مكتبات مفقودة")
                
        except Exception as e:
            print(f"❌ خطأ في إعداد مكونات الذكاء الاصطناعي: {e}")
            print(f"📊 تفاصيل الخطأ: {type(e).__name__}")
            import traceback
            print(f"📊 التفاصيل الكاملة: {traceback.format_exc()}")
            self.chat_manager = None

    def process_message(self, message):
        """معالجة الرسالة وإنتاج الرد"""
        try:
            # تشخيص مفصل
            print(f"🔍 حالة chat_manager: {self.chat_manager is not None}")
            if self.chat_manager:
                print(f"🔍 وجود get_response: {hasattr(self.chat_manager, 'get_response')}")
            
            if self.chat_manager and hasattr(self.chat_manager, 'get_response'):
                # استخدام مدير الشات إذا كان متاحاً
                print("🤖 استخدام OpenRouter...")
                response = self.chat_manager.get_response(message)
                self.add_message("assistant", response)
            else:
                # رد احتياطي محسن
                print("🔄 استخدام الرد الاحتياطي...")
                response = self.enhanced_fallback_response(message)
                self.add_message("assistant", response)
                
        except Exception as e:
            print(f"❌ خطأ في معالجة الرسالة: {e}")
            print(f"📊 نوع الخطأ: {type(e).__name__}")
            error_response = f"❌ حدث خطأ في معالجة طلبك: {str(e)}"
            self.add_message("assistant", error_response)

    def load_models_to_selector(self):
        try:
            if hasattr(self, 'chat_manager') and self.chat_manager:
                models = self.chat_manager.get_available_models()
            else:
                # تحميل مباشر من بيانات النماذج المجانية
                models = self._load_fallback_free_models()
            
            # إضافة النماذج للقائمة
            self.model_selector.clear()
            for model_id, info in models.items():
                vendor = info.get('vendor', info['name'].split(':')[0] if ':' in info['name'] else 'OpenRouter')
                display_text = f"{info['name']} ({vendor})"
                self.model_selector.addItem(display_text, model_id)
            
            # تعيين النموذج الافتراضي وتحديث الواجهة
            if self.model_selector.count() > 0:
                # تعيين أول نموذج كافتراضي
                self.model_selector.setCurrentIndex(0)
                # تحديث شريط المعلومات فوراً
                self.update_model_display()
                
            print(f"✅ تم تحميل {len(models)} نموذج إلى القائمة")
            
        except Exception as e:
            print(f"❌ خطأ في تحميل النماذج: {e}")
            self.model_selector.addItem("Qwen3 4B (Qwen)", "qwen/qwen3-4b:free")
            self.update_model_display()
    
    def _load_fallback_free_models(self) -> dict:
        """تحميل النماذج المجانية كنسخة احتياطية - مرتبة حسب الموثوقية"""
        # نفس قائمة النماذج المجانية من openrouter_chat_manager
        # مرتبة بحيث النماذج الموثوقة والتي تعمل تأتي أولاً
        free_models_data = [
            # النماذج الموثوقة التي تعمل بشكل جيد
            {"model_id": "qwen/qwen3-4b:free", "name": "Qwen: Qwen3 4B", "context": 40960},
            {"model_id": "qwen/qwen3-8b:free", "name": "Qwen: Qwen3 8B", "context": 40960},
            {"model_id": "qwen/qwen3-14b:free", "name": "Qwen: Qwen3 14B", "context": 40960},
            {"model_id": "meta-llama/llama-3.2-3b-instruct:free", "name": "Meta: Llama 3.2 3B Instruct", "context": 131072},
            {"model_id": "meta-llama/llama-3.3-8b-instruct:free", "name": "Meta: Llama 3.3 8B Instruct", "context": 128000},
            {"model_id": "mistralai/mistral-7b-instruct:free", "name": "Mistral: Mistral 7B Instruct", "context": 32768},
            {"model_id": "mistralai/mistral-nemo:free", "name": "Mistral: Mistral Nemo", "context": 131072},
            # النماذج المتقدمة (قد تكون أبطأ)
            {"model_id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Meta: Llama 3.3 70B Instruct", "context": 65536},
            {"model_id": "deepseek/deepseek-r1:free", "name": "DeepSeek: R1", "context": 163840},
            {"model_id": "deepseek/deepseek-r1-0528:free", "name": "DeepSeek: R1 0528", "context": 163840},
            {"model_id": "qwen/qwen2.5-72b-instruct:free", "name": "Qwen2.5 72B Instruct", "context": 32768},
            # النماذج التجريبية
            {"model_id": "google/gemini-2.0-flash-exp:free", "name": "Google: Gemini 2.0 Flash Experimental", "context": 1048576},
            {"model_id": "x-ai/grok-4-fast:free", "name": "xAI: Grok 4 Fast", "context": 2000000},
            # باقي النماذج
            {"model_id": "deepseek/deepseek-chat-v3-0324:free", "name": "DeepSeek: DeepSeek V3 0324", "context": 163840},
            {"model_id": "tngtech/deepseek-r1t2-chimera:free", "name": "TNG: DeepSeek R1T2 Chimera", "context": 163840},
            {"model_id": "z-ai/glm-4.5-air:free", "name": "Z.AI: GLM 4.5 Air", "context": 131072},
            {"model_id": "qwen/qwen3-coder:free", "name": "Qwen: Qwen3 Coder 480B A35B", "context": 262144},
            {"model_id": "tngtech/deepseek-r1t-chimera:free", "name": "TNG: DeepSeek R1T Chimera", "context": 163840},
            {"model_id": "qwen/qwen3-235b-a22b:free", "name": "Qwen: Qwen3 235B A22B", "context": 131072},
            {"model_id": "moonshotai/kimi-k2:free", "name": "MoonshotAI: Kimi K2 0711", "context": 32768},
            {"model_id": "microsoft/mai-ds-r1:free", "name": "Microsoft: MAI DS R1", "context": 163840},
            {"model_id": "nvidia/nemotron-nano-9b-v2:free", "name": "NVIDIA: Nemotron Nano 9B V2", "context": 128000},
            {"model_id": "deepseek/deepseek-r1-distill-llama-70b:free", "name": "DeepSeek: R1 Distill Llama 70B", "context": 8192},
            {"model_id": "openai/gpt-oss-20b:free", "name": "OpenAI: gpt-oss-20b", "context": 131072},
            {"model_id": "mistralai/mistral-small-3.2-24b-instruct:free", "name": "Mistral: Mistral Small 3.2 24B", "context": 131072},
            {"model_id": "meta-llama/llama-4-maverick:free", "name": "Meta: Llama 4 Maverick", "context": 128000},
            {"model_id": "qwen/qwen2.5-vl-72b-instruct:free", "name": "Qwen: Qwen2.5 VL 72B Instruct", "context": 32768},
            {"model_id": "deepseek/deepseek-r1-0528-qwen3-8b:free", "name": "DeepSeek: Deepseek R1 0528 Qwen3 8B", "context": 131072},
            {"model_id": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free", "name": "Venice: Uncensored", "context": 32768},
            {"model_id": "meta-llama/llama-3.1-405b-instruct:free", "name": "Meta: Llama 3.1 405B Instruct", "context": 65536},
            {"model_id": "moonshotai/kimi-dev-72b:free", "name": "MoonshotAI: Kimi Dev 72B", "context": 131072},
            {"model_id": "qwen/qwen3-30b-a3b:free", "name": "Qwen: Qwen3 30B A3B", "context": 40960},
            {"model_id": "agentica-org/deepcoder-14b-preview:free", "name": "Agentica: Deepcoder 14B Preview", "context": 96000},
            {"model_id": "google/gemma-3-27b-it:free", "name": "Google: Gemma 3 27B", "context": 96000},
            {"model_id": "qwen/qwen-2.5-coder-32b-instruct:free", "name": "Qwen2.5 Coder 32B Instruct", "context": 32768},
            {"model_id": "meta-llama/llama-4-scout:free", "name": "Meta: Llama 4 Scout", "context": 128000},
            {"model_id": "mistralai/mistral-small-3.1-24b-instruct:free", "name": "Mistral: Mistral Small 3.1 24B", "context": 128000},
            {"model_id": "qwen/qwq-32b:free", "name": "Qwen: QwQ 32B", "context": 32768},
            {"model_id": "shisa-ai/shisa-v2-llama3.3-70b:free", "name": "Shisa AI: Shisa V2 Llama 3.3 70B", "context": 32768},
            {"model_id": "mistralai/devstral-small-2505:free", "name": "Mistral: Devstral Small 2505", "context": 32768},
            {"model_id": "qwen/qwen2.5-vl-32b-instruct:free", "name": "Qwen: Qwen2.5 VL 32B Instruct", "context": 8192},
            {"model_id": "cognitivecomputations/dolphin3.0-mistral-24b:free", "name": "Dolphin3.0 Mistral 24B", "context": 32768},
            {"model_id": "nousresearch/deephermes-3-llama-3-8b-preview:free", "name": "Nous: DeepHermes 3 Llama 3 8B Preview", "context": 131072},
            {"model_id": "moonshotai/kimi-vl-a3b-thinking:free", "name": "MoonshotAI: Kimi VL A3B Thinking", "context": 131072},
            {"model_id": "tencent/hunyuan-a13b-instruct:free", "name": "Tencent: Hunyuan A13B Instruct", "context": 32768},
            {"model_id": "google/gemma-3-12b-it:free", "name": "Google: Gemma 3 12B", "context": 32768},
            {"model_id": "mistralai/mistral-small-24b-instruct-2501:free", "name": "Mistral: Mistral Small 3", "context": 32768},
            {"model_id": "arliai/qwq-32b-arliai-rpr-v1:free", "name": "ArliAI: QwQ 32B RpR v1", "context": 32768},
            {"model_id": "google/gemma-2-9b-it:free", "name": "Google: Gemma 2 9B", "context": 8192},
            {"model_id": "google/gemma-3n-e2b-it:free", "name": "Google: Gemma 3n 2B", "context": 8192},
            {"model_id": "cognitivecomputations/dolphin3.0-r1-mistral-24b:free", "name": "Dolphin3.0 R1 Mistral 24B", "context": 32768},
            {"model_id": "google/gemma-3n-e4b-it:free", "name": "Google: Gemma 3n 4B", "context": 8192},
            {"model_id": "google/gemma-3-4b-it:free", "name": "Google: Gemma 3 4B", "context": 32768},
            # النماذج المحدثة الجديدة
            {"model_id": "deepseek/deepseek-chat-v3.1:free", "name": "DeepSeek: DeepSeek V3.1", "context": 163840}
        ]
        
        models = {}
        for model_data in free_models_data:
            model_id = model_data["model_id"]
            models[model_id] = {
                "name": model_data["name"],
                "vendor": model_data["name"].split(":")[0],
                "params": "Free Tier",
                "context": model_data["context"],
                "modalities": "text",
                "description": f"Free tier model - {model_data['context']} context window",
                "pricing_input": 0.0,
                "pricing_output": 0.0
            }
        
        return models

    def on_model_changed(self):
        """التعامل مع تغيير النموذج - محسن"""
        if hasattr(self, 'model_selector') and self.model_selector.currentData():
            selected_model = self.model_selector.currentData()
            selected_text = self.model_selector.currentText()
            
            print(f"🔄 تغيير النموذج إلى: {selected_model}")
            print(f"🔄 النص المعروض: {selected_text}")
            
            # تحديث مدير الشات إذا كان متاحاً
            if hasattr(self, 'chat_manager') and self.chat_manager:
                try:
                    self.chat_manager.set_model(selected_model)
                    print(f"✅ تم تعيين النموذج في مدير الشات")
                except Exception as e:
                    print(f"❌ خطأ في تعيين النموذج: {e}")
            
            # تحديث عرض النموذج في الواجهة
            self.update_model_display()
            
        else:
            print("⚠️ لا يوجد نموذج محدد أو القائمة فارغة")
            
    def update_model_display(self):
        """تحديث عرض النموذج في شريط المعلومات"""
        try:
            if hasattr(self, 'model_selector') and self.model_selector.currentData():
                selected_model = self.model_selector.currentData()
                selected_text = self.model_selector.currentText()
                
                # استخراج اسم النموذج المختصر
                if '(' in selected_text and ')' in selected_text:
                    # استخراج الاسم من النص المعروض
                    model_name = selected_text.split('(')[0].strip()
                else:
                    # استخراج من معرف النموذج
                    model_name = selected_model.split('/')[-1].split(':')[0]
                
                # تحديث شريط المعلومات
                if hasattr(self, 'current_model_label'):
                    self.current_model_label.setText(f"🤖 النموذج: {model_name}")
                    print(f"✅ تم تحديث عرض النموذج في الشريط: {model_name}")
                else:
                    print("⚠️ لم يتم العثور على current_model_label")
                
                # تحديث معلومات الاتصال في الشريط العلوي
                if hasattr(self, 'connection_info_model'):
                    self.connection_info_model.setText(model_name)
                elif hasattr(self, 'model_info'):
                    self.model_info.setText(model_name)
                
                # تحديث حالة الاتصال
                if hasattr(self, 'connection_status'):
                    self.connection_status.setText("✅ متصل")
                    self.connection_status.setStyleSheet("QLabel { color: #4CAF50; font-size: 12px; }")
                    
            else:
                # في حالة عدم وجود نموذج محدد
                if hasattr(self, 'current_model_label'):
                    self.current_model_label.setText("🤖 النموذج: غير محدد")
                print("⚠️ لا يوجد نموذج محدد للعرض")
                
        except Exception as e:
            print(f"❌ خطأ في تحديث عرض النموذج: {e}")
            if hasattr(self, 'current_model_label'):
                self.current_model_label.setText("🤖 النموذج: خطأ")
            if hasattr(self, 'connection_status'):
                self.connection_status.setText("❌ خطأ")
                self.connection_status.setStyleSheet("QLabel { color: #f44336; font-size: 12px; }")

    def load_current_conversation(self):
        """تحميل المحادثة الحالية من التاريخ"""
        try:
            if self.history_manager and hasattr(self.history_manager, 'get_current_session_messages'):
                messages = self.history_manager.get_current_session_messages()
                # مسح المحادثة الحالية قبل التحميل
                self.clear_messages_only()
                
                for message in messages:
                    if hasattr(message, 'role') and hasattr(message, 'content'):
                        self.add_message(message.role, message.content, save_to_history=False)

                if messages:
                    print(f"✅ تم تحميل {len(messages)} رسالة من الجلسة الحالية")
                else:
                    # إضافة رسالة ترحيب فقط إذا لم توجد رسائل
                    self.add_welcome_message()
            else:
                print("⚠️ مدير التاريخ غير متوفر - بدء بمحادثة فارغة")
                self.add_welcome_message()
        except Exception as e:
            print(f"❌ خطأ في تحميل المحادثة: {e}")
            self.add_welcome_message()

    # === وظائف الأزرار والتحكم ===
    
    def start_new_chat(self):
        """بدء محادثة جديدة"""
        try:
            if self.history_manager:
                self.history_manager.create_new_session()
            
            self.clear_current_chat()
            self.add_welcome_message()
            print("✅ تم بدء محادثة جديدة")
        except Exception as e:
            print(f"❌ خطأ في بدء محادثة جديدة: {e}")

    def clear_messages_only(self):
        """مسح الرسائل فقط بدون مسح التاريخ"""
        try:
            # مسح واجهة الرسائل
            for i in reversed(range(self.messages_layout.count())):
                child = self.messages_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
            
            # مسح قائمة الرسائل
            self.conversation_history.clear()
        except Exception as e:
            print(f"❌ خطأ في مسح الرسائل: {e}")

    def clear_current_chat(self):
        """مسح المحادثة الحالية"""
        try:
            self.clear_messages_only()
            print("✅ تم مسح المحادثة")
        except Exception as e:
            print(f"❌ خطأ في مسح المحادثة: {e}")

    def show_chat_history(self):
        """عرض سجل المحادثات"""
        if self.history_manager:
            try:
                from chat_components import ChatHistoryDialog
                dialog = ChatHistoryDialog(self, self.history_manager)
                if dialog.exec_() == QDialog.Accepted:
                    selected_session_id = dialog.get_selected_session()
                    if selected_session_id:
                        self.history_manager.load_session(selected_session_id)
                        self.load_current_conversation()
            except Exception as e:
                print(f"❌ خطأ في عرض التاريخ: {e}")
        else:
            QMessageBox.information(self, "معلومات", "⚠️ مدير تاريخ المحادثات غير متوفر")

    def export_conversation(self):
        """تصدير المحادثة"""
        if not self.conversation_history:
            QMessageBox.information(self, "تنبيه", "لا توجد رسائل لتصديرها!")
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "تصدير المحادثة",
                f"محادثة_{timestamp}.txt",
                "Text Files (*.txt);;JSON Files (*.json);;All Files (*)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    if filename.endswith('.json'):
                        json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
                    else:
                        f.write(f"محادثة مُصدَّرة - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("="*50 + "\n\n")
                        
                        for msg in self.conversation_history:
                            sender = "المستخدم" if msg["sender"] == "user" else "المساعد"
                            f.write(f"[{sender}]: {msg['message']}\n\n")
                
                QMessageBox.information(self, "نجح", f"تم تصدير المحادثة إلى:\n{filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تصدير المحادثة:\n{str(e)}")

    def manage_instruction_file(self, index):
        """إدارة ملف التعليمات"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"إدارة ملف التعليمات {index + 1}")
            dialog.setModal(True)
            dialog.resize(600, 500)
            
            layout = QVBoxLayout(dialog)
            
            # معلومات الملف الحالي
            current_info = QLabel()
            if self.instruction_files[index]["file"]:
                current_info.setText(f"الملف الحالي: {os.path.basename(self.instruction_files[index]['file'])}")
            else:
                current_info.setText(NO_FILE_SELECTED)
            layout.addWidget(current_info)
            
            # أزرار التحكم
            buttons_layout = QHBoxLayout()
            
            select_btn = QPushButton("📁 اختيار ملف")
            select_btn.clicked.connect(lambda: self.select_instruction_file(index, current_info))
            
            remove_btn = QPushButton("🗑️ إزالة الملف")
            remove_btn.clicked.connect(lambda: self.remove_instruction_file(index, current_info))
            
            buttons_layout.addWidget(select_btn)
            buttons_layout.addWidget(remove_btn)
            layout.addLayout(buttons_layout)
            
            # معاينة المحتوى
            preview_group = QGroupBox("معاينة المحتوى")
            preview_layout = QVBoxLayout(preview_group)
            
            preview_text = QTextBrowser()
            preview_text.setMaximumHeight(200)
            
            if self.instruction_files[index]["file"]:
                try:
                    with open(self.instruction_files[index]["file"], 'r', encoding='utf-8') as f:
                        content = f.read()[:5000]  # أول 5000 حرف
                        preview_text.setPlainText(content)
                except Exception as e:
                    preview_text.setPlainText(f"خطأ في قراءة الملف: {str(e)}")
            else:
                preview_text.setPlainText(NO_FILE_SELECTED)
                
            preview_layout.addWidget(preview_text)
            layout.addWidget(preview_group)
            
            # أزرار الحفظ والإلغاء
            dialog_buttons = QHBoxLayout()
            ok_btn = QPushButton("✅ موافق")
            cancel_btn = QPushButton("❌ إلغاء")
            
            ok_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            dialog_buttons.addWidget(ok_btn)
            dialog_buttons.addWidget(cancel_btn)
            layout.addLayout(dialog_buttons)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ في إدارة ملف التعليمات:\n{str(e)}")

    def select_instruction_file(self, index, info_label):
        """اختيار ملف التعليمات"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "اختيار ملف التعليمات",
                "",
                "Text Files (*.txt);;Markdown Files (*.md);;All Files (*)"
            )
            
            if file_path:
                self.instruction_files[index]["file"] = file_path
                info_label.setText(f"الملف الحالي: {os.path.basename(file_path)}")
                
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في اختيار الملف: {str(e)}")

    def remove_instruction_file(self, index, info_label):
        """إزالة ملف التعليمات"""
        self.instruction_files[index]["file"] = None
        info_label.setText(NO_FILE_SELECTED)

    # === وظائف الأزرار السريعة ===
    
    def quick_quran_search(self):
        """بحث سريع في القرآن"""
        text = self.message_input.toPlainText()
        if text:
            self.message_input.setText(f"ابحث في القرآن عن: {text}")
        else:
            self.message_input.setText("ابحث في القرآن عن: ")
        self.message_input.setFocus()

    def quick_text_analysis(self):
        """تحليل نص سريع"""
        text = self.message_input.toPlainText()
        if text:
            self.message_input.setText(f"حلل هذا النص: {text}")
        else:
            self.message_input.setText("حلل هذا النص: ")
        self.message_input.setFocus()

    def quick_summarize(self):
        """تلخيص سريع"""
        text = self.message_input.toPlainText()
        if text:
            self.message_input.setText(f"لخص هذا النص: {text}")
        else:
            self.message_input.setText("لخص هذا النص: ")
        self.message_input.setFocus()

    def attach_file(self):
        """إرفاق ملف"""
        QMessageBox.information(self, "قريباً", "🔧 وظيفة إرفاق الملفات قيد التطوير")

    def voice_input(self):
        """إدخال صوتي"""
        QMessageBox.information(self, "قريباً", "🎤 وظيفة الإدخال الصوتي قيد التطوير")

    # === وظائف الإعدادات والثيمات ===
    
    def toggle_theme(self):
        """تبديل الثيم"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()
        print(f"🎨 تم تبديل الثيم إلى: {self.current_theme}")

    def apply_theme(self):
        """تطبيق الثيم المحدد"""
        if self.current_theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self):
        """تطبيق الثيم المظلم المحدث"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #222223;
                color: #ffffff;
                font-family: '{self.font_family}';
                font-size: {self.font_size}px;
            }}
            QFrame {{
                background-color: #333333;
            }}
            QGroupBox {{
                background-color: transparent;
                font-weight: bold;
                color: #ffffff;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #f36d0b;
            }}
            QWidget {{
                background-color: #222;
                color: #ffffff;
                font-family: '{self.font_family}';
                font-size: {self.font_size}px;
            }}
        """)

    def apply_light_theme(self):
        """تطبيق الثيم الفاتح"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f5f5f5;
                color: #333333;
                font-family: '{self.font_family}';
                font-size: {self.font_size}px;
            }}
            QFrame {{
                background-color: #ffffff;
            }}
            QGroupBox {{
                background-color: #ffffff;
            }}
            QWidget {{
                background-color: #f5f5f5;
                color: #333333;
                font-family: '{self.font_family}';
                font-size: {self.font_size}px;
            }}
        """)

    def apply_global_styles(self):
        """تطبيق الستايل العام"""
        self.apply_theme()

    def show_font_settings(self):
        """عرض إعدادات الخط"""
        dialog = FontSettingsDialog(self, self.font_size, self.font_family)
        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_font_settings()
            self.font_size = settings['size']
            self.font_family = settings['family']
            
            # تطبيق الإعدادات الجديدة
            self.apply_theme()
            print(f"🔤 تم تحديث إعدادات الخط: {self.font_family}, {self.font_size}px")

    def show_about_dialog(self):
        """عرض معلومات حول البرنامج"""
        about_text = f"""
🤖 **المساعد الذكي للقرآن الكريم - المحسن**

**الإصدار:** 2.0 المحسن
**المطور:** فريق التطوير
**التاريخ:** 2024

**الميزات:**
✨ واجهة محسنة وأكثر جمالاً
🔍 بحث متقدم في القرآن الكريم
📊 تحليل النصوص العربية
🌐 بحث في الإنترنت
💬 دعم الذكاء الاصطناعي
📋 تحديد ونسخ النصوص
🎨 ثيمات متعددة
⌨️ اختصارات لوحة المفاتيح
🔧 قائمة جانبية قابلة للإخفاء
📏 أحجام مرنة للواجهة

**الاختصارات:**
Ctrl+N - محادثة جديدة
Ctrl+H - سجل المحادثات
Ctrl+L - مسح المحادثة
Ctrl+S - حفظ المحادثة
Ctrl+T - تبديل الثيم
Ctrl+Shift+S - إخفاء/إظهار القائمة الجانبية
F1 - المساعدة

**الخط الحالي:** {self.font_family} - {self.font_size}px
**الثيم الحالي:** {self.current_theme}
        """
        QMessageBox.about(self, "حول البرنامج", about_text)

    def show_help(self):
        """عرض المساعدة"""
        help_text = """
📖 **مساعدة المساعد الذكي**

**كيفية الاستخدام:**
1. اكتب رسالتك في الحقل السفلي
2. اضغط Enter للإرسال أو Shift+Enter لسطر جديد
3. استخدم الأزرار السريعة للوصول لميزات معينة
4. انقر بالزر الأيمن على النصوص لنسخها

**الأزرار السريعة:**
🔍 - بحث في القرآن
📊 - تحليل نص
🌐 - بحث الإنترنت
📝 - تلخيص

**القائمة الجانبية:**
- يمكن إخفاؤها/إظهارها بالزر ◀/▶
- قابلة لتغيير العرض بالسحب
- تحتوي على جميع الإعدادات والتحكم

**تغيير حجم منطقة الإدخال:**
- استخدم المقبض الأزرق فوق منطقة الإدخال
- اسحب لأعلى أو لأسفل لتغيير الحجم

**نصائح:**
- استخدم Ctrl+↑/↓ للتنقل في تاريخ الرسائل
- يمكنك تحديد ونسخ أي نص في المحادثة
- استخدم الشريط الجانبي لتخصيص الإعدادات
- جرب تغيير حجم الخط من إعدادات الخط
        """
        QMessageBox.information(self, "المساعدة", help_text)

    def adjust_color(self, color, amount):
        """تعديل لون بزيادة أو تقليل السطوع"""
        # تحويل بسيط للون - يمكن تحسينه لاحقاً
        if color.startswith('#'):
            return color  # إرجاع اللون كما هو للتبسيط
        return color

    def resizeEvent(self, event):
        """التعامل مع تغيير حجم النافذة"""
        super().resizeEvent(event)
        # إعادة وضع زر التمرير إذا كان موجوداً
        if hasattr(self, 'scroll_to_top_btn'):
            parent = self.scroll_to_top_btn.parent()
            if parent:
                self.reposition_scroll_button(parent)

# === الدوال المساعدة ===

def get_theme_settings(theme_name):
    """الحصول على إعدادات الثيم"""
    themes = {
        'dark': {
            'name': 'المظلم',
            'background_color': '#1e1e1e',
            'secondary_bg': '#2d2d2d',
            'text_color': '#ffffff',
            'highlight_color': '#4CAF50',
            'hover_color': '#202020',
            'border_color': '#555555'
        },
        'light': {
            'name': 'الفاتح',
            'background_color': '#f5f5f5',
            'secondary_bg': '#ffffff',
            'text_color': '#333333',
            'highlight_color': '#2196F3',
            'hover_color': '#1976D2',
            'border_color': '#cccccc'
        }
    }
    return themes.get(theme_name, themes['dark'])

def create_stylesheet(theme, font_family, font_size):
    """إنشاء stylesheet محسن"""
    theme_settings = get_theme_settings(theme)
    
    return f"""
        QMainWindow {{
            background-color: {theme_settings['background_color']};
            color: {theme_settings['text_color']};
            font-family: '{font_family}';
            font-size: {font_size}px;
        }}
    """

def get_font_family(font_name):
    """الحصول على اسم عائلة الخط"""
    fonts = {
        'arabic_uthmani': 'Arial Unicode MS',
        'tahoma': 'Tahoma',
        'arial': 'Arial'
    }
    return fonts.get(font_name, 'Arial Unicode MS')

def get_font_size(size_name):
    """الحصول على حجم الخط"""
    sizes = {
        'small': 12,
        'medium': 14,
        'large': 16,
        'xlarge': 18
    }
    return sizes.get(size_name, 14) if isinstance(size_name, str) else size_name

# === نقطة الدخول ===

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # تطبيق ستايل عام للتطبيق
    app.setStyle('Fusion')
    
    # إنشاء النافذة
    window = ProfessionalChatWindow()
    window.show()
    
    sys.exit(app.exec_())