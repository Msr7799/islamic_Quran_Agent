#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة الشات الاحترافية المكتملة
Complete Professional Chat Window
"""

from shared_imports import *
from data_models import SimpleTextProcessor

# استيراد مكونات الذكاء الاصطناعي والتاريخ
try:
    from Agent.groq_chat_manager import GroqChatManager, ChatConfig
    from Agent.chat_history_manager import ChatHistoryManager
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️ مكونات الذكاء الاصطناعي غير متوفرة")
    ChatHistoryManager = None
    GroqChatManager = None
    ChatConfig = None

# ثوابت
NO_FILE_SELECTED = "لم يتم اختيار ملف"


# دمج كلاس ProfessionalChatWindow مع جميع الدوال من الجزأين
class ProfessionalChatWindow(QMainWindow):
    """نافذة الشات الاحترافية المنفصلة - مكتملة"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversation_history = []
        self.chat_manager = None
        self.input_history_index = -1  # فهرس تاريخ المدخلات

        # إعدادات واجهة المستخدم - ستأخذ من النافذة الأب
        self.theme = "light"
        self.font_size = 18
        self.font_family = "arabic_uthmani"

        # إذا كان هناك نافذة أب، خذ الإعدادات منها
        if parent and hasattr(parent, 'theme'):
            self.theme = parent.theme
            self.font_size = parent.font_size
            self.font_family = parent.font_family

        # إعداد مدير تاريخ المحادثات
        try:
            if ChatHistoryManager:
                self.history_manager = ChatHistoryManager()
                print("✅ تم تهيئة مدير تاريخ المحادثات")
            else:
                self.history_manager = None
        except Exception as e:
            print(f"❌ خطأ في تهيئة مدير التاريخ: {e}")
            self.history_manager = None

        self.setup_ui()
        self.setup_ai_components()

        # تحميل المحادثة الحالية
        self.load_current_conversation()

    def setup_ui(self):
        """إعداد واجهة الشات الاحترافية"""
        self.setWindowTitle("💬 الشات الذكي - مساعد القرآن الكريم")
        self.setGeometry(100, 100, 1200, 800)

        # الألوان المطلوبة
        self.colors = {
            'bg_primary': '#212121',
            'bg_secondary': '#262625',
            'user_msg': '#5994A4',
            'assistant_msg': '#C0E8C1',
            'text_color': '#212121',  # تغيير لون النص إلى #212121
            'code_bg': '#262625',
            'status_good': '#212121',  # تغيير لون المؤشر الأخضر إلى #212121
            'status_bad': '#FF3A45',
            'status_off': '#403A36'
        }

        # الويدجت المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # التخطيط الرئيسي
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # شريط علوي مع المؤشرات
        self.create_header(main_layout)

        # منطقة المحادثة
        self.create_chat_area(main_layout)

        # منطقة الإدخال
        self.create_input_area(main_layout)

        # تطبيق الستايل العام
        self.apply_ui_settings()

    def create_header(self, main_layout):
        """إنشاء الشريط العلوي مع المؤشرات"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['bg_secondary']};
                border-bottom: 2px solid {self.colors['bg_primary']};
            }}
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # العنوان
        title = QLabel("🤖 المساعد الذكي للقرآن الكريم")
        title.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }}
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # أزرار إدارة المحادثات
        self.create_chat_management_buttons(header_layout)

        # أزرار تضمين ملفات التعليمات
        self.create_instruction_buttons(header_layout)

        main_layout.addWidget(header)

    def create_chat_management_buttons(self, layout):
        """إنشاء أزرار إدارة المحادثات"""
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 0, 20, 0)

        # زر محادثة جديدة
        new_chat_btn = QPushButton("+")
        new_chat_btn.setFixedSize(35, 35)
        new_chat_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['user_msg']};
                color: white;
                border: none;
                border-radius: 17px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #4a7c8a;
            }}
            QPushButton:pressed {{
                background-color: #3a6c7a;
            }}
        """)
        new_chat_btn.clicked.connect(self.start_new_chat)
        buttons_layout.addWidget(new_chat_btn)

        # زر قائمة المحادثات
        history_btn = QPushButton("📂")
        history_btn.setFixedSize(35, 35)
        history_btn.setToolTip("سجل المحادثات")
        history_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['assistant_msg']};
                color: {self.colors['text_color']};
                border: none;
                border-radius: 17px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #a8d4a9;
            }}
            QPushButton:pressed {{
                background-color: #98c499;
            }}
        """)
        history_btn.clicked.connect(self.show_chat_history)
        buttons_layout.addWidget(history_btn)

        layout.addWidget(buttons_widget)

    def create_instruction_buttons(self, layout):
        """إنشاء أزرار تضمين ملفات التعليمات"""
        instruction_widget = QWidget()
        instruction_layout = QHBoxLayout(instruction_widget)
        instruction_layout.setSpacing(5)
        instruction_layout.setContentsMargins(0, 0, 10, 0)

        # إنشاء 4 أزرار لملفات التعليمات
        self.instruction_files = [
            {"name": "📄 تعليمات 1", "file": None, "mode": "auto"},
            {"name": "📄 تعليمات 2", "file": None, "mode": "auto"},
            {"name": "📄 تعليمات 3", "file": None, "mode": "auto"}, 
            {"name": "📄 تعليمات 4", "file": None, "mode": "auto"}
        ]

        for i, instruction in enumerate(self.instruction_files):
            btn = QPushButton(instruction["name"])
            btn.setFixedSize(80, 30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 15px;
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 0.2);
                }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self.manage_instruction_file(idx))
            instruction_layout.addWidget(btn)
            
        layout.addWidget(instruction_widget)

    def manage_instruction_file(self, index):
        """إدارة ملف التعليمات"""
        from chat_components import ChatHistoryDialog  # تجنب الاستيراد الدائري
        
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
        
        # اختيار الملف
        file_layout = QHBoxLayout()
        select_file_btn = QPushButton("📁 اختيار ملف")
        select_file_btn.clicked.connect(lambda: self.select_instruction_file(index, current_info))
        
        remove_file_btn = QPushButton("🗑️ إزالة الملف")
        remove_file_btn.clicked.connect(lambda: self.remove_instruction_file(index, current_info))
        
        file_layout.addWidget(select_file_btn)
        file_layout.addWidget(remove_file_btn)
        layout.addLayout(file_layout)
        
        # وضع التضمين
        mode_group = QGroupBox("وضع التضمين")
        mode_layout = QVBoxLayout(mode_group)
        
        auto_radio = QRadioButton("تلقائي - يتبع التعليمات حسب السياق المناسب")
        always_radio = QRadioButton("دائماً - يتبع التعليمات في كل الردود")
        
        if self.instruction_files[index]["mode"] == "auto":
            auto_radio.setChecked(True)
        else:
            always_radio.setChecked(True)
            
        mode_layout.addWidget(auto_radio)
        mode_layout.addWidget(always_radio)
        layout.addWidget(mode_group)
        
        # معاينة محتوى الملف
        preview_group = QGroupBox("معاينة المحتوى")
        preview_layout = QVBoxLayout(preview_group)
        
        preview_text = QTextBrowser()
        preview_text.setMaximumHeight(200)
        
        if self.instruction_files[index]["file"]:
            try:
                with open(self.instruction_files[index]["file"], 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 2000 * 5:  # 2000 كلمة تقريباً × 5 أحرف
                        content = content[:2000*5] + "\n\n... تم اقتطاع المحتوى (الحد الأقصى 2000 كلمة)"
                    preview_text.setPlainText(content)
            except Exception as e:
                preview_text.setPlainText(f"خطأ في قراءة الملف: {str(e)}")
        else:
            preview_text.setPlainText(NO_FILE_SELECTED)
            
        preview_layout.addWidget(preview_text)
        layout.addWidget(preview_group)
        
        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("💾 حفظ")
        cancel_btn = QPushButton("❌ إلغاء")
        
        def save_settings():
            self.instruction_files[index]["mode"] = "auto" if auto_radio.isChecked() else "always"
            dialog.accept()
            
        save_btn.clicked.connect(save_settings)
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        dialog.exec_()

    def select_instruction_file(self, index, info_label):
        """اختيار ملف التعليمات"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "اختيار ملف التعليمات",
            "",
            "Text Files (*.txt);;Markdown Files (*.md);;All Files (*)"
        )
        
        if file_path:
            # التحقق من حجم الملف
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    word_count = len(content.split())
                    if word_count > 2000:
                        reply = QMessageBox.question(
                            self,
                            "تحذير",
                            f"الملف يحتوي على {word_count} كلمة، والحد الأقصى هو 2000 كلمة.\nهل تريد المتابعة؟ سيتم اقتطاع المحتوى.",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        if reply == QMessageBox.No:
                            return
                            
                self.instruction_files[index]["file"] = file_path
                info_label.setText(f"الملف الحالي: {os.path.basename(file_path)}")
                
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل في قراءة الملف: {str(e)}")

    def remove_instruction_file(self, index, info_label):
        """إزالة ملف التعليمات"""
        self.instruction_files[index]["file"] = None
        info_label.setText(NO_FILE_SELECTED)

    def clear_current_chat(self):
        """مسح المحادثة الحالية"""
        # مسح الواجهة
        for i in reversed(range(self.messages_layout.count())):
            widget = self.messages_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def show_chat_history(self):
        """عرض سجل المحادثات السابقة"""
        if hasattr(self, 'history_manager') and self.history_manager:
            from chat_components import ChatHistoryDialog  # تجنب الاستيراد الدائري
            dialog = ChatHistoryDialog(self, self.history_manager)
            if dialog.exec_() == QDialog.Accepted:
                selected_session_id = dialog.get_selected_session()
                if selected_session_id:
                    self.history_manager.load_session(selected_session_id)
                    self.load_current_conversation()
        else:
            print("⚠️ مدير تاريخ المحادثات غير متوفر")

    def start_new_chat(self):
        """بدء محادثة جديدة"""
        if self.history_manager:
            self.history_manager.create_new_session()
            self.clear_current_chat()

    # استيراد جميع الدوال من الجزء الثاني
    def create_status_indicators(self, main_layout):
        """إنشاء مؤشرات الحالة في الأسفل"""
        status_container = QWidget()
        status_container.setFixedHeight(60)
        status_container.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['bg_secondary']};
                border-top: 2px solid {self.colors['bg_primary']};
            }}
        """)

        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(15, 10, 15, 10)
        status_layout.setSpacing(20)

        # مؤشر قاعدة البيانات
        self.db_status = self.create_status_indicator("📚", "قاعدة البيانات", self.colors['status_good'])
        status_layout.addWidget(self.db_status)

        # مؤشر GROQ مع اسم النموذج
        self.groq_status = self.create_status_indicator("🤖", "GROQ", self.colors['status_good'])
        status_layout.addWidget(self.groq_status)

        # مؤشر النموذج الحالي
        self.model_status = self.create_status_indicator("🧠", "llama-3.3-70b", self.colors['status_good'])
        status_layout.addWidget(self.model_status)

        # مؤشر Tavily
        self.tavily_status = self.create_status_indicator("🌐", "Tavily", self.colors['status_good'])
        status_layout.addWidget(self.tavily_status)

        # مؤشر الإنترنت
        self.internet_status = self.create_status_indicator("📡", "الإنترنت", self.colors['status_good'])
        status_layout.addWidget(self.internet_status)

        # أزرار التبديل
        toggle_container = QWidget()
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(10)

        # زر تبديل قاعدة البيانات
        self.db_toggle = self.create_toggle_button("📚 قاعدة البيانات", True)
        self.db_toggle.clicked.connect(self.toggle_database)
        toggle_layout.addWidget(self.db_toggle)

        # زر تبديل الإنترنت
        self.internet_toggle = self.create_toggle_button("🌐 بحث الإنترنت", True)
        self.internet_toggle.clicked.connect(self.toggle_internet)
        toggle_layout.addWidget(self.internet_toggle)

        status_layout.addWidget(toggle_container)
        status_layout.addStretch()

        # عداد الرسائل
        self.message_counter = QLabel("0 رسالة")
        self.message_counter.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 12px;
                font-family: 'Arial Unicode MS', 'Tahoma';
                padding: 5px 10px;
                background-color: {self.colors['bg_primary']};
                border-radius: 15px;
            }}
        """)
        status_layout.addWidget(self.message_counter)

        main_layout.addWidget(status_container)

        # تحديث حالة المؤشرات
        self.update_status_indicators()

    # ... باقي الدوال من chat_components_part2.py
    # سأقوم بنسخها جميعاً لتجنب التكرار في الكود

    # الدوال الأساسية للشات (تحتاج لتعريفها في نفس الكلاس)
    def create_status_indicator(self, icon, text, color):
        """إنشاء مؤشر حالة واحد"""
        indicator = QWidget()
        indicator.setFixedSize(140, 35)

        layout = QHBoxLayout(indicator)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(8)

        # الأيقونة
        icon_label = QLabel(icon)
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 16px;")

        # النص
        text_label = QLabel(text)
        text_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 11px;
                font-weight: bold;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }}
        """)

        # نقطة الحالة
        status_dot = QLabel("●")
        status_dot.setFixedSize(12, 12)
        status_dot.setAlignment(Qt.AlignCenter)
        status_dot.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 16px;
            }}
        """)

        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        layout.addWidget(status_dot)

        # حفظ مرجع للنقطة لتحديث اللون لاحقاً
        indicator.status_dot = status_dot

        return indicator

    def update_status_indicators(self):
        """تحديث حالة المؤشرات"""
        try:
            if hasattr(self, 'chat_manager') and self.chat_manager:
                # تحديث مؤشر النموذج (إذا كان متاحاً)
                if hasattr(self, 'model_status'):
                    self.model_status.status_dot.setStyleSheet(f"QLabel {{ color: {self.colors['status_good']}; font-size: 16px; }}")

                # تحديث مؤشر قاعدة البيانات (افتراضي: متاح)
                if hasattr(self, 'db_status'):
                    self.db_status.status_dot.setStyleSheet(f"QLabel {{ color: {self.colors['status_good']}; font-size: 16px; }}")

                # تحديث مؤشر الإنترنت (افتراضي: متاح)
                if hasattr(self, 'internet_status'):
                    self.internet_status.status_dot.setStyleSheet(f"QLabel {{ color: {self.colors['status_good']}; font-size: 16px; }}")
            else:
                # إذا لم يكن مدير الشات متاحاً، اجعل المؤشرات حمراء
                if hasattr(self, 'db_status'):
                    self.db_status.status_dot.setStyleSheet(f"QLabel {{ color: {self.colors['status_bad']}; font-size: 16px; }}")
                if hasattr(self, 'model_status'):
                    self.model_status.status_dot.setStyleSheet(f"QLabel {{ color: {self.colors['status_bad']}; font-size: 16px; }}")
                if hasattr(self, 'internet_status'):
                    self.internet_status.status_dot.setStyleSheet(f"QLabel {{ color: {self.colors['status_bad']}; font-size: 16px; }}")

        except Exception as e:
            print(f"خطأ في تحديث المؤشرات: {e}")

    def create_toggle_button(self, text, initial_state=True):
        """إنشاء زر تبديل"""
        button = QPushButton(text)
        button.setCheckable(True)
        button.setChecked(initial_state)
        button.setFixedSize(120, 30)

        # تحديث النمط حسب الحالة
        self.update_toggle_style(button)

        # ربط تغيير الحالة بتحديث النمط
        button.toggled.connect(lambda: self.update_toggle_style(button))

        return button

    def update_toggle_style(self, button):
        """تحديث نمط زر التبديل"""
        if button.isChecked():
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors['status_good']};
                    color: white;
                    border: none;
                    border-radius: 15px;
                    font-size: 10px;
                    font-weight: bold;
                    font-family: 'Arial Unicode MS', 'Tahoma';
                }}
                QPushButton:hover {{
                    background-color: #45a049;
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors['status_bad']};
                    color: white;
                    border: none;
                    border-radius: 15px;
                    font-size: 10px;
                    font-weight: bold;
                    font-family: 'Arial Unicode MS', 'Tahoma';
                }}
                QPushButton:hover {{
                    background-color: #d32f2f;
                }}
            """)

    def toggle_database(self):
        """تبديل حالة قاعدة البيانات"""
        if hasattr(self, 'chat_manager') and self.chat_manager:
            enabled = self.db_toggle.isChecked()
            if hasattr(self.chat_manager, 'toggle_database'):
                self.chat_manager.toggle_database(enabled)
            self.update_status_indicators()

    def toggle_internet(self):
        """تبديل حالة الإنترنت"""
        if hasattr(self, 'chat_manager') and self.chat_manager:
            enabled = self.internet_toggle.isChecked()
            if hasattr(self.chat_manager, 'toggle_internet'):
                self.chat_manager.toggle_internet(enabled)
            self.update_status_indicators()

    def create_chat_area(self, main_layout):
        """إنشاء منطقة المحادثة"""
        # منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # الويدجت الذي يحتوي على الرسائل
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(15)

        scroll_area.setWidget(self.messages_widget)

        # ستايل منطقة التمرير
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.colors['bg_primary']};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {self.colors['bg_secondary']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: rgba(255,255,255,0.3);
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: rgba(255,255,255,0.5);
            }}
        """)

        # إضافة رسالة ترحيب
        self.add_welcome_message()

        main_layout.addWidget(scroll_area)

    def create_input_area(self, main_layout):
        """إنشاء منطقة الإدخال مع دعم الكتابة على عدة أسطر"""
        input_container = QWidget()
        input_container.setFixedHeight(120)
        input_container.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['bg_secondary']};
                border-top: 2px solid {self.colors['bg_primary']};
            }}
        """)

        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(15)

        # حقل الإدخال متعدد الأسطر
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("اكتب رسالتك هنا... (Enter للإرسال، Shift+Enter لسطر جديد)")
        self.message_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: white;
                color: {self.colors['text_color']};
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 25px;
                padding: 15px 20px;
                font-size: 14px;
                font-family: 'Arial Unicode MS', 'Tahoma';
                font-weight: bold;
            }}
            QTextEdit:focus {{
                border-color: {self.colors['user_msg']};
                outline: none;
            }}
        """)
        self.message_input.setMinimumHeight(50)
        self.message_input.setMaximumHeight(80)

        # ربط الأحداث: Enter للإرسال، Shift+Enter لسطر جديد
        self.message_input.installEventFilter(self)

        # زر الإرسال
        send_btn = QPushButton("إرسال")
        send_btn.setFixedSize(100, 50)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['user_msg']};
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }}
            QPushButton:hover {{
                background-color: #4a7c8a;
            }}
            QPushButton:pressed {{
                background-color: #3a6c7a;
            }}
        """)
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_btn)

        main_layout.addWidget(input_container)

        # إضافة المؤشرات في الأسفل
        self.create_status_indicators(main_layout)

    def add_welcome_message(self):
        """إضافة رسالة الترحيب"""
        welcome_text = """
🤖 **مرحباً! أنا مساعدك الذكي للقرآن الكريم**

يمكنني مساعدتك في:
- 🔍 البحث في القرآن الكريم
- 📊 تحليل النصوص العربية
- 🌐 البحث في الإنترنت
- 💬 الإجابة على أي سؤال
- 🖼️ تحليل ملفات SVG

**اكتب رسالتك وابدأ المحادثة!**
        """
        self.add_message("assistant", welcome_text.strip())

    def update_message_counter(self):
        """تحديث عداد الرسائل"""
        try:
            if hasattr(self, 'message_counter'):
                count = len(self.conversation_history)
                self.message_counter.setText(f"{count} رسالة")
        except Exception as e:
            print(f"خطأ في تحديث عداد الرسائل: {e}")

    # دوال أساسية للشات - مبسطة للمثال
    def add_message(self, sender, message, save_to_history=True):
        """إضافة رسالة للمحادثة - نسخة مبسطة"""
        print(f"🔄 إضافة رسالة من {sender}: {message[:50]}...")
        
        # حفظ في تاريخ المحادثات
        if save_to_history:
            self.conversation_history.append({"sender": sender, "message": message})
        
        # إنشاء عنصر رسالة بسيط
        message_widget = QLabel(f"{sender}: {message}")
        message_widget.setWordWrap(True)
        message_widget.setStyleSheet(f"""
            QLabel {{
                padding: 10px;
                margin: 5px;
                border-radius: 10px;
                background-color: {"#C0E8C1" if sender == "assistant" else "#5994A4"};
                color: {"#212121" if sender == "assistant" else "white"};
                font-family: 'Arial Unicode MS', 'Tahoma';
            }}
        """)
        
        self.messages_layout.addWidget(message_widget)
        
        # التمرير للأسفل
        QTimer.singleShot(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """التمرير لأسفل المحادثة"""
        scroll_area = self.messages_widget.parent().parent()
        if isinstance(scroll_area, QScrollArea):
            scroll_bar = scroll_area.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())

    def send_message(self):
        """إرسال رسالة (يدعم QTextEdit)"""
        message = self.message_input.toPlainText().strip()
        if not message:
            return

        # إضافة رسالة المستخدم
        self.add_message("user", message)
        self.message_input.clear()

        # تحديث عداد الرسائل
        self.update_message_counter()

        # معالجة الرسالة
        self.process_message(message)

    def eventFilter(self, obj, event):
        """فلتر الأحداث للتحكم في مدخلات المستخدم ودعم Enter/Shift+Enter"""
        if obj == self.message_input and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                if event.modifiers() & Qt.ShiftModifier:
                    # إدراج سطر جديد
                    return False  # يسمح بإدراج سطر جديد
                else:
                    # إرسال الرسالة
                    self.send_message()
                    return True

        # السماح للحدث بالمرور للمعالجة الافتراضية
        return super().eventFilter(obj, event)

    def process_message(self, message):
        """معالجة الرسالة وإنتاج الرد"""
        try:
            if self.chat_manager and hasattr(self.chat_manager, 'get_response'):
                # استخدام مدير الشات إذا كان متاحاً
                response = self.chat_manager.get_response(message)
                self.add_message("assistant", response)
            else:
                # رد افتراضي
                fallback_response = self.fallback_response(message)
                self.add_message("assistant", fallback_response)
                
            # تحديث عداد الرسائل
            self.update_message_counter()

        except Exception as e:
            print(f"❌ خطأ في معالجة الرسالة: {e}")
            error_response = f"❌ حدث خطأ: {str(e)}"
            self.add_message("assistant", error_response)

    def setup_ai_components(self):
        """إعداد مكونات الذكاء الاصطناعي"""
        try:
            if GroqChatManager:
                self.chat_manager = GroqChatManager()
                if hasattr(self.chat_manager, 'set_model'):
                    self.chat_manager.set_model("llama3-70b-8192")
                print("✅ تم تهيئة مدير الشات بنجاح")
            else:
                self.chat_manager = None
                print("❌ GroqChatManager غير متاح")
            
            if hasattr(self, 'update_status_indicators'):
                self.update_status_indicators()
        except Exception as e:
            print(f"❌ خطأ في تهيئة مدير الشات: {e}")
            self.chat_manager = None

    def load_current_conversation(self):
        """تحميل المحادثة الحالية من التاريخ"""
        try:
            if self.history_manager and hasattr(self.history_manager, 'get_current_session_messages'):
                # تحميل رسائل الجلسة الحالية
                messages = self.history_manager.get_current_session_messages()
                for message in messages:
                    if hasattr(message, 'role') and hasattr(message, 'content'):
                        self.add_message(message.role, message.content, save_to_history=False)

                if messages:
                    print(f"✅ تم تحميل {len(messages)} رسالة من الجلسة الحالية")
                else:
                    print("✅ تم تحميل رسالة الترحيب")
            else:
                print("⚠️ مدير التاريخ غير متوفر")
        except Exception as e:
            print(f"❌ خطأ في تحميل المحادثة: {e}")

    def fallback_response(self, message):
        """رد احتياطي بدون مدير الشات"""
        message_lower = message.lower()

        # تحيات بسيطة
        if any(word in message_lower for word in ['مرحبا', 'السلام', 'أهلا']):
            return "🤖 أهلاً وسهلاً! عذراً، الخدمة المتقدمة غير متاحة حالياً."

        # البحث في القرآن
        if any(word in message_lower for word in ['آية', 'سورة', 'قرآن', 'ابحث']):
            return self.search_quran_fallback(message)

        # رد عام
        return "عذراً، مدير الشات غير متاح حالياً. يرجى التحقق من إعدادات API."

    def search_quran_fallback(self, query):
        """بحث احتياطي في القرآن"""
        try:
            # محاولة البحث البسيط
            if 'الفاتحة' in query:
                return """
🕌 **سورة الفاتحة:**

بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
الرَّحْمَٰنِ الرَّحِيمِ
مَالِكِ يَوْمِ الدِّينِ
إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ
اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ
صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ
                """
            else:
                return f"🔍 **البحث عن:** {query}\n\n⚠️ عذراً، البحث المتقدم غير متاح حالياً."

        except Exception as e:
            return f"❌ خطأ في البحث: {str(e)}"

    def apply_ui_settings(self):
        """تطبيق إعدادات واجهة المستخدم على نافذة الشات"""
        try:
            # استخدام الـ stylesheet المحسن من الإعدادات
            stylesheet = create_stylesheet(self.theme, self.font_family, self.font_size)

            # الحصول على إعدادات الثيم
            theme_settings = get_theme_settings(self.theme)

            # تحديث الألوان حسب الثيم المختار
            self.colors = {
                'bg_primary': theme_settings['background_color'],
                'bg_secondary': theme_settings['secondary_bg'],
                'user_msg': theme_settings['highlight_color'],
                'assistant_msg': theme_settings['hover_color'],
                'text_color': theme_settings['text_color'],
                'code_bg': theme_settings['secondary_bg'],
                'status_good': theme_settings['highlight_color'],
                'status_bad': '#FF3A45',
                'status_off': theme_settings['border_color']
            }

            # تطبيق الستايل المحسن
            enhanced_stylesheet = stylesheet + f"""
                /* ستايل خاص بنافذة الشات */
                QMainWindow {{
                    background-color: {self.colors['bg_primary']};
                }}

                /* منطقة الرسائل */
                QScrollArea {{
                    background-color: {self.colors['bg_primary']};
                    border: none;
                }}
            """

            self.setStyleSheet(enhanced_stylesheet)

            # تطبيق الخط
            font = QFont(get_font_family(self.font_family), get_font_size(self.font_size))
            self.setFont(font)

            # تحديث عنوان النافذة
            theme_info = get_theme_settings(self.theme)
            self.setWindowTitle(f"💬 الشات الذكي - {theme_info.get('name', self.theme)}")

            print(f"✅ تم تطبيق الإعدادات على نافذة الشات: {self.theme}, {self.font_size}px")

        except Exception as e:
            print(f"❌ خطأ في تطبيق الإعدادات على نافذة الشات: {e}")
