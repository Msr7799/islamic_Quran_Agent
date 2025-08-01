#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
النافذة الرئيسية لمحلل النصوص القرآنية
Main window for Quran Text Analyzer
"""

from shared_imports import *
from data_models import AyahInfo, TextAnalysisResult, SimpleTextProcessor
from analysis_widgets import CharacterAnalysisWidget, StatisticsWidget
from complete_chat_window import ProfessionalChatWindow
from svg_comparison_tools import SVGAnalyzerWidget, ComparisonWidget
from shared_constants import GUI_DATA_DIR


class CoordinateExtractorWidget(QWidget):
    """ويدجت استخراج الإحداثيات من صور SVG"""

    def __init__(self):
        super().__init__()
        self.svg_dir = "gui/Agent/pages_svgs"
        self.extracted_coordinates = []
        self.setup_ui()

    def setup_ui(self):
        """إعداد واجهة استخراج الإحداثيات"""
        layout = QVBoxLayout(self)

        # عنوان
        title = QLabel("📍 استخراج إحداثيات الآيات من SVG")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 15px;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        # منطقة الإعدادات
        settings_group = QGroupBox("إعدادات الاستخراج")
        settings_layout = QVBoxLayout(settings_group)

        # اختيار المجلد
        folder_layout = QHBoxLayout()
        
        self.folder_path_label = QLabel(f"مجلد الصور: {self.svg_dir}")
        self.folder_path_label.setStyleSheet("""
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            color: #495057;
        """)

        browse_folder_btn = QPushButton("📁 اختيار مجلد")
        browse_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        browse_folder_btn.clicked.connect(self.browse_svg_folder)

        folder_layout.addWidget(self.folder_path_label, 1)
        folder_layout.addWidget(browse_folder_btn)
        settings_layout.addLayout(folder_layout)

        # خيارات الاستخراج
        options_layout = QHBoxLayout()
        
        # نطاق الصفحات
        range_group = QGroupBox("نطاق الصفحات")
        range_layout = QHBoxLayout(range_group)
        
        range_layout.addWidget(QLabel("من:"))
        self.start_page = QSpinBox()
        self.start_page.setMinimum(1)
        self.start_page.setMaximum(604)
        self.start_page.setValue(1)
        
        range_layout.addWidget(self.start_page)
        range_layout.addWidget(QLabel("إلى:"))
        
        self.end_page = QSpinBox()
        self.end_page.setMinimum(1)
        self.end_page.setMaximum(604)
        self.end_page.setValue(10)
        
        range_layout.addWidget(self.end_page)
        options_layout.addWidget(range_group)

        # خيارات الاستخراج
        extract_options_group = QGroupBox("عناصر الاستخراج")
        extract_options_layout = QVBoxLayout(extract_options_group)
        
        self.extract_text_elements = QCheckBox("عناصر النص (<text>)")
        self.extract_text_elements.setChecked(True)
        
        self.extract_use_elements = QCheckBox("عناصر الاستخدام (<use>)")
        self.extract_use_elements.setChecked(True)
        
        self.extract_paths = QCheckBox("المسارات (<path>)")
        self.extract_paths.setChecked(False)
        
        extract_options_layout.addWidget(self.extract_text_elements)
        extract_options_layout.addWidget(self.extract_use_elements)
        extract_options_layout.addWidget(self.extract_paths)
        
        options_layout.addWidget(extract_options_group)
        settings_layout.addLayout(options_layout)

        layout.addWidget(settings_group)

        # شريط الحالة
        self.status_label = QLabel("جاهز لاستخراج الإحداثيات")
        self.status_label.setStyleSheet("""
            color: #6c757d;
            font-size: 12px;
            padding: 5px;
            background-color: #f8f9fa;
            border-radius: 3px;
        """)
        layout.addWidget(self.status_label)

    def browse_svg_folder(self):
        """اختيار مجلد صور SVG"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "اختيار مجلد صور SVG",
            self.svg_dir
        )
        
        if folder:
            self.svg_dir = folder
            self.folder_path_label.setText(f"مجلد الصور: {folder}")


class QuranTextAnalyzer(QMainWindow):
    """النافذة الرئيسية لتحليل النصوص القرآنية"""

    def __init__(self):
        super().__init__()

        # إعدادات واجهة المستخدم المحسنة للشاشات الكبيرة
        self.theme = "light"
        self.font_size = 18  # حجم بالبكسل مباشرة
        self.font_family = "arabic_uthmani"  # الخط العثماني كافتراضي

        # متغيرات البيانات
        self.hafs_data = None
        self.current_analysis = None
        self.professional_chat_window = None

        # تحميل الإعدادات المحفوظة
        self.load_saved_settings()

        # تطبيق إعدادات الواجهة
        self.apply_ui_settings()

        # إعداد واجهة المستخدم
        self.setup_ui()

    def apply_ui_settings(self):
        """تطبيق إعدادات واجهة المستخدم - مبسط"""
        try:
            # التحقق البسيط من الإعدادات
            if not self.validate_settings():
                self.reset_to_default_settings()

            # تطبيق الستايل
            stylesheet = create_stylesheet(self.theme, self.font_family, self.font_size)
            self.setStyleSheet(stylesheet)

            # تطبيق الخط
            font = QFont(get_font_family(self.font_family), get_font_size(self.font_size))
            self.setFont(font)

            # تحديث العنوان
            theme_info = get_theme_settings(self.theme)
            self.setWindowTitle(f"🕌 محلل النصوص القرآنية المتقدم - {theme_info.get('name', self.theme)}")

            print(f"✅ تم تطبيق الإعدادات: {self.theme}, {self.font_size}px, {self.font_family}")

        except Exception as e:
            print(f"❌ خطأ في تطبيق الإعدادات: {e}")
            # إعدادات افتراضية آمنة
            self.theme = "light"
            self.font_size = 18
            self.font_family = "arabic_uthmani"

    def validate_settings(self):
        """التحقق من صحة الإعدادات - مبسط"""
        try:
            # قائمة الثيمات المتاحة
            available_themes = ["light", "dark", "red_dark", "orange_light", "neon_dark", "auto", "blue_ocean", "purple_royal", "green_forest", "gold_luxury"]

            # التحقق من الثيم
            if self.theme not in available_themes:
                print(f"⚠️ ثيم غير صحيح: {self.theme}")
                return False

            # التحقق من حجم الخط
            if not isinstance(self.font_size, (int, float)) or self.font_size < 8 or self.font_size > 128:
                print(f"⚠️ حجم خط غير صحيح: {self.font_size}")
                return False

            # قائمة الخطوط المتاحة
            available_fonts = ["default", "arabic_uthmani", "arabic_uthmani_alt", "arabic_uthmani_simple", "arabic", "arabic_naskh", "arabic_kufi", "arabic_traditional", "arabic_modern", "english", "english_modern", "english_classic", "english_elegant", "monospace", "monospace_alt", "system_default"]

            # التحقق من نوع الخط
            if self.font_family not in available_fonts:
                print(f"⚠️ نوع خط غير صحيح: {self.font_family}")
                return False

            return True

        except Exception as e:
            print(f"❌ خطأ في التحقق من الإعدادات: {e}")
            return False

    def reset_to_default_settings(self):
        """إعادة تعيين الإعدادات للقيم الافتراضية الآمنة"""
        self.theme = "light"
        self.font_size = 18
        self.font_family = "arabic_uthmani"
        print("🔄 تم إعادة تعيين الإعدادات للقيم الافتراضية")

    def change_theme(self, theme):
        """تغيير الثيم"""
        self.theme = theme
        self.apply_ui_settings()

    def change_font_size(self, size):
        """تغيير حجم الخط"""
        self.font_size = size
        self.apply_ui_settings()

    def change_font_family(self, family):
        """تغيير نوع الخط"""
        self.font_family = family
        self.apply_ui_settings()

    def setup_ui(self):
        """إعداد واجهة المستخدم المحسنة"""
        # إعداد النافذة باستخدام الإعدادات المحسنة
        theme_info = get_theme_settings(self.theme)
        self.setWindowTitle(f"🕌 محلل النصوص القرآنية المتقدم - {theme_info.get('name', self.theme)}")

        # استخدام إعدادات النافذة من الملف
        self.setGeometry(
            100, 100,
            WINDOW_SETTINGS['default_width'],
            WINDOW_SETTINGS['default_height']
        )
        self.setMinimumSize(
            WINDOW_SETTINGS['min_width'],
            WINDOW_SETTINGS['min_height']
        )

        # جعل النافذة قابلة لتغيير الحجم بحرية (نظام Linux)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # القائمة الرئيسية
        self.create_menu()
        
        # الويدجت المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # التخطيط الرئيسي - responsive
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # منطقة الإدخال
        input_group = QGroupBox("إدخال النص للتحليل")
        input_layout = QVBoxLayout(input_group)
        
        # شريط أدوات الإدخال
        input_toolbar = QHBoxLayout()
        
        load_file_btn = QPushButton("📁 تحميل من ملف")
        load_file_btn.clicked.connect(self.load_text_from_file)
        
        load_ayah_btn = QPushButton("📖 تحميل آية")
        load_ayah_btn.clicked.connect(self.load_ayah_dialog)
        
        paste_btn = QPushButton("📋 لصق")
        paste_btn.clicked.connect(self.paste_text)

        # زر الشات الاحترافي
        chat_btn = QPushButton("💬 الشات الاحترافي")
        chat_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: linear-gradient(45deg, #5a6fd8, #6a4190);
            }
        """)
        chat_btn.clicked.connect(self.open_professional_chat)

        input_toolbar.addWidget(load_file_btn)
        input_toolbar.addWidget(load_ayah_btn)
        input_toolbar.addWidget(paste_btn)
        input_toolbar.addWidget(chat_btn)
        input_toolbar.addStretch()
        
        input_layout.addLayout(input_toolbar)
        
        # منطقة النص
        self.text_input = QTextEdit()
        self.text_input.setMaximumHeight(150)
        self.text_input.setStyleSheet("""
            QTextEdit {
                font-size: 18px;
                font-family: 'Arial Unicode MS', 'Tahoma';
                line-height: 1.8;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
        """)
        self.text_input.setPlaceholderText("أدخل النص القرآني هنا للتحليل...")
        
        input_layout.addWidget(self.text_input)
        
        # زر التحليل
        analyze_btn = QPushButton("🔍 تحليل النص")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_text)
        
        input_layout.addWidget(analyze_btn)
        
        main_layout.addWidget(input_group)
        
        # التبويبات
        self.tabs = QTabWidget()
        
        # تبويب تحليل الأحرف
        self.char_analysis_widget = CharacterAnalysisWidget()
        self.tabs.addTab(self.char_analysis_widget, "🔤 تحليل الأحرف")
        
        # تبويب الإحصائيات
        self.statistics_widget = StatisticsWidget()
        self.tabs.addTab(self.statistics_widget, "📊 الإحصائيات")
        
        # تبويب النتائج المفصلة
        self.results_widget = QTextBrowser()
        self.results_widget.setStyleSheet("""
            QTextBrowser {
                font-size: 14px;
                font-family: 'Arial Unicode MS', 'Tahoma';
                line-height: 1.6;
                padding: 15px;
            }
        """)
        self.tabs.addTab(self.results_widget, "📋 النتائج المفصلة")
        
        # تبويب مقارنة النصوص
        self.comparison_widget = ComparisonWidget()
        self.tabs.addTab(self.comparison_widget, "🔄 مقارنة النصوص")
        
        # تبويب تحليل SVG
        self.svg_analyzer_widget = SVGAnalyzerWidget()
        self.tabs.addTab(self.svg_analyzer_widget, "🖼️ تحليل SVG")
        
        # تبويب استخراج الإحداثيات
        self.coordinate_extractor_widget = CoordinateExtractorWidget()
        self.tabs.addTab(self.coordinate_extractor_widget, "📍 استخراج الإحداثيات")
        
        main_layout.addWidget(self.tabs)

        # تطبيق CSS للمرونة والاستجابة
        self.apply_responsive_styles()

        # شريط الحالة
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("جاهز للتحليل")

    def apply_responsive_styles(self):
        """تطبيق أنماط CSS للمرونة والاستجابة"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
                border-radius: 8px;
            }

            QTabWidget::tab-bar {
                alignment: center;
            }

            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e9ecef, stop:1 #dee2e6);
                border: 1px solid #ced4da;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 100px;
            }

            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                font-weight: bold;
            }

            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }

            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #495057;
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 20px;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0056b3, stop:1 #004085);
            }

            QPushButton:pressed {
                background: #004085;
            }

            QTextEdit, QPlainTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                selection-background-color: #007bff;
            }

            QTextEdit:focus, QPlainTextEdit:focus {
                border-color: #007bff;
            }
        """)

    def create_menu(self):
        """إنشاء القائمة الرئيسية"""
        menubar = self.menuBar()
        
        # قائمة ملف
        file_menu = menubar.addMenu("ملف")
        
        open_action = QAction("فتح نص", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.load_text_from_file)
        file_menu.addAction(open_action)
        
        save_results_action = QAction("حفظ النتائج", self)
        save_results_action.setShortcut("Ctrl+S") 
        save_results_action.triggered.connect(self.save_results)
        file_menu.addAction(save_results_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("خروج", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # قائمة تحليل
        analysis_menu = menubar.addMenu("تحليل")
        
        quick_analysis_action = QAction("تحليل سريع", self)
        quick_analysis_action.setShortcut("F5")
        quick_analysis_action.triggered.connect(self.analyze_text)
        analysis_menu.addAction(quick_analysis_action)
        
        compare_action = QAction("مقارنة نصين", self)
        compare_action.triggered.connect(lambda: self.tabs.setCurrentIndex(3))
        analysis_menu.addAction(compare_action)
        
        # قائمة أدوات
        tools_menu = menubar.addMenu("أدوات")

        # إضافة خيار الشات الاحترافي
        professional_chat_action = QAction("💬 الشات الاحترافي", self)
        professional_chat_action.setShortcut("Ctrl+T")
        professional_chat_action.triggered.connect(self.open_professional_chat)
        tools_menu.addAction(professional_chat_action)
        
        export_chart_action = QAction("تصدير الرسم البياني", self)
        export_chart_action.triggered.connect(self.export_chart)
        tools_menu.addAction(export_chart_action)
        
        settings_action = QAction("الإعدادات", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

    def load_text_from_file(self):
        """تحميل نص من ملف"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "فتح ملف نصي",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    self.text_input.setText(text)
                    self.status_bar.showMessage(f"تم تحميل الملف: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل تحميل الملف: {str(e)}")

    def load_ayah_dialog(self):
        """حوار تحميل آية من البيانات"""
        if self.hafs_data is None:
            QMessageBox.warning(self, WARNING_TITLE, "بيانات حفص غير متوفرة")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("اختر آية")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # البحث
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("ابحث عن آية...")
        search_button = QPushButton("بحث")
        
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        
        # جدول النتائج
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["السورة", "رقم الآية", "النص", "الصفحة"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # ملء الجدول بأول 100 آية
        if self.hafs_data is not None:
            table.setRowCount(min(100, len(self.hafs_data)))
            for i in range(min(100, len(self.hafs_data))):
                row = self.hafs_data.iloc[i]
                table.setItem(i, 0, QTableWidgetItem(row['sura_name_ar']))
                table.setItem(i, 1, QTableWidgetItem(str(row['aya_no'])))
                table.setItem(i, 2, QTableWidgetItem(row['aya_text'][:50] + "..."))
                table.setItem(i, 3, QTableWidgetItem(str(row['page'])))
            
        layout.addWidget(table)
        
        # أزرار
        buttons_layout = QHBoxLayout()
        load_btn = QPushButton("تحميل")
        cancel_btn = QPushButton("إلغاء")
        
        load_btn.clicked.connect(lambda: self.load_selected_ayah(table, dialog))
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons_layout.addWidget(load_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        dialog.exec_()

    def load_selected_ayah(self, table: QTableWidget, dialog: QDialog):
        """تحميل الآية المحددة"""
        current_row = table.currentRow()
        if current_row >= 0 and self.hafs_data is not None:
            ayah_text = self.hafs_data.iloc[current_row]['aya_text']
            self.text_input.setText(ayah_text)
            dialog.accept()

    def paste_text(self):
        """لصق نص من الحافظة"""
        clipboard = QApplication.clipboard()
        self.text_input.setText(clipboard.text())

    def analyze_text(self):
        """تحليل النص المدخل"""
        text = self.text_input.toPlainText().strip()
        
        if not text:
            QMessageBox.warning(self, WARNING_TITLE, "الرجاء إدخال نص للتحليل")
            return
            
        self.status_bar.showMessage("جاري التحليل...")
        
        try:
            # إجراء التحليل
            processor = SimpleTextProcessor()

            # تطبيع النص
            normalized = processor.normalize_arabic(text)

            # تحليل الأحرف
            char_freq = {}
            for char in text:
                if char.strip():  # تجاهل المسافات الفارغة
                    char_freq[char] = char_freq.get(char, 0) + 1

            # استخراج الرموز الخاصة
            special_symbols = []
            numbers = []
            diacritics = []

            for char in text:
                code = ord(char)
                if 0x0660 <= code <= 0x0669:  # أرقام عربية
                    numbers.append(char)
                elif 0x064B <= code <= 0x0652:  # تشكيل
                    diacritics.append(char)
                elif 0x06D0 <= code <= 0x06ED:  # رموز قرآنية
                    special_symbols.append(char)

            # إنشاء نتيجة التحليل
            self.current_analysis = TextAnalysisResult(
                original_text=text,
                normalized_text=normalized,
                character_count=len(text),
                word_count=len(text.split()),
                unique_characters=list(set(text)),
                character_frequencies=char_freq,
                special_symbols=list(set(special_symbols)),
                numbers=list(set(numbers)),
                diacritics=list(set(diacritics))
            )

            # عرض النتائج في التبويبات
            self.display_results()

            self.status_bar.showMessage("تم التحليل بنجاح")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل التحليل: {str(e)}")
            self.status_bar.showMessage("فشل التحليل")

    def display_results(self):
        """عرض نتائج التحليل"""
        if not self.current_analysis:
            return
            
        # تحليل الأحرف
        self.char_analysis_widget.display_analysis(self.current_analysis)
        
        # الإحصائيات
        self.statistics_widget.set_analysis(self.current_analysis)
        
        # النتائج المفصلة
        results_html = f"""
        <h2>نتائج تحليل النص القرآني</h2>
        
        <h3>معلومات عامة:</h3>
        <ul>
            <li><b>عدد الأحرف الكلي:</b> {self.current_analysis.character_count}</li>
            <li><b>عدد الكلمات:</b> {self.current_analysis.word_count}</li>
            <li><b>عدد الأحرف الفريدة:</b> {len(self.current_analysis.unique_characters)}</li>
            <li><b>متوسط طول الكلمة:</b> {self.current_analysis.character_count / max(1, self.current_analysis.word_count):.2f} حرف</li>
        </ul>
        
        <h3>الرموز الخاصة:</h3>
        """
        
        if self.current_analysis.special_symbols:
            results_html += "<p><b>الرموز القرآنية:</b> "
            for symbol in self.current_analysis.special_symbols:
                results_html += f"<span style='font-size: 20px; margin: 0 5px;'>{symbol}</span>"
            results_html += "</p>"
            
        if self.current_analysis.numbers:
            results_html += "<p><b>الأرقام:</b> " + " ".join(self.current_analysis.numbers) + "</p>"
            
        if self.current_analysis.diacritics:
            results_html += "<p><b>علامات التشكيل:</b> "
            for diacritic in self.current_analysis.diacritics:
                results_html += f"<span style='font-size: 20px; margin: 0 5px;'>◌{diacritic}</span>"
            results_html += "</p>"
            
        # أكثر الأحرف تكراراً
        results_html += "<h3>أكثر 5 أحرف تكراراً:</h3><ol>"
        
        sorted_chars = sorted(
            self.current_analysis.character_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        for char, freq in sorted_chars:
            percentage = (freq / self.current_analysis.character_count) * 100
            results_html += f"<li><b>{char}</b> - {freq} مرة ({percentage:.1f}%)</li>"
            
        results_html += "</ol>"
        
        # النص المطبع
        results_html += f"""
        <h3>النص بعد التطبيع:</h3>
        <div style='background-color: #f5f5f5; padding: 10px; border-radius: 5px; 
                    font-size: 16px; line-height: 1.8; direction: rtl;'>
            {self.current_analysis.normalized_text}
        </div>
        """
        
        self.results_widget.setHtml(results_html)
        
        # وضع النص في تبويب المقارنة
        self.comparison_widget.text2_edit.setText(self.current_analysis.original_text)

    def save_results(self):
        """حفظ نتائج التحليل"""
        if not self.current_analysis:
            QMessageBox.warning(self, WARNING_TITLE, "لا توجد نتائج لحفظها")
            return
            
        file_path, file_type = QFileDialog.getSaveFileName(
            self,
            "حفظ النتائج",
            f"text_analysis_{QDateTime.currentDateTime().toString('yyyyMMdd_HHmmss')}",
            "HTML Files (*.html);;JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.html'):
                    # حفظ كـ HTML
                    html_content = f"""
                    <!DOCTYPE html>
                    <html dir="rtl">
                    <head>
                        <meta charset="UTF-8">
                        <title>نتائج تحليل النص القرآني</title>
                        <style>
                            body {{ font-family: 'Arial Unicode MS', Tahoma; padding: 20px; }}
                            h1, h2, h3 {{ color: #333; }}
                            .arabic-text {{ font-size: 18px; line-height: 1.8; background: #f5f5f5; padding: 15px; }}
                        </style>
                    </head>
                    <body>
                        {self.results_widget.toHtml()}
                    </body>
                    </html>
                    """
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                        
                elif file_path.endswith('.json'):
                    # حفظ كـ JSON
                    data = {
                        'original_text': self.current_analysis.original_text,
                        'normalized_text': self.current_analysis.normalized_text,
                        'character_count': self.current_analysis.character_count,
                        'word_count': self.current_analysis.word_count,
                        'character_frequencies': self.current_analysis.character_frequencies,
                        'special_symbols': self.current_analysis.special_symbols,
                        'numbers': self.current_analysis.numbers,
                        'diacritics': self.current_analysis.diacritics
                    }
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                        
                else:
                    # حفظ كنص عادي
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.results_widget.toPlainText())
                        
                QMessageBox.information(self, "نجح", "تم حفظ النتائج بنجاح")
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل حفظ النتائج: {str(e)}")

    def export_chart(self):
        """تصدير الرسم البياني الحالي"""
        if not self.current_analysis:
            QMessageBox.warning(self, WARNING_TITLE, "لا يوجد رسم بياني لتصديره")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "تصدير الرسم البياني",
            f"chart_{QDateTime.currentDateTime().toString('yyyyMMdd_HHmmss')}",
            "PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg)"
        )
        
        if file_path:
            try:
                if hasattr(self.statistics_widget, 'figure') and self.statistics_widget.figure:
                    self.statistics_widget.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                    QMessageBox.information(self, "نجح", "تم تصدير الرسم البياني بنجاح")
                else:
                    QMessageBox.warning(self, WARNING_TITLE, "لا يوجد رسم بياني متاح للتصدير")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل تصدير الرسم: {str(e)}")

    def show_settings(self):
        """عرض نافذة الإعدادات المحسنة"""
        dialog = QDialog(self)
        dialog.setWindowTitle("⚙️ إعدادات التطبيق المتقدمة")
        dialog.setModal(True)
        dialog.resize(650, 550)

        # الحصول على الثيم الفعلي المطبق حالياً (مهم للثيم التلقائي)
        from ui_settings import get_current_effective_theme
        effective_theme = get_current_effective_theme(self.theme)
        theme_settings = get_theme_settings(effective_theme)
        
        # تطبيق ستايل النافذة باستخدام الثيم الفعلي
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {theme_settings['background_color']};
                color: {theme_settings['text_color']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme_settings['border_color']};
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: {theme_settings['secondary_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                font-size: 14px;
                color: {theme_settings['text_color']};
            }}
            QComboBox {{
                background-color: {theme_settings['secondary_bg']};
                border: 2px solid {theme_settings['border_color']};
                border-radius: 5px;
                padding: 8px;
                color: {theme_settings['text_color']};
            }}
            QComboBox:focus {{
                border-color: {theme_settings['highlight_color']};
            }}
            QSpinBox {{
                background-color: {theme_settings['secondary_bg']};
                border: 2px solid {theme_settings['border_color']};
                border-radius: 5px;
                padding: 8px;
                color: {theme_settings['text_color']};
            }}
            QSpinBox:focus {{
                border-color: {theme_settings['highlight_color']};
            }}
            QPushButton {{
                background-color: {theme_settings['highlight_color']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme_settings['hover_color']};
            }}
            QLabel {{
                color: {theme_settings['text_color']};
            }}
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # مجموعة إعدادات الثيم
        theme_group = QGroupBox("🎨 إعدادات المظهر والألوان")
        theme_layout = QVBoxLayout(theme_group)

        # عرض الثيم الحالي والفعلي
        current_theme_info = QLabel()
        if self.theme == "auto":
            current_theme_info.setText(f"الثيم الحالي: 🔄 تلقائي → {get_theme_settings(effective_theme)['name']}")
            current_theme_info.setStyleSheet(f"color: {theme_settings['highlight_color']}; font-weight: bold;")
        else:
            current_theme_info.setText(f"الثيم الحالي: {get_theme_settings(self.theme)['name']}")
            current_theme_info.setStyleSheet(f"color: {theme_settings['highlight_color']}; font-weight: bold;")
        
        theme_layout.addWidget(current_theme_info)

        # اختيار الثيم - مبسط
        theme_layout.addWidget(QLabel("اختر الثيم:"))
        theme_combo = QComboBox()

        # قائمة الثيمات المتاحة
        themes = [
            ("light", "🌞 فاتح"),
            ("dark", "🌙 داكن"),
            ("red_dark", "🔴 أحمر داكن"),
            ("orange_light", "🟠 برتقالي فاتح"),
            ("neon_dark", "💚 نيون داكن"),
            ("auto", "🔄 تلقائي"),
            ("blue_ocean", "🌊 أزرق محيطي"),
            ("purple_royal", "👑 بنفسجي ملكي"),
            ("green_forest", "🌲 أخضر غابات"),
            ("gold_luxury", "✨ ذهبي فاخر")
        ]

        # إضافة الثيمات للقائمة
        for theme_key, theme_name in themes:
            theme_combo.addItem(theme_name, theme_key)
            if theme_key == self.theme:
                theme_combo.setCurrentIndex(theme_combo.count() - 1)

        theme_layout.addWidget(theme_combo)
        layout.addWidget(theme_group)

        # مجموعة إعدادات الخط المحسنة للشاشات الكبيرة
        font_group = QGroupBox("🔤 إعدادات الخطوط والنصوص - للشاشات الكبيرة")
        font_layout = QVBoxLayout(font_group)

        # حجم الخط بشريط أرقام مرن
        font_size_layout = QVBoxLayout()

        # عنوان وشريط الأرقام
        size_header_layout = QHBoxLayout()
        size_header_layout.addWidget(QLabel("📏 حجم الخط بالبكسل:"))

        # شريط الأرقام الرئيسي - مبسط
        font_size_spinbox = QSpinBox()
        font_size_spinbox.setRange(8, 128)  # نطاق مباشر
        font_size_spinbox.setValue(self.font_size if isinstance(self.font_size, int) else 18)
        font_size_spinbox.setSuffix(" px")
        font_size_spinbox.setMinimumWidth(120)
        font_size_spinbox.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
        """)

        size_header_layout.addWidget(font_size_spinbox)
        size_header_layout.addStretch()

        # معلومات الحدود
        size_info = QLabel("الحد الأدنى: 8px | الحد الأقصى: 128px")
        size_info.setStyleSheet("color: gray; font-size: 11px;")

        font_size_layout.addLayout(size_header_layout)
        font_size_layout.addWidget(size_info)

        font_layout.addLayout(font_size_layout)

        # نوع الخط - مبسط
        font_family_layout = QHBoxLayout()
        font_family_layout.addWidget(QLabel("نوع الخط:"))
        font_family_combo = QComboBox()

        # قائمة الخطوط المتاحة
        fonts = [
            ("default", "Arial (افتراضي)"),
            ("arabic_uthmani", "🕌 الخط العثماني الأصلي"),
            ("arabic_uthmani_alt", "🕌 الخط العثماني البديل"),
            ("arabic", "📖 الخط العربي الأساسي"),
            ("arabic_naskh", "✍️ خط النسخ العربي"),
            ("english", "🔤 الإنجليزي الأساسي"),
            ("monospace", "⌨️ أحادي المسافة")
        ]

        for family_key, family_name in fonts:
            font_family_combo.addItem(family_name, family_key)
            if family_key == self.font_family:
                font_family_combo.setCurrentIndex(font_family_combo.count() - 1)

        font_family_layout.addWidget(font_family_combo)
        font_layout.addLayout(font_family_layout)

        layout.addWidget(font_group)

        # أزرار التحكم المحسنة
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        # زر التطبيق
        apply_btn = QPushButton("✅ تطبيق وحفظ")
        apply_btn.setDefault(True)

        # زر الإلغاء
        cancel_btn = QPushButton("❌ إلغاء")
        cancel_btn.clicked.connect(dialog.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(apply_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        # ربط زر التطبيق
        def apply_and_close():
            self.apply_settings(
                theme_combo.currentData(),
                font_size_spinbox.value(),  # من الـ spinbox
                font_family_combo.currentData()
            )
            dialog.accept()

        apply_btn.clicked.connect(apply_and_close)

        # تشغيل النافذة
        dialog.exec_()

    def apply_settings(self, theme, font_size, font_family):
        """تطبيق الإعدادات الجديدة"""
        try:
            self.theme = theme
            self.font_size = font_size
            self.font_family = font_family
            self.apply_ui_settings()

            # حفظ الإعدادات تلقائياً
            self.save_settings()

            # تطبيق الإعدادات على نافذة الشات إذا كانت مفتوحة
            self.apply_settings_to_chat_window()

            print(f"✅ تم تطبيق وحفظ الإعدادات: {theme}, {font_size}, {font_family}")

            # إظهار رسالة تأكيد
            theme_info = get_theme_settings(theme)
            QMessageBox.information(
                self,
                "✅ تم التطبيق بنجاح",
                f"تم تطبيق الإعدادات الجديدة على:\n\n"
                f"🖥️ النافذة الرئيسية\n"
                f"💬 نافذة الشات الذكي\n\n"
                f"🎨 الثيم: {theme_info.get('name', theme)}\n"
                f"📏 حجم الخط: {get_font_size(font_size)}px\n"
                f"🔤 نوع الخط: {get_font_family(font_family)}"
            )

        except Exception as e:
            QMessageBox.warning(self, "❌ خطأ", f"فشل في تطبيق الإعدادات: {str(e)}")

    def save_settings(self):
        """حفظ الإعدادات في ملف"""
        try:
            # إنشاء مجلد GUI_DATA إذا لم يكن موجوداً
            GUI_DATA_DIR.mkdir(exist_ok=True)
            
            settings = {
                "theme": self.theme,
                "font_size": self.font_size,  # الآن يحفظ الرقم مباشرة
                "font_family": self.font_family,
                "window_width": self.width(),
                "window_height": self.height(),
                "window_x": self.x(),
                "window_y": self.y(),
                "settings_version": "2.0",  # إصدار الإعدادات
                "last_updated": str(QDateTime.currentDateTime().toString())
            }

            # استخدام المسار الجديد
            settings_file = GUI_DATA_DIR / "gui_settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)

            print(f"✅ تم حفظ الإعدادات في {settings_file}")

        except Exception as e:
            print(f"❌ خطأ في حفظ الإعدادات: {e}")

    def load_saved_settings(self):
        """تحميل الإعدادات المحفوظة"""
        try:
            settings_file = GUI_DATA_DIR / "gui_settings.json"
            
            # إنشاء مجلد GUI_DATA إذا لم يكن موجوداً
            GUI_DATA_DIR.mkdir(exist_ok=True)
            
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # تطبيق الإعدادات المحفوظة مع التحقق من النوع
                self.theme = settings.get("theme", "light")

                # التحقق من نوع font_size - قد يكون رقم أو نص قديم
                saved_font_size = settings.get("font_size", 18)
                if isinstance(saved_font_size, str):
                    # إذا كان نص قديم، حوله للرقم المناسب
                    old_size_mapping = {
                        "small": 12,
                        "medium": 16,
                        "large": 20,
                        "xlarge": 24
                    }
                    self.font_size = old_size_mapping.get(saved_font_size, 18)
                    print(f"🔄 تم تحويل حجم الخط القديم '{saved_font_size}' إلى {self.font_size}px")
                else:
                    self.font_size = saved_font_size

                # التحقق من نوع الخط
                saved_font_family = settings.get("font_family", "arabic_uthmani")
                if saved_font_family == "default":
                    self.font_family = "arabic_uthmani"  # تحديث للخط العثماني
                    print("🔄 تم تحديث الخط الافتراضي للخط العثماني")
                else:
                    self.font_family = saved_font_family

                # إذا كان الثيم تلقائي، ابدأ مؤقت التحديث
                if self.theme == "auto":
                    self.start_auto_theme_timer()
                    from ui_settings import get_current_effective_theme
                    effective_theme = get_current_effective_theme(self.theme)
                    print(f"🔄 تم تشغيل الثيم التلقائي: {get_theme_settings(effective_theme)['name']}")

                # تطبيق موضع وحجم النافذة المحفوظ
                if settings.get("window_width") and settings.get("window_height"):
                    self.resize(settings["window_width"], settings["window_height"])

                if settings.get("window_x") is not None and settings.get("window_y") is not None:
                    self.move(settings["window_x"], settings["window_y"])

                print(f"✅ تم تحميل الإعدادات المحفوظة: {self.theme}, {self.font_size}px, {self.font_family}")

            else:
                print("📁 لا يوجد ملف إعدادات محفوظ، استخدام الإعدادات الافتراضية")
                # الإعدادات الافتراضية
                self.theme = "light"
                self.font_size = 18
                self.font_family = "arabic_uthmani"

        except Exception as e:
            print(f"❌ خطأ في تحميل الإعدادات: {e}")
            # في حالة الخطأ، استخدم الإعدادات الافتراضية
            self.theme = "light"
            self.font_size = 18
            self.font_family = "arabic_uthmani"

    def closeEvent(self, event):
        """حفظ الإعدادات عند إغلاق التطبيق"""
        self.save_settings()
        event.accept()

    def open_professional_chat(self):
        """فتح نافذة الشات الاحترافية مع تطبيق الإعدادات"""
        if self.professional_chat_window is None:
            self.professional_chat_window = ProfessionalChatWindow(self)
            # تطبيق إعدادات الواجهة على نافذة الشات
            self.apply_settings_to_chat_window()
        else:
            # تحديث الإعدادات إذا كانت النافذة موجودة
            self.apply_settings_to_chat_window()

        self.professional_chat_window.show()
        self.professional_chat_window.raise_()
        self.professional_chat_window.activateWindow()

    def apply_settings_to_chat_window(self):
        """تطبيق إعدادات الواجهة على نافذة الشات - مبسط"""
        if self.professional_chat_window:
            try:
                # تطبيق الإعدادات على نافذة الشات
                self.professional_chat_window.theme = self.theme
                self.professional_chat_window.font_size = self.font_size
                self.professional_chat_window.font_family = self.font_family
                if hasattr(self.professional_chat_window, 'apply_ui_settings'):
                    self.professional_chat_window.apply_ui_settings()

                print(f"✅ تم تطبيق الإعدادات على نافذة الشات")

            except Exception as e:
                print(f"❌ خطأ في تطبيق الإعدادات على نافذة الشات: {e}")
