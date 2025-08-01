#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ويدجات التحليل والإحصائيات
Analysis and statistics widgets for Quran Text Analyzer
"""

from shared_imports import *
from data_models import TextAnalysisResult


class CharacterAnalysisWidget(QWidget):
    """ويدجت تحليل الأحرف"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # عنوان
        title = QLabel("تحليل الأحرف والرموز")
        title.setStyleSheet(TITLE_STYLE)
        layout.addWidget(title)
        
        # جدول الأحرف
        self.char_table = QTableWidget()
        self.char_table.setColumnCount(5)
        self.char_table.setHorizontalHeaderLabels([
            "الحرف", "الترميز", "التكرار", "النسبة %", CHAR_TYPE_LABEL
        ])
        
        # تنسيق الجدول
        self.char_table.horizontalHeader().setStretchLastSection(True)
        self.char_table.setAlternatingRowColors(True)
        self.char_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        layout.addWidget(self.char_table)
        
    def display_analysis(self, analysis: TextAnalysisResult):
        """عرض نتائج التحليل"""
        # مسح الجدول
        self.char_table.setRowCount(0)
        
        # حساب العدد الكلي للأحرف
        total_chars = sum(analysis.character_frequencies.values())
        
        # ترتيب الأحرف حسب التكرار
        sorted_chars = sorted(
            analysis.character_frequencies.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # ملء الجدول
        for char, freq in sorted_chars:
            row = self.char_table.rowCount()
            self.char_table.insertRow(row)
            
            # الحرف
            char_item = QTableWidgetItem(char)
            char_item.setTextAlignment(Qt.AlignCenter)
            char_item.setFont(QFont("Arial", 16))
            self.char_table.setItem(row, 0, char_item)
            
            # الترميز Unicode
            unicode_item = QTableWidgetItem(f"U+{ord(char):04X}")
            unicode_item.setTextAlignment(Qt.AlignCenter)
            self.char_table.setItem(row, 1, unicode_item)
            
            # التكرار
            freq_item = QTableWidgetItem(str(freq))
            freq_item.setTextAlignment(Qt.AlignCenter)
            self.char_table.setItem(row, 2, freq_item)
            
            # النسبة المئوية
            percentage = (freq / total_chars) * 100
            percent_item = QTableWidgetItem(f"{percentage:.2f}%")
            percent_item.setTextAlignment(Qt.AlignCenter)
            self.char_table.setItem(row, 3, percent_item)
            
            # نوع الحرف
            char_type = self._get_char_type(char)
            type_item = QTableWidgetItem(char_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.char_table.setItem(row, 4, type_item)
            
            # تلوين حسب النوع
            color = self._get_type_color(char_type)
            for col in range(5):
                self.char_table.item(row, col).setBackground(QColor(color))
                
        # تحديث حجم الأعمدة
        self.char_table.resizeColumnsToContents()
        
    def _get_char_type(self, char: str) -> str:
        """تحديد نوع الحرف"""
        code = ord(char)
        
        # الحروف العربية الأساسية
        if 0x0621 <= code <= 0x063A:
            return ARABIC_CHAR_TYPE
        elif 0x0641 <= code <= 0x064A:
            return ARABIC_CHAR_TYPE
            
        # التشكيل
        elif 0x064B <= code <= 0x0652:
            return "تشكيل"
            
        # الأرقام العربية
        elif 0x0660 <= code <= 0x0669:
            return "رقم عربي"
            
        # علامات الوقف القرآنية
        elif code in [0x06D6, 0x06D7, 0x06D8, 0x06D9, 0x06DA, 0x06DB, 0x06DC]:
            return "علامة وقف"
            
        # رموز قرآنية خاصة
        elif 0x06D0 <= code <= 0x06ED:
            return "رمز قرآني"
            
        # مسافات وفواصل
        elif char in [' ', '\n', '\t']:
            return "مسافة"
            
        else:
            return "أخرى"
            
    def _get_type_color(self, char_type: str) -> str:
        """الحصول على لون حسب نوع الحرف"""
        colors = {
            "حرف عربي": "#e3f2fd",
            "تشكيل": "#f3e5f5", 
            "رقم عربي": "#e8f5e9",
            "علامة وقف": "#fff3e0",
            "رمز قرآني": "#fce4ec",
            "مسافة": "#f5f5f5",
            "أخرى": "#efebe9"
        }
        return colors.get(char_type, "#ffffff")


class StatisticsWidget(QWidget):
    """ويدجت الإحصائيات والرسوم البيانية"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # عنوان
        title = QLabel("الإحصائيات والتحليل البصري")
        title.setStyleSheet(TITLE_STYLE)
        layout.addWidget(title)
        
        # منطقة الرسوم البيانية - مع التحقق من توفر matplotlib Qt backend
        if MATPLOTLIB_QT_AVAILABLE:
            self.figure = Figure(figsize=(10, 8))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
        else:
            # عرض رسالة بديلة إذا لم تكن matplotlib Qt متاحة
            placeholder_label = QLabel("📊 الرسوم البيانية غير متاحة\n\nالرجاء التأكد من تثبيت matplotlib بشكل صحيح")
            placeholder_label.setAlignment(Qt.AlignCenter)
            placeholder_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #666;
                    background-color: #f8f9fa;
                    border: 2px dashed #ddd;
                    border-radius: 10px;
                    padding: 50px;
                    min-height: 300px;
                }
            """)
            layout.addWidget(placeholder_label)
            self.figure = None
            self.canvas = None
        
        # أزرار التحكم
        controls_layout = QHBoxLayout()
        
        self.chart_type = QComboBox()
        self.chart_type.addItems([
            "مخطط دائري - توزيع الأحرف",
            "مخطط أعمدة - تكرار الأحرف", 
            "مخطط خطي - توزيع الكلمات",
            "خريطة حرارية - مواضع الأحرف"
        ])
        self.chart_type.currentIndexChanged.connect(self.update_chart)
        
        controls_layout.addWidget(QLabel("نوع الرسم:"))
        controls_layout.addWidget(self.chart_type)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        self.analysis_result = None
        
    def set_analysis(self, analysis: TextAnalysisResult):
        """تعيين نتائج التحليل"""
        self.analysis_result = analysis
        self.update_chart()
        
    def update_chart(self):
        """تحديث الرسم البياني"""
        if not self.analysis_result or not MATPLOTLIB_QT_AVAILABLE:
            return
            
        self.figure.clear()
        
        chart_type = self.chart_type.currentIndex()
        
        if chart_type == 0:  # مخطط دائري
            self.draw_pie_chart()
        elif chart_type == 1:  # مخطط أعمدة
            self.draw_bar_chart()
        elif chart_type == 2:  # مخطط خطي
            self.draw_line_chart()
        elif chart_type == 3:  # خريطة حرارية
            self.draw_heatmap()
            
        self.canvas.draw()
        
    def draw_pie_chart(self):
        """رسم مخطط دائري لتوزيع الأحرف"""
        if not MATPLOTLIB_QT_AVAILABLE:
            return
            
        ax = self.figure.add_subplot(111)
        
        # أخذ أكثر 10 أحرف تكراراً
        sorted_chars = sorted(
            self.analysis_result.character_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        labels = []
        sizes = []
        
        for char, freq in sorted_chars:
            # معالجة النص العربي للعرض الصحيح
            reshaped_text = arabic_reshaper.reshape(char)
            bidi_text = get_display(reshaped_text)
            labels.append(bidi_text)
            sizes.append(freq)
            
        # إضافة "أخرى" للباقي
        other_count = sum(
            freq for char, freq in self.analysis_result.character_frequencies.items()
            if (char, freq) not in sorted_chars
        )
        if other_count > 0:
            labels.append("أخرى")
            sizes.append(other_count)
            
        # رسم المخطط - التحقق من توفر plt
        if plt is not None:
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        else:
            # استخدام ألوان افتراضية إذا لم يكن plt متاحاً
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc'] * (len(labels) // 5 + 1)
            colors = colors[:len(labels)]
            
        _, texts, autotexts = ax.pie(
            sizes, 
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90
        )
        
        # تحسين مظهر النص
        for text in texts:
            text.set_fontsize(12)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
            
        ax.set_title("توزيع الأحرف الأكثر تكراراً", fontsize=14, weight='bold')
        
    def draw_bar_chart(self):
        """رسم مخطط أعمدة لتكرار الأحرف"""
        if not MATPLOTLIB_QT_AVAILABLE:
            return
            
        ax = self.figure.add_subplot(111)
        
        # أخذ أكثر 20 حرف تكراراً
        sorted_chars = sorted(
            self.analysis_result.character_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        chars = []
        frequencies = []
        
        for char, freq in sorted_chars:
            reshaped_text = arabic_reshaper.reshape(char)
            bidi_text = get_display(reshaped_text)
            chars.append(bidi_text)
            frequencies.append(freq)
            
        # رسم الأعمدة
        bars = ax.bar(range(len(chars)), frequencies, color='steelblue')
        
        # تخصيص المحاور
        ax.set_xticks(range(len(chars)))
        ax.set_xticklabels(chars, rotation=45, ha='right')
        ax.set_xlabel('الحرف', fontsize=12)
        ax.set_ylabel('التكرار', fontsize=12)
        ax.set_title('تكرار الأحرف في النص', fontsize=14, weight='bold')
        
        # إضافة قيم على الأعمدة
        for bar, freq in zip(bars, frequencies):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., 
                height,
                f'{freq}',
                ha='center', 
                va='bottom',
                fontsize=8
            )
            
        # استخدام plt فقط إذا كان متاحاً
        if plt is not None:
            plt.tight_layout()
        
    def draw_line_chart(self):
        """رسم مخطط خطي لتوزيع طول الكلمات"""
        ax = self.figure.add_subplot(111)
        
        # تحليل أطوال الكلمات
        words = self.analysis_result.normalized_text.split()
        word_lengths = [len(word) for word in words]
        
        # حساب التوزيع
        length_counts = {}
        for length in word_lengths:
            length_counts[length] = length_counts.get(length, 0) + 1
            
        # ترتيب حسب الطول
        sorted_lengths = sorted(length_counts.items())
        
        lengths = [l for l, _ in sorted_lengths]
        counts = [c for _, c in sorted_lengths]
        
        # رسم الخط
        ax.plot(lengths, counts, 'o-', linewidth=2, markersize=8, color='darkgreen')
        ax.fill_between(lengths, counts, alpha=0.3, color='lightgreen')
        
        ax.set_xlabel('طول الكلمة (عدد الأحرف)', fontsize=12)
        ax.set_ylabel('عدد الكلمات', fontsize=12)
        ax.set_title('توزيع أطوال الكلمات', fontsize=14, weight='bold')
        ax.grid(True, alpha=0.3)
        
        # إضافة إحصائيات
        avg_length = np.mean(word_lengths)
        ax.axvline(avg_length, color='red', linestyle='--', label=f'المتوسط: {avg_length:.2f}')
        ax.legend()
        
    def draw_heatmap(self):
        """رسم خريطة حرارية لمواضع الأحرف"""
        ax = self.figure.add_subplot(111)
        
        # أخذ أكثر 10 أحرف تكراراً
        sorted_chars = sorted(
            self.analysis_result.character_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # تحليل مواضع الأحرف
        text = self.analysis_result.normalized_text
        position_matrix = []
        char_labels = []
        
        for char, _ in sorted_chars:
            positions = [i for i, c in enumerate(text) if c == char]
            # تقسيم النص إلى 20 قسم
            bins = np.histogram(positions, bins=20, range=(0, len(text)))[0]
            position_matrix.append(bins)
            
            reshaped_text = arabic_reshaper.reshape(char)
            bidi_text = get_display(reshaped_text)
            char_labels.append(bidi_text)
            
        # رسم الخريطة الحرارية
        im = ax.imshow(position_matrix, cmap='YlOrRd', aspect='auto')
        
        # تخصيص المحاور
        ax.set_yticks(range(len(char_labels)))
        ax.set_yticklabels(char_labels)
        ax.set_xlabel('موضع في النص (مقسم إلى 20 قسم)', fontsize=12)
        ax.set_ylabel('الحرف', fontsize=12)
        ax.set_title('خريطة حرارية لتوزيع مواضع الأحرف', fontsize=14, weight='bold')
        
        # إضافة شريط الألوان
        cbar = self.figure.colorbar(im, ax=ax)
        cbar.set_label('التكرار', rotation=270, labelpad=15)
