#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة محسنة لعرض وإدارة بيانات القرآن الكريم بالرسم العثماني
Enhanced Interface for Quran Uthmanic Data Management
"""

from shared_imports import *
from data_models import AyahInfo, TextAnalysisResult, SimpleTextProcessor
from analysis_widgets import CharacterAnalysisWidget, StatisticsWidget
from complete_chat_window import ProfessionalChatWindow
from svg_comparison_tools import SVGAnalyzerWidget, ComparisonWidget
from shared_constants import GUI_DATA_DIR
import pandas as pd
import json


class QuranDataViewerWidget(QWidget):
    """ويدجت عرض بيانات القرآن الكريم المتقدم"""
    
    def __init__(self):
        super().__init__()
        self.hafs_data = None
        self.filtered_data = None
        self.current_page = 1
        self.items_per_page = 50
        self.setup_ui()
        self.load_quran_data()
        
    def setup_ui(self):
        """إعداد واجهة عرض البيانات"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)  # هوامش أقل
        layout.setSpacing(1)  # مسافات أقل
        
        # رأس الصفحة - مضغوط جداً
        header = QLabel("📊 بيانات القرآن الكريم - حفص عن عاصم")
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(35)  # ارتفاع ثابت
        header.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                padding: 5px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 4px;
                margin: 0px;
            }
        """)
        layout.addWidget(header)
        
        # شريط البحث والفلترة المتقدم
        search_frame = self.create_search_frame()
        layout.addWidget(search_frame)
        
        # جدول البيانات الرئيسي - يأخذ المساحة المتبقية
        self.data_table = self.create_data_table()
        layout.addWidget(self.data_table, 1)  # stretch factor = 1
        
        # شريط التنقل والتصدير
        navigation_frame = self.create_navigation_frame()
        layout.addWidget(navigation_frame)
        
        
    def create_search_frame(self):
        """إنشاء إطار البحث والفلترة"""
        frame = QGroupBox("🔍 البحث والفلترة المتقدمة")
        frame.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #007bff;
                border-radius: 6px;
                margin: 1px;
                margin-top: 15px;
                padding-top: 12px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                left: 15px;
                top: -20px;
                padding: 5px 15px 5px 15px;
                background-color: #007bff;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #0056b3;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 5, 8, 5)  # هوامش مقللة
        layout.setSpacing(5)  # مسافات مقللة
        
        # الصف الأول: البحث النصي
        search_row1 = QHBoxLayout()
        search_row1.setSpacing(8)
        
        search_row1.addWidget(QLabel("البحث:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث في نص الآيات...")
        self.search_input.textChanged.connect(self.apply_filters)
        
        self.search_type = QComboBox()
        self.search_type.addItems(["نص عثماني", "نص إملائي", "كلاهما"])
        self.search_type.currentTextChanged.connect(self.apply_filters)
        
        search_row1.addWidget(self.search_input, 3)
        search_row1.addWidget(self.search_type, 1)
        
        # الصف الثاني: الفلاتر والأزرار
        controls_row = QHBoxLayout()
        controls_row.setSpacing(8)
        
        # فلاتر مضغوطة
        controls_row.addWidget(QLabel("سورة:"))
        self.sura_filter = QComboBox()
        self.sura_filter.addItem("جميع")
        self.sura_filter.currentTextChanged.connect(self.apply_filters)
        controls_row.addWidget(self.sura_filter, 1)
        
        controls_row.addWidget(QLabel("جزء:"))
        self.juzz_filter = QComboBox()
        self.juzz_filter.addItems(["جميع"] + [str(i) for i in range(1, 31)])
        self.juzz_filter.currentTextChanged.connect(self.apply_filters)
        controls_row.addWidget(self.juzz_filter, 1)
        
        controls_row.addWidget(QLabel("صفحة:"))
        self.page_filter = QSpinBox()
        self.page_filter.setRange(0, 604)
        self.page_filter.setSpecialValueText("جميع")
        self.page_filter.valueChanged.connect(self.apply_filters)
        controls_row.addWidget(self.page_filter, 1)
        
        # أزرار مضغوطة
        clear_btn = QPushButton("🔄 مسح")
        clear_btn.setMaximumWidth(60)
        clear_btn.clicked.connect(self.clear_filters)
        controls_row.addWidget(clear_btn)
        
        export_btn = QPushButton("📤 تصدير")
        export_btn.setMaximumWidth(70)
        export_btn.clicked.connect(self.export_filtered_data)
        controls_row.addWidget(export_btn)
        
        controls_row.addStretch()
        
        layout.addLayout(search_row1)
        layout.addLayout(controls_row)
        
        return frame
        
    def create_data_table(self):
        """إنشاء جدول البيانات الرئيسي"""
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSortingEnabled(True)
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dee2e6;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #dee2e6;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QHeaderView::section {
                background-color: #343a40;
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # إعداد الأعمدة
        headers = [
            "الرقم", "الجزء", "رقم السورة", "اسم السورة", 
            "الصفحة", "رقم الآية", "بداية السطر", "نهاية السطر",
            "نص الآية العثماني", "النص الإملائي"
        ]
        
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # تخصيص عرض الأعمدة
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # الرقم
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # الجزء
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # رقم السورة
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # اسم السورة
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # الصفحة
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # رقم الآية
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # بداية السطر
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # نهاية السطر
        header.setSectionResizeMode(8, QHeaderView.Stretch)           # النص العثماني
        header.setSectionResizeMode(9, QHeaderView.Stretch)           # النص الإملائي
        
        # السماح بتغيير حجم الأعمدة يدوياً
        header.setSectionsMovable(True)
        
        # ربط النقر المزدوج بعرض تفاصيل الآية
        table.itemDoubleClicked.connect(self.show_ayah_details)
        
        return table
        
    def create_navigation_frame(self):
        """إنشاء إطار التنقل والتصدير - مضغوط"""
        frame = QFrame()
        frame.setMaximumHeight(35)  # تحديد ارتفاع أقصى
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(5, 2, 5, 2)  # هوامش صغيرة
        layout.setSpacing(8)  # مسافات صغيرة
        
        # معلومات التنقل
        self.page_info_label = QLabel("الصفحة 1 من 1")
        self.page_info_label.setStyleSheet("font-weight: bold; color: #495057; font-size: 12px;")
        
        # أزرار تنقل مضغوطة
        first_btn = QPushButton("⏮️")
        prev_btn = QPushButton("◀️")
        next_btn = QPushButton("▶️")
        last_btn = QPushButton("⏭️")
        
        # تصغير الأزرار
        for btn in [first_btn, prev_btn, next_btn, last_btn]:
            btn.setMaximumSize(30, 25)
            btn.setMinimumSize(30, 25)
        
        first_btn.clicked.connect(lambda: self.go_to_page(1))
        prev_btn.clicked.connect(self.prev_page)
        next_btn.clicked.connect(self.next_page)
        last_btn.clicked.connect(self.go_to_last_page)
        
        # عدد العناصر لكل صفحة
        self.items_per_page_combo = QComboBox()
        self.items_per_page_combo.addItems(["25", "50", "100", "200"])
        self.items_per_page_combo.setCurrentText("50")
        self.items_per_page_combo.setMaximumWidth(60)
        self.items_per_page_combo.currentTextChanged.connect(self.change_items_per_page)
        
        # أزرار التصدير مضغوطة
        export_csv_btn = QPushButton("CSV")
        export_json_btn = QPushButton("JSON")
        export_excel_btn = QPushButton("Excel")
        
        for btn in [export_csv_btn, export_json_btn, export_excel_btn]:
            btn.setMaximumSize(50, 25)
            btn.setMinimumSize(50, 25)
        
        export_csv_btn.clicked.connect(lambda: self.export_data("csv"))
        export_json_btn.clicked.connect(lambda: self.export_data("json"))
        export_excel_btn.clicked.connect(lambda: self.export_data("excel"))
        
        # ترتيب مضغوط
        layout.addWidget(self.page_info_label)
        layout.addWidget(first_btn)
        layout.addWidget(prev_btn)
        layout.addWidget(next_btn)
        layout.addWidget(last_btn)
        layout.addStretch()
        layout.addWidget(self.items_per_page_combo)
        layout.addStretch()
        layout.addWidget(export_csv_btn)
        layout.addWidget(export_json_btn)
        layout.addWidget(export_excel_btn)
        
        return frame
        
    def load_quran_data(self):
        """تحميل بيانات القرآن الكريم"""
        try:
            # محاولة تحميل البيانات من ملف CSV
            csv_path = Path("Uthmanic_data/hafs_smart.csv")
            if csv_path.exists():
                self.hafs_data = pd.read_csv(csv_path, encoding='utf-8')
                self.filtered_data = self.hafs_data.copy()
                
                # تحديث فلتر السور
                sura_names = self.hafs_data['sura_name_ar'].unique()
                self.sura_filter.addItems(sorted(sura_names))
                
                # عرض البيانات
                self.display_current_page()
                
                self.show_status_message("تم تحميل البيانات بنجاح", "success")
                
            else:
                self.show_status_message("ملف البيانات غير موجود", "error")
                
        except Exception as e:
            self.show_status_message(f"خطأ في تحميل البيانات: {str(e)}", "error")
            
    def apply_filters(self):
        """تطبيق الفلاتر على البيانات"""
        if self.hafs_data is None:
            return
            
        filtered_data = self.hafs_data.copy()
        
        # فلتر البحث النصي
        search_text = self.search_input.text().strip()
        if search_text:
            search_type = self.search_type.currentText()
            if search_type == "نص عثماني":
                filtered_data = filtered_data[filtered_data['aya_text'].str.contains(search_text, na=False)]
            elif search_type == "نص إملائي":
                filtered_data = filtered_data[filtered_data['aya_text_emlaey'].str.contains(search_text, na=False)]
            else:  # كلاهما
                mask1 = filtered_data['aya_text'].str.contains(search_text, na=False)
                mask2 = filtered_data['aya_text_emlaey'].str.contains(search_text, na=False)
                filtered_data = filtered_data[mask1 | mask2]
                
        # فلتر السورة
        if self.sura_filter.currentText() != "جميع السور":
            sura_name = self.sura_filter.currentText()
            filtered_data = filtered_data[filtered_data['sura_name_ar'] == sura_name]
            
        # فلتر الجزء
        if self.juzz_filter.currentText() != "جميع الأجزاء":
            juzz_num = int(self.juzz_filter.currentText().split()[-1])
            filtered_data = filtered_data[filtered_data['jozz'] == juzz_num]
            
        # فلتر الصفحة
        if self.page_filter.value() > 0:
            filtered_data = filtered_data[filtered_data['page'] == self.page_filter.value()]
            
        self.filtered_data = filtered_data
        self.current_page = 1
        self.display_current_page()
        
    def clear_filters(self):
        """مسح جميع الفلاتر"""
        self.search_input.clear()
        self.search_type.setCurrentIndex(0)
        self.sura_filter.setCurrentIndex(0)
        self.juzz_filter.setCurrentIndex(0)
        self.page_filter.setValue(0)
        
        if self.hafs_data is not None:
            self.filtered_data = self.hafs_data.copy()
            self.current_page = 1
            self.display_current_page()
            
    def display_current_page(self):
        """عرض الصفحة الحالية من البيانات"""
        if self.filtered_data is None or len(self.filtered_data) == 0:
            self.data_table.setRowCount(0)
            self.page_info_label.setText("لا توجد بيانات للعرض")
            return
            
        # حساب نطاق البيانات للصفحة الحالية
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_data = self.filtered_data.iloc[start_idx:end_idx]
        
        # إعداد الجدول
        self.data_table.setRowCount(len(page_data))
        
        # ملء البيانات
        for row, (_, record) in enumerate(page_data.iterrows()):
            self.data_table.setItem(row, 0, QTableWidgetItem(str(record['id'])))
            self.data_table.setItem(row, 1, QTableWidgetItem(str(record['jozz'])))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(record['sura_no'])))
            self.data_table.setItem(row, 3, QTableWidgetItem(record['sura_name_ar']))
            self.data_table.setItem(row, 4, QTableWidgetItem(str(record['page'])))
            self.data_table.setItem(row, 5, QTableWidgetItem(str(record['aya_no'])))
            self.data_table.setItem(row, 6, QTableWidgetItem(str(record.get('line_start', ''))))
            self.data_table.setItem(row, 7, QTableWidgetItem(str(record.get('line_end', ''))))
            
            # النص العثماني مع تنسيق خاص
            uthmanic_item = QTableWidgetItem(record['aya_text'])
            # استخدام الخط العثماني المحمل من التطبيق
            from PyQt5.QtGui import QFontDatabase
            font_db = QFontDatabase()
            uthmanic_families = [f for f in font_db.families() if 'uthmanic' in f.lower() or 'hafs' in f.lower()]
            if uthmanic_families:
                uthmanic_font = QFont(uthmanic_families[0], 16)
            else:
                uthmanic_font = QFont("Traditional Arabic", 16)
            uthmanic_item.setFont(uthmanic_font)
            # تحسين عرض النص العثماني
            uthmanic_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.data_table.setItem(row, 8, uthmanic_item)
            
            # النص الإملائي
            emlaey_item = QTableWidgetItem(record['aya_text_emlaey'])
            emlaey_item.setFont(QFont("Arial Unicode MS", 12))
            self.data_table.setItem(row, 9, emlaey_item)
            
        # تحديث معلومات التنقل
        total_pages = (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page
        self.page_info_label.setText(f"الصفحة {self.current_page} من {total_pages} ({len(self.filtered_data)} عنصر)")
        
    def show_ayah_details(self, item):
        """عرض تفاصيل الآية عند النقر المزدوج"""
        row = item.row()
        if row < 0:
            return
            
        # الحصول على بيانات الآية
        start_idx = (self.current_page - 1) * self.items_per_page + row
        if start_idx >= len(self.filtered_data):
            return
            
        ayah_data = self.filtered_data.iloc[start_idx]
        
        # إنشاء نافذة التفاصيل
        dialog = QDialog(self)
        dialog.setWindowTitle(f"تفاصيل الآية - {ayah_data['sura_name_ar']} آية {ayah_data['aya_no']}")
        dialog.setModal(True)
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # معلومات الآية
        info_text = f"""
        <h2>{ayah_data['sura_name_ar']} - الآية {ayah_data['aya_no']}</h2>
        <p><b>الجزء:</b> {ayah_data['jozz']} | <b>الصفحة:</b> {ayah_data['page']}</p>
        <p><b>السطر:</b> من {ayah_data.get('line_start', 'غير محدد')} إلى {ayah_data.get('line_end', 'غير محدد')}</p>
        <hr>
        <h3>النص العثماني:</h3>
        <div style="font-family: 'Traditional Arabic', 'Arabic Typesetting'; font-size: 20px; 
                    line-height: 2; padding: 20px; background: #f8f9fa; border-radius: 8px; 
                    text-align: right; direction: rtl;">
            {ayah_data['aya_text']}
        </div>
        <h3>النص الإملائي:</h3>
        <div style="font-family: 'Arial Unicode MS'; font-size: 16px; 
                    line-height: 1.8; padding: 20px; background: #e9ecef; border-radius: 8px;
                    text-align: right; direction: rtl;">
            {ayah_data['aya_text_emlaey']}
        </div>
        """
        
        text_browser = QTextBrowser()
        text_browser.setHtml(info_text)
        layout.addWidget(text_browser)
        
        # زر الإغلاق
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
        
    # دوال التنقل
    def next_page(self):
        total_pages = (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.display_current_page()
            
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()
            
    def go_to_page(self, page):
        total_pages = (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page
        if 1 <= page <= total_pages:
            self.current_page = page
            self.display_current_page()
            
    def go_to_last_page(self):
        total_pages = (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page
        self.go_to_page(total_pages)
        
    def change_items_per_page(self, text):
        self.items_per_page = int(text)
        self.current_page = 1
        self.display_current_page()
        
    def export_data(self, format_type):
        """تصدير البيانات بتنسيقات مختلفة"""
        if self.filtered_data is None or len(self.filtered_data) == 0:
            QMessageBox.warning(self, "تحذير", "لا توجد بيانات للتصدير")
            return
            
        timestamp = QDateTime.currentDateTime().toString('yyyyMMdd_HHmmss')
        
        if format_type == "csv":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "تصدير CSV", 
                f"quran_data_{timestamp}.csv",
                "CSV Files (*.csv)"
            )
            if file_path:
                self.filtered_data.to_csv(file_path, index=False, encoding='utf-8-sig')
                
        elif format_type == "json":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "تصدير JSON",
                f"quran_data_{timestamp}.json", 
                "JSON Files (*.json)"
            )
            if file_path:
                self.filtered_data.to_json(file_path, orient='records', ensure_ascii=False, indent=2)
                
        elif format_type == "excel":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "تصدير Excel",
                f"quran_data_{timestamp}.xlsx",
                "Excel Files (*.xlsx)"
            )
            if file_path:
                self.filtered_data.to_excel(file_path, index=False, engine='openpyxl')
                
        if file_path:
            QMessageBox.information(self, "نجح", f"تم التصدير بنجاح إلى:\n{file_path}")
            
    def export_filtered_data(self):
        """تصدير البيانات المفلترة الحالية"""
        self.export_data("csv")  # افتراضياً CSV
        
    def show_status_message(self, message, msg_type="info"):
        """عرض رسالة الحالة"""
        if hasattr(self.parent(), 'status_bar'):
            self.parent().status_bar.showMessage(message)


class DataFormatsWidget(QWidget):
    """ويدجت عرض تنسيقات البيانات المتاحة"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # عنوان
        title = QLabel("📁 تنسيقات البيانات المتاحة")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 15px;
            background: linear-gradient(90deg, #6f42c1 0%, #6610f2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # معلومات التنسيقات
        formats_info = """
        <h3>📊 ملفات البيانات المتوفرة:</h3>
        
        <div style="margin: 15px 0;">
            <h4 style="color: #007bff;">🔹 hafs_smart.csv</h4>
            <ul>
                <li><b>التنسيق:</b> CSV (قيم مفصولة بفواصل)</li>
                <li><b>الحجم:</b> 6,238 سطر</li>
                <li><b>الترميز:</b> UTF-8 مع دعم اليونيكود العربي</li>
                <li><b>الاستخدام:</b> يمكن استيراده في جداول البيانات والقواعد</li>
            </ul>
        </div>

        <div style="margin: 15px 0;">
            <h4 style="color: #28a745;">🔹 hafs_smart.json</h4>
            <ul>
                <li><b>التنسيق:</b> JSON (كائنات جافا سكريبت)</li>
                <li><b>الحجم:</b> 81,071 سطر</li>
                <li><b>البنية:</b> مصفوفة من الكائنات، كل آية في كائن منفصل</li>
                <li><b>الاستخدام:</b> مثالي لتطبيقات الويب وواجهات البرمجة</li>
            </ul>
        </div>

        <div style="margin: 15px 0;">
            <h4 style="color: #fd7e14;">🔹 hafs_smart.html</h4>
            <ul>
                <li><b>التنسيق:</b> جدول HTML</li>
                <li><b>الحجم:</b> 87,326 سطر</li>
                <li><b>العنوان:</b> "KFGQPC Uthmanic Hafs Smart v8 Data"</li>
                <li><b>الاستخدام:</b> يمكن فتحه مباشرة في المتصفحات</li>
            </ul>
        </div>

        <div style="margin: 15px 0;">
            <h4 style="color: #dc3545;">🔹 hafs_smart.sql</h4>
            <ul>
                <li><b>التنسيق:</b> أوامر SQL INSERT</li>
                <li><b>الحجم:</b> 6,241 سطر</li>
                <li><b>قواعد البيانات:</b> متوافق مع MySQL/MariaDB/PostgreSQL</li>
                <li><b>الاستخدام:</b> استيراد مباشر إلى قواعد البيانات</li>
            </ul>
        </div>

        <div style="margin: 15px 0;">
            <h4 style="color: #6610f2;">🔹 hafs_smart.xml</h4>
            <ul>
                <li><b>التنسيق:</b> XML منسق ومنظم</li>
                <li><b>الحجم:</b> 87,307 سطر</li>
                <li><b>البنية:</b> عقدة DATA الجذرية مع عناصر ROW لكل آية</li>
                <li><b>الاستخدام:</b> مثالي لتبادل البيانات والتكامل</li>
            </ul>
        </div>

        <div style="margin: 15px 0;">
            <h4 style="color: #20c997;">🔹 hafs_smart.xlsx</h4>
            <ul>
                <li><b>التنسيق:</b> جدول بيانات Microsoft Excel</li>
                <li><b>المميزات:</b> يدعم الفلترة والتحليل المتقدم</li>
                <li><b>الاستخدام:</b> Excel، LibreOffice Calc، وبرامج الجداول</li>
            </ul>
        </div>

        <h3>🔤 موارد الخطوط:</h3>
        
        <div style="margin: 15px 0;">
            <h4 style="color: #6c757d;">🔹 Quran_Uthmanic_symbols.png</h4>
            <ul>
                <li><b>النوع:</b> خريطة أحرف اليونيكود</li>
                <li><b>المحتوى:</b> مرجع بصري لخط KFGQPC Uthmanic Hafs Smart</li>
                <li><b>النطاق:</b> مواضع اليونيكود U+0600-U+06FF (الكتلة العربية)</li>
                <li><b>يشمل:</b> الرموز القرآنية الخاصة وعلامات نهاية الآيات</li>
            </ul>
        </div>

        <h3>📈 إحصائيات البيانات:</h3>
        <table style="border-collapse: collapse; width: 100%; margin: 15px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #dee2e6; padding: 8px;"><b>إجمالي الآيات</b></td>
                <td style="border: 1px solid #dee2e6; padding: 8px;">6,236 آية</td>
            </tr>
            <tr>
                <td style="border: 1px solid #dee2e6; padding: 8px;"><b>إجمالي السور</b></td>
                <td style="border: 1px solid #dee2e6; padding: 8px;">114 سورة</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #dee2e6; padding: 8px;"><b>إجمالي الأجزاء</b></td>
                <td style="border: 1px solid #dee2e6; padding: 8px;">30 جزءاً</td>
            </tr>
            <tr>
                <td style="border: 1px solid #dee2e6; padding: 8px;"><b>إجمالي الصفحات</b></td>
                <td style="border: 1px solid #dee2e6; padding: 8px;">604 صفحة (مصحف المدينة)</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="border: 1px solid #dee2e6; padding: 8px;"><b>إصدار الخط</b></td>
                <td style="border: 1px solid #dee2e6; padding: 8px;">KFGQPC Uthmanic Hafs Smart v8</td>
            </tr>
            <tr>
                <td style="border: 1px solid #dee2e6; padding: 8px;"><b>ترميز النص</b></td>
                <td style="border: 1px solid #dee2e6; padding: 8px;">Unicode UTF-8</td>
            </tr>
        </table>

        <h3>🛠️ أمثلة الاستخدام:</h3>
        <ul>
            <li><b>تطوير الويب:</b> استخدم تنسيق JSON لواجهات البرمجة</li>
            <li><b>تطبيقات قواعد البيانات:</b> استخدم تنسيق SQL للاستيراد المباشر</li>
            <li><b>البحث والتحليل:</b> استخدم تنسيق CSV للتحليل الإحصائي</li>
            <li><b>التطبيقات متعددة المنصات:</b> استخدم تنسيق XML للتوافق</li>
            <li><b>معالجة الوثائق:</b> استخدم تنسيق HTML للعرض على الويب</li>
            <li><b>التطبيقات المكتبية:</b> استخدم تنسيق Excel للواجهة سهلة الاستخدام</li>
        </ul>
        """
        
        info_browser = QTextBrowser()
        info_browser.setHtml(formats_info)
        layout.addWidget(info_browser)
        
        # أزرار الوصول السريع
        buttons_frame = self.create_quick_access_buttons()
        layout.addWidget(buttons_frame)
        
    def create_quick_access_buttons(self):
        """إنشاء أزرار الوصول السريع للملفات"""
        frame = QGroupBox("🚀 وصول سريع")
        layout = QHBoxLayout(frame)
        
        # أزرار فتح الملفات
        open_csv_btn = QPushButton("📊 فتح CSV")
        open_json_btn = QPushButton("📋 فتح JSON") 
        open_html_btn = QPushButton("🌐 فتح HTML")
        open_excel_btn = QPushButton("📈 فتح Excel")
        
        open_csv_btn.clicked.connect(lambda: self.open_file("hafs_smart.csv"))
        open_json_btn.clicked.connect(lambda: self.open_file("hafs_smart.json"))
        open_html_btn.clicked.connect(lambda: self.open_file("hafs_smart.html"))
        open_excel_btn.clicked.connect(lambda: self.open_file("hafs_smart.xlsx"))
        
        layout.addWidget(open_csv_btn)
        layout.addWidget(open_json_btn)
        layout.addWidget(open_html_btn)
        layout.addWidget(open_excel_btn)
        layout.addStretch()
        
        return frame
        
    def open_file(self, filename):
        """فتح ملف في التطبيق المناسب"""
        file_path = Path("Uthmanic_data") / filename
        if file_path.exists():
            try:
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.run(["start", str(file_path)], shell=True)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(file_path)])
                else:  # Linux
                    subprocess.run(["xdg-open", str(file_path)])
                    
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"لا يمكن فتح الملف: {str(e)}")
        else:
            QMessageBox.warning(self, "تحذير", f"الملف غير موجود: {filename}")


class FontAnalysisWidget(QWidget):
    """ويدجت تحليل وعرض خريطة الخط العثماني"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # عنوان
        title = QLabel("🔤 تحليل الخط العثماني والرموز القرآنية")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 15px;
            background: linear-gradient(90deg, #dc3545 0%, #fd7e14 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # معلومات الخط
        font_info = """
        <h3>🎨 معلومات خط KFGQPC Uthmanic Hafs Smart:</h3>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4>📋 تفاصيل الخط:</h4>
            <ul>
                <li><b>الاسم:</b> KFGQPC Uthmanic Hafs Smart</li>
                <li><b>الإصدار:</b> v8 (2022-06-30)</li>
                <li><b>النوع:</b> خط عثماني متخصص للنصوص القرآنية</li>
                <li><b>الترميز:</b> Unicode UTF-8</li>
                <li><b>النطاق:</b> U+0600-U+06FF (الكتلة العربية)</li>
            </ul>
        </div>

        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4>🔣 الرموز الخاصة المتضمنة:</h4>
            <ul>
                <li><b>علامات نهاية الآيات:</b> ۞ ۝ ۜ</li>
                <li><b>رموز الوقف:</b> ۘ ۖ ۗ ۚ ۙ</li>
                <li><b>علامات التشكيل المتقدمة:</b> تشكيل خاص بالرسم العثماني</li>
                <li><b>الحروف المقطعة:</b> رموز فواتح السور</li>
                <li><b>علامات الضبط:</b> رموز متخصصة للقراءة الصحيحة</li>
            </ul>
        </div>

        <div style="background: #f3e5f5; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4>💎 المميزات الخاصة:</h4>
            <ul>
                <li><b>الرسم العثماني الأصيل:</b> يحافظ على الشكل التقليدي للمصحف</li>
                <li><b>تحسين للأجهزة الذكية:</b> محسن للقراءة على الشاشات الصغيرة</li>
                <li><b>دعم كامل لليونيكود:</b> توافق مع جميع المنصات</li>
                <li><b>الضبط الدقيق:</b> علامات تشكيل وضبط متخصصة</li>
            </ul>
        </div>

        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4>⚠️ ملاحظات مهمة:</h4>
            <ul>
                <li>هذا الخط مُعد لعرض الآيات فقط وليس لعرض صفحات كاملة</li>
                <li>يُستخدم لنتائج البحث وعرض الآيات في التطبيقات</li>
                <li>غير معد لمطابقة مصحف المدينة النبوية كاملاً</li>
                <li>مثالي للاستخدام في التفسير والكتب الإسلامية</li>
            </ul>
        </div>
        """
        
        info_browser = QTextBrowser()
        info_browser.setHtml(font_info)
        layout.addWidget(info_browser)
        
        # أزرار عرض خريطة الخط
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        
        view_symbols_btn = QPushButton("🔍 عرض خريطة الرموز")
        install_font_btn = QPushButton("💾 تثبيت الخط")
        test_font_btn = QPushButton("✨ اختبار الخط")
        
        view_symbols_btn.clicked.connect(self.view_font_symbols)
        install_font_btn.clicked.connect(self.install_font)
        test_font_btn.clicked.connect(self.test_font_display)
        
        buttons_layout.addWidget(view_symbols_btn)
        buttons_layout.addWidget(install_font_btn)
        buttons_layout.addWidget(test_font_btn)
        buttons_layout.addStretch()
        
        layout.addWidget(buttons_frame)
        
    def view_font_symbols(self):
        """عرض خريطة رموز الخط"""
        symbols_path = Path("Uthmanic_font/Quran_Uthmanic_symbols.png")
        if symbols_path.exists():
            dialog = QDialog(self)
            dialog.setWindowTitle("خريطة الرموز العثمانية")
            dialog.setModal(True)
            dialog.resize(1000, 800)
            
            layout = QVBoxLayout(dialog)
            
            # عرض الصورة
            label = QLabel()
            pixmap = QPixmap(str(symbols_path))
            label.setPixmap(pixmap.scaled(950, 750, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            label.setAlignment(Qt.AlignCenter)
            
            scroll_area = QScrollArea()
            scroll_area.setWidget(label)
            scroll_area.setWidgetResizable(True)
            
            layout.addWidget(scroll_area)
            
            close_btn = QPushButton("إغلاق")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.exec_()
        else:
            QMessageBox.warning(self, "تحذير", "ملف خريطة الرموز غير موجود")
            
    def install_font(self):
        """تثبيت الخط العثماني"""
        font_path = Path("Uthmanic_font/uthmanic_hafs-Font.ttf")
        if font_path.exists():
            try:
                # محاولة فتح الخط لتثبيته
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.run(["start", str(font_path)], shell=True)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", str(font_path)])
                else:  # Linux
                    subprocess.run(["xdg-open", str(font_path)])
                    
                QMessageBox.information(self, "معلومات", 
                    "تم فتح ملف الخط. يرجى اتباع التعليمات لتثبيته على نظامك.")
                    
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"لا يمكن فتح ملف الخط: {str(e)}")
        else:
            QMessageBox.warning(self, "تحذير", "ملف الخط غير موجود")
            
    def test_font_display(self):
        """اختبار عرض الخط"""
        dialog = QDialog(self)
        dialog.setWindowTitle("اختبار عرض الخط العثماني")
        dialog.setModal(True)
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        test_text = """
        <div style="text-align: center; padding: 20px;">
            <h3>اختبار الخط العثماني</h3>
        </div>
        
        <div style="font-family: 'Traditional Arabic', 'Arabic Typesetting', 'uthmanic_hafs-Font'; 
                    font-size: 24px; line-height: 2; padding: 20px; 
                    background: #f8f9fa; border-radius: 8px; 
                    text-align: right; direction: rtl; margin: 10px;">
            بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ ۝ ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ ۝
        </div>
        
        <div style="font-family: 'Traditional Arabic', 'Arabic Typesetting'; 
                    font-size: 20px; line-height: 1.8; padding: 20px; 
                    background: #e3f2fd; border-radius: 8px; 
                    text-align: right; direction: rtl; margin: 10px;">
            وَلَقَدْ يَسَّرْنَا ٱلْقُرْآنَ لِلذِّكْرِ فَهَلْ مِن مُّدَّكِرٍۢ ۝
        </div>
        
        <div style="padding: 15px; background: #fff3cd; border-radius: 8px; margin: 10px;">
            <h4>الرموز الخاصة:</h4>
            <p style="font-size: 20px; text-align: center;">
                ۞ ۝ ۜ ۘ ۖ ۗ ۚ ۙ ۛ
            </p>
        </div>
        """
        
        text_browser = QTextBrowser()
        text_browser.setHtml(test_text)
        layout.addWidget(text_browser)
        
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()


class QuranAnalysisMainWindow(QMainWindow):
    """النافذة الرئيسية المحدثة لمحلل النصوص القرآنية مع الواجهات الجديدة"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_shortcuts()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم الرئيسية"""
        self.setWindowTitle("🕌 محلل النصوص القرآنية المتقدم - إصدار OpenRouter")
        # تم إزالة setWindowIcon لتجنب مشاكل الاستيراد
        self.resize(1400, 900)
        
        # الويدجت المركزي
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(central_widget)
        
        # شريط الأدوات العلوي
        toolbar_frame = self.create_main_toolbar()
        main_layout.addWidget(toolbar_frame)
        
        # التبويبات الرئيسية
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)
        self.tabs.setMovable(True)
        
        # إضافة التبويبات الجديدة
        self.setup_tabs()
        
        main_layout.addWidget(self.tabs)
        
    def setup_tabs(self):
        """إعداد التبويبات الرئيسية"""
        # تبويب الشات الاحترافي
        self.chat_tab = QWidget()
        self.setup_chat_tab()
        self.tabs.addTab(self.chat_tab, "💬 الشات الاحترافي")
        
        # تبويب عرض بيانات القرآن
        self.quran_data_viewer = QuranDataViewerWidget()
        self.tabs.addTab(self.quran_data_viewer, "📖 بيانات القرآن")
        
        # تبويب تنسيقات البيانات
        self.data_formats_widget = DataFormatsWidget()
        self.tabs.addTab(self.data_formats_widget, "📁 تنسيقات البيانات")
        
        # تبويب تحليل الخط
        self.font_analysis_widget = FontAnalysisWidget()
        self.tabs.addTab(self.font_analysis_widget, "🔤 تحليل الخط")
        
        # تبويب تحليل الأحرف (إضافي)
        self.character_analysis_tab = CharacterAnalysisWidget()
        self.tabs.addTab(self.character_analysis_tab, "🔤 تحليل الأحرف")
        
        # تبويب الإحصائيات
        self.statistics_tab = StatisticsWidget()
        self.tabs.addTab(self.statistics_tab, "📊 الإحصائيات")
        
    def setup_chat_tab(self):
        """إعداد تبويب الشات الاحترافي"""
        layout = QVBoxLayout(self.chat_tab)
        
        # رسالة ترحيبية
        welcome_label = QLabel("مرحباً بك في الشات الاحترافي لتحليل النصوص القرآنية")
        welcome_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px;
            text-align: center;
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        # زر فتح الشات الاحترافي
        open_chat_btn = QPushButton("🚀 فتح الشات الاحترافي")
        open_chat_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 15px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                margin: 20px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #5a67d8 0%, #6b5b95 100%);
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #4c51bf 0%, #553c7b 100%);
            }
        """)
        open_chat_btn.clicked.connect(self.open_professional_chat)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(open_chat_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
    def create_main_toolbar(self):
        """إنشاء شريط الأدوات الرئيسي"""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.StyledPanel)
        toolbar_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
        """)
        
        layout = QHBoxLayout(toolbar_frame)
        
        # الشعار والعنوان
        title_label = QLabel("🕌 محلل النصوص القرآنية المتقدم")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #495057;
            padding: 5px 15px;
        """)
        
        layout.addWidget(title_label)
        layout.addStretch()
        
        # أزرار سريعة
        quick_chat_btn = QPushButton("💬 شات سريع")
        quick_analysis_btn = QPushButton("⚡ تحليل سريع")
        settings_btn = QPushButton("⚙️ الإعدادات")
        
        for btn in [quick_chat_btn, quick_analysis_btn, settings_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    margin: 2px;
                }
                QPushButton:hover {
                    background: #0056b3;
                }
            """)
        
        quick_chat_btn.clicked.connect(self.open_professional_chat)
        quick_analysis_btn.clicked.connect(self.quick_analysis)
        settings_btn.clicked.connect(self.open_settings)
        
        layout.addWidget(quick_chat_btn)
        layout.addWidget(quick_analysis_btn)
        layout.addWidget(settings_btn)
        
        return toolbar_frame
        
    def setup_menu_bar(self):
        """إعداد شريط القوائم"""
        menubar = self.menuBar()
        
        # قائمة الملف
        file_menu = menubar.addMenu('📁 ملف')
        
        open_action = QAction('📂 فتح ملف', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        
        save_action = QAction('💾 حفظ', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        
        exit_action = QAction('🚪 خروج', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # قائمة الأدوات
        tools_menu = menubar.addMenu('🔧 أدوات')
        
        chat_action = QAction('💬 الشات الاحترافي', self)
        chat_action.setShortcut('Ctrl+T')
        chat_action.triggered.connect(self.open_professional_chat)
        
        analysis_action = QAction('🔍 تحليل سريع', self)
        analysis_action.setShortcut('F5')
        analysis_action.triggered.connect(self.quick_analysis)
        
        tools_menu.addAction(chat_action)
        tools_menu.addAction(analysis_action)
        
        # قائمة المساعدة
        help_menu = menubar.addMenu('❓ مساعدة')
        
        about_action = QAction('ℹ️ حول البرنامج', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """إعداد شريط الحالة"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("جاهز للاستخدام - مرحباً بك في محلل النصوص القرآنية")
        
    def setup_shortcuts(self):
        """إعداد اختصارات لوحة المفاتيح"""
        # اختصار للشات الاحترافي
        QShortcut(QKeySequence("Ctrl+T"), self, self.open_professional_chat)
        
        # اختصار للتحليل السريع
        QShortcut(QKeySequence("F5"), self, self.quick_analysis)
        
    def open_professional_chat(self):
        """فتح نافذة الشات الاحترافي"""
        try:
            self.chat_window = ProfessionalChatWindow(self)
            self.chat_window.show()
            self.status_bar.showMessage("تم فتح الشات الاحترافي")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"لا يمكن فتح الشات الاحترافي: {str(e)}")
            
    def quick_analysis(self):
        """تحليل سريع للنص"""
        self.tabs.setCurrentIndex(1)  # الانتقال لتبويب بيانات القرآن
        self.status_bar.showMessage("تم الانتقال لتبويب التحليل السريع")
        
    def open_settings(self):
        """فتح نافذة الإعدادات"""
        QMessageBox.information(self, "الإعدادات", "نافذة الإعدادات قيد التطوير")
        
    def open_file(self):
        """فتح ملف"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "فتح ملف نصي", "", 
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.status_bar.showMessage(f"تم فتح الملف: {file_path}")
            
    def save_file(self):
        """حفظ الملف"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ الملف", "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.status_bar.showMessage(f"تم حفظ الملف: {file_path}")
            
    def show_about(self):
        """عرض معلومات حول البرنامج"""
        QMessageBox.about(self, "حول البرنامج", 
            "🕌 محلل النصوص القرآنية المتقدم\n\n"
            "إصدار 2.0 - OpenRouter Edition\n\n"
            "برنامج متقدم لتحليل النصوص القرآنية\n"
            "مع دعم الذكاء الاصطناعي عبر OpenRouter\n\n"
            "تطوير: فريق تطوير تطبيقات القرآن الكريم")


# تعيين الكلاس الجديد كبديل لـ QuranTextAnalyzer
QuranTextAnalyzer = QuranAnalysisMainWindow