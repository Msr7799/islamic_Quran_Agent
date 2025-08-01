#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مكونات الشات والمحادثات الذكية
Chat components and intelligent conversation interfaces
"""

from shared_imports import *
from data_models import SimpleTextProcessor


class ChatHistoryDialog(QDialog):
    """نافذة قائمة المحادثات السابقة"""

    def __init__(self, parent, history_manager):
        super().__init__(parent)
        self.history_manager = history_manager
        self.selected_session_id = None
        self.setup_ui()
        self.load_sessions()

    def setup_ui(self):
        """إعداد واجهة النافذة"""
        self.setWindowTitle("📋 قائمة المحادثات")
        self.setFixedSize(600, 500)
        self.setModal(True)

        # التخطيط الرئيسي
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # العنوان
        title = QLabel("📋 المحادثات السابقة")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #212121;
                font-family: 'Arial Unicode MS', 'Tahoma';
                padding: 10px 0;
            }
        """)
        layout.addWidget(title)

        # قائمة المحادثات
        self.sessions_list = QListWidget()
        self.sessions_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 10px;
                background-color: white;
                font-family: 'Arial Unicode MS', 'Tahoma';
                font-size: 14px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #5994A4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        self.sessions_list.itemDoubleClicked.connect(self.on_session_double_clicked)
        layout.addWidget(self.sessions_list)

        # أزرار التحكم
        buttons_layout = QHBoxLayout()

        # زر تحميل
        load_btn = QPushButton("📂 تحميل المحادثة")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #5994A4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
            QPushButton:hover {
                background-color: #4a7c8a;
            }
        """)
        load_btn.clicked.connect(self.load_selected_session)
        buttons_layout.addWidget(load_btn)

        # زر حذف
        delete_btn = QPushButton("🗑️ حذف المحادثة")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF3A45;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
            QPushButton:hover {
                background-color: #e63946;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected_session)
        buttons_layout.addWidget(delete_btn)

        buttons_layout.addStretch()

        # زر إلغاء
        cancel_btn = QPushButton("❌ إلغاء")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def load_sessions(self):
        """تحميل قائمة الجلسات"""
        sessions = self.history_manager.get_all_sessions()

        self.sessions_list.clear()

        for session in sessions:
            # تنسيق التاريخ
            try:
                from datetime import datetime
                created_date = datetime.fromisoformat(session['created_at']).strftime('%Y-%m-%d %H:%M')
                updated_date = datetime.fromisoformat(session['updated_at']).strftime('%Y-%m-%d %H:%M')
            except:
                created_date = session['created_at'][:16]
                updated_date = session['updated_at'][:16]

            # إنشاء عنصر القائمة
            item_text = f"""
📝 {session['title']}
📅 تم الإنشاء: {created_date}
🔄 آخر تحديث: {updated_date}
💬 عدد الرسائل: {session['message_count']}
            """.strip()

            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, session['session_id'])

            # تلوين العنصر الحالي
            if session['session_id'] == self.history_manager.current_session_id:
                item.setBackground(QColor('#C0E8C1'))
                item.setText(f"🟢 {item_text}")

            self.sessions_list.addItem(item)

    def on_session_double_clicked(self, item):
        """عند النقر المزدوج على جلسة"""
        self.selected_session_id = item.data(Qt.UserRole)
        self.accept()

    def load_selected_session(self):
        """تحميل الجلسة المحددة"""
        current_item = self.sessions_list.currentItem()
        if current_item:
            self.selected_session_id = current_item.data(Qt.UserRole)
            self.accept()
        else:
            QMessageBox.information(self, WARNING_TITLE, "يرجى اختيار محادثة أولاً")

    def delete_selected_session(self):
        """حذف الجلسة المحددة"""
        current_item = self.sessions_list.currentItem()
        if not current_item:
            QMessageBox.information(self, WARNING_TITLE, "يرجى اختيار محادثة أولاً")
            return

        session_id = current_item.data(Qt.UserRole)

        # تأكيد الحذف
        reply = QMessageBox.question(
            self,
            "تأكيد الحذف",
            "هل أنت متأكد من حذف هذه المحادثة؟\nلا يمكن التراجع عن هذا الإجراء.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.history_manager.delete_session(session_id):
                QMessageBox.information(self, "نجح", "تم حذف المحادثة بنجاح")
                self.load_sessions()  # إعادة تحميل القائمة
            else:
                QMessageBox.warning(self, "خطأ", "فشل في حذف المحادثة")

    def get_selected_session(self):
        """الحصول على الجلسة المحددة"""
        return self.selected_session_id


class ProfessionalChatWindow(QMainWindow):
    """نافذة الشات الاحترافية المنفصلة"""

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

    # باقي الدوال ستكون في الجزء الثاني لتجنب إنشاء ملف واحد كبير جداً
