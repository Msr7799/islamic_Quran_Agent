#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أدوات SVG وأدوات المقارنة
SVG analysis tools and text comparison utilities
"""

from shared_imports import *
from data_models import SimpleTextProcessor, TextAnalysisResult


class SVGAnalyzerWidget(QWidget):
    """ويدجت تحليل ملفات SVG"""

    def __init__(self):
        super().__init__()
        self.current_svg_path = None
        self.setup_ui()

    def setup_ui(self):
        """إعداد واجهة تحليل SVG"""
        layout = QVBoxLayout(self)

        # عنوان
        title = QLabel("🖼️ تحليل ملفات SVG")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 15px;
            background: linear-gradient(90deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        # منطقة تحميل الملف
        file_group = QGroupBox("تحميل ملف SVG")
        file_layout = QVBoxLayout(file_group)

        # شريط أدوات الملف
        file_toolbar = QHBoxLayout()

        self.file_path_label = QLabel("لم يتم اختيار ملف")
        self.file_path_label.setStyleSheet("""
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            color: #6c757d;
        """)

        browse_btn = QPushButton("📁 اختيار ملف SVG")
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        browse_btn.clicked.connect(self.browse_svg_file)

        analyze_btn = QPushButton("🔍 تحليل الملف")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_svg)

        file_toolbar.addWidget(self.file_path_label, 1)
        file_toolbar.addWidget(browse_btn)
        file_toolbar.addWidget(analyze_btn)

        file_layout.addLayout(file_toolbar)
        layout.addWidget(file_group)

        # تبويبات النتائج
        self.results_tabs = QTabWidget()

        # تبويب معلومات عامة
        self.info_widget = QTextBrowser()
        self.info_widget.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
        """)
        self.results_tabs.addTab(self.info_widget, "📊 معلومات عامة")

        # تبويب النصوص المستخرجة
        self.texts_table = QTableWidget()
        self.texts_table.setColumnCount(5)
        self.texts_table.setHorizontalHeaderLabels([
            "النص", "الإحداثيات X", "الإحداثيات Y", "العرض", "الارتفاع"
        ])
        self.texts_table.horizontalHeader().setStretchLastSection(True)
        self.texts_table.setAlternatingRowColors(True)
        self.results_tabs.addTab(self.texts_table, "📝 النصوص المستخرجة")

        # تبويب العناصر
        self.elements_tree = QTreeWidget()
        self.elements_tree.setHeaderLabels(["العنصر", CHAR_TYPE_LABEL, "الخصائص"])
        self.results_tabs.addTab(self.elements_tree, "🏗️ هيكل العناصر")

        # تبويب الإحصائيات
        self.stats_widget = QTextBrowser()
        self.stats_widget.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Arial Unicode MS', 'Tahoma';
            }
        """)
        self.results_tabs.addTab(self.stats_widget, "📈 إحصائيات")

        layout.addWidget(self.results_tabs)

        # شريط الحالة
        self.svg_status = QLabel("جاهز لتحليل ملفات SVG")
        self.svg_status.setStyleSheet("""
            color: #6c757d;
            font-size: 12px;
            padding: 5px;
        """)
        layout.addWidget(self.svg_status)

    def browse_svg_file(self):
        """اختيار ملف SVG"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "اختيار ملف SVG",
            "pages_svgs/",
            "SVG Files (*.svg);;All Files (*)"
        )

        if file_path:
            self.current_svg_path = file_path
            self.file_path_label.setText(os.path.basename(file_path))
            self.file_path_label.setStyleSheet("""
                padding: 10px;
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 5px;
                color: #155724;
            """)
            self.svg_status.setText(f"تم اختيار: {os.path.basename(file_path)}")

    def analyze_svg(self):
        """تحليل ملف SVG"""
        if not self.current_svg_path:
            QMessageBox.warning(self, WARNING_TITLE, "يرجى اختيار ملف SVG أولاً")
            return

        if not os.path.exists(self.current_svg_path):
            QMessageBox.warning(self, "خطأ", "الملف المحدد غير موجود")
            return

        self.svg_status.setText("🔍 جاري تحليل الملف...")
        QApplication.processEvents()

        try:
            # تحليل الملف
            analysis_result = self.perform_svg_analysis(self.current_svg_path)

            # عرض النتائج
            self.display_svg_results(analysis_result)

            self.svg_status.setText("✅ تم التحليل بنجاح")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحليل الملف:\n{str(e)}")
            self.svg_status.setText("❌ فشل التحليل")

    def perform_svg_analysis(self, svg_path):
        """تنفيذ تحليل SVG"""
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()

            # جمع المعلومات
            analysis = {
                'file_path': svg_path,
                'file_size': os.path.getsize(svg_path),
                'root_tag': root.tag,
                'namespaces': dict(root.attrib) if root.attrib else {},
                'elements': [],
                'texts': [],
                'statistics': {}
            }

            # تحليل العناصر
            element_counts = {}
            text_elements = []

            for elem in root.iter():
                # إحصاء العناصر
                tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                element_counts[tag_name] = element_counts.get(tag_name, 0) + 1

                # جمع معلومات العنصر
                element_info = {
                    'tag': tag_name,
                    'attributes': dict(elem.attrib),
                    'text': elem.text.strip() if elem.text else None
                }
                analysis['elements'].append(element_info)

                # استخراج النصوص
                if elem.tag.endswith('use') and 'data-text' in elem.attrib:
                    text_content = elem.get('data-text', '')
                    transform = elem.get('transform', '')

                    if text_content.strip():
                        # استخراج الإحداثيات
                        coords = self.extract_coordinates_from_transform(transform)

                        text_info = {
                            'text': self.decode_html_entities(text_content),
                            'x': coords.get('x', 0),
                            'y': coords.get('y', 0),
                            'width': coords.get('width', 0),
                            'height': coords.get('height', 0),
                            'transform': transform
                        }
                        text_elements.append(text_info)

                elif elem.text and elem.text.strip():
                    # نصوص عادية
                    text_info = {
                        'text': elem.text.strip(),
                        'x': elem.get('x', 0),
                        'y': elem.get('y', 0),
                        'width': 0,
                        'height': 0,
                        'transform': elem.get('transform', '')
                    }
                    text_elements.append(text_info)

            analysis['texts'] = text_elements
            analysis['statistics'] = {
                'total_elements': len(analysis['elements']),
                'element_types': len(element_counts),
                'element_counts': element_counts,
                'text_elements': len(text_elements),
                'total_characters': sum(len(t['text']) for t in text_elements),
                'file_size_kb': round(analysis['file_size'] / 1024, 2)
            }

            return analysis

        except Exception as e:
            print(f"خطأ في تحليل {svg_path}: {e}")
            return {}

    def extract_coordinates_from_transform(self, transform_str):
        """استخراج الإحداثيات من transform"""
        coords = {'x': 0, 'y': 0, 'width': 0, 'height': 0}

        if not transform_str:
            return coords

        try:
            # البحث عن translate
            translate_match = re.search(r'translate\(([^)]+)\)', transform_str)
            if translate_match:
                values = translate_match.group(1).split(',')
                if len(values) >= 2:
                    coords['x'] = float(values[0].strip())
                    coords['y'] = float(values[1].strip())

            # البحث عن scale للحجم
            scale_match = re.search(r'scale\(([^)]+)\)', transform_str)
            if scale_match:
                values = scale_match.group(1).split(',')
                if len(values) >= 2:
                    coords['width'] = float(values[0].strip()) * 10  # تقدير
                    coords['height'] = float(values[1].strip()) * 10  # تقدير

        except Exception:
            pass

        return coords

    def decode_html_entities(self, text):
        """تحويل HTML entities إلى نص عربي"""
        import html
        try:
            # تحويل HTML entities
            decoded = html.unescape(text)

            # تحويل الترميز العددي
            def replace_numeric(match):
                try:
                    return chr(int(match.group(1)))
                except:
                    return match.group(0)

            decoded = re.sub(r'&#(\d+);', replace_numeric, decoded)

            return decoded
        except:
            return text

    def display_svg_results(self, analysis):
        """عرض نتائج التحليل"""
        # المعلومات العامة
        info_html = f"""
        <h2>📊 معلومات ملف SVG</h2>

        <h3>📁 معلومات الملف:</h3>
        <ul>
            <li><b>المسار:</b> {analysis['file_path']}</li>
            <li><b>الحجم:</b> {analysis['statistics']['file_size_kb']} KB</li>
            <li><b>العنصر الجذر:</b> {analysis['root_tag']}</li>
        </ul>

        <h3>📈 الإحصائيات:</h3>
        <ul>
            <li><b>إجمالي العناصر:</b> {analysis['statistics']['total_elements']}</li>
            <li><b>أنواع العناصر:</b> {analysis['statistics']['element_types']}</li>
            <li><b>عناصر النص:</b> {analysis['statistics']['text_elements']}</li>
            <li><b>إجمالي الأحرف:</b> {analysis['statistics']['total_characters']}</li>
        </ul>

        <h3>🏗️ أنواع العناصر:</h3>
        <ul>
        """

        for element_type, count in analysis['statistics']['element_counts'].items():
            info_html += f"<li><b>{element_type}:</b> {count}</li>"

        info_html += "</ul>"

        self.info_widget.setHtml(info_html)

        # جدول النصوص
        self.texts_table.setRowCount(len(analysis['texts']))

        for i, text_info in enumerate(analysis['texts']):
            self.texts_table.setItem(i, 0, QTableWidgetItem(text_info['text'][:50]))
            self.texts_table.setItem(i, 1, QTableWidgetItem(str(text_info['x'])))
            self.texts_table.setItem(i, 2, QTableWidgetItem(str(text_info['y'])))
            self.texts_table.setItem(i, 3, QTableWidgetItem(str(text_info['width'])))
            self.texts_table.setItem(i, 4, QTableWidgetItem(str(text_info['height'])))

        # شجرة العناصر
        self.elements_tree.clear()

        for element in analysis['elements'][:100]:  # أول 100 عنصر
            item = QTreeWidgetItem([
                element['tag'],
                'عنصر SVG',
                f"{len(element['attributes'])} خاصية"
            ])

            # إضافة الخصائص كعناصر فرعية
            for attr_name, attr_value in element['attributes'].items():
                attr_item = QTreeWidgetItem([
                    attr_name,
                    'خاصية',
                    str(attr_value)[:50]
                ])
                item.addChild(attr_item)

            self.elements_tree.addTopLevelItem(item)

        # الإحصائيات المفصلة
        stats_html = f"""
        <h2>📈 إحصائيات مفصلة</h2>

        <h3>📊 توزيع العناصر:</h3>
        <table border="1" style="width:100%; border-collapse: collapse;">
            <tr style="background-color: #f8f9fa;">
                <th>نوع العنصر</th>
                <th>العدد</th>
                <th>النسبة</th>
            </tr>
        """

        total_elements = analysis['statistics']['total_elements']
        for element_type, count in sorted(analysis['statistics']['element_counts'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_elements) * 100 if total_elements > 0 else 0
            stats_html += f"""
            <tr>
                <td>{element_type}</td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
            """

        stats_html += "</table>"

        # إحصائيات النصوص
        if analysis['texts']:
            avg_text_length = sum(len(t['text']) for t in analysis['texts']) / len(analysis['texts'])
            stats_html += f"""

            <h3>📝 إحصائيات النصوص:</h3>
            <ul>
                <li><b>متوسط طول النص:</b> {avg_text_length:.1f} حرف</li>
                <li><b>أطول نص:</b> {max(len(t['text']) for t in analysis['texts'])} حرف</li>
                <li><b>أقصر نص:</b> {min(len(t['text']) for t in analysis['texts'])} حرف</li>
            </ul>
            """

        self.stats_widget.setHtml(stats_html)


class ComparisonWidget(QWidget):
    """ويدجت مقارنة النصوص"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # عنوان
        title = QLabel(COMPARE_TEXTS_TITLE)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # منطقة النصوص
        text_layout = QHBoxLayout()
        
        # النص الأول
        text1_group = QGroupBox("النص المرجعي")
        text1_layout = QVBoxLayout(text1_group)
        self.text1_edit = QTextEdit()
        self.text1_edit.setStyleSheet("""
            QTextEdit {
                font-size: 16px;
                font-family: 'Arial Unicode MS', 'Tahoma';
                line-height: 1.5;
            }
        """)
        text1_layout.addWidget(self.text1_edit)
        
        # النص الثاني
        text2_group = QGroupBox("النص المستخرج")
        text2_layout = QVBoxLayout(text2_group)
        self.text2_edit = QTextEdit()
        self.text2_edit.setStyleSheet("""
            QTextEdit {
                font-size: 16px;
                font-family: 'Arial Unicode MS', 'Tahoma';
                line-height: 1.5;
            }
        """)
        text2_layout.addWidget(self.text2_edit)
        
        text_layout.addWidget(text1_group)
        text_layout.addWidget(text2_group)
        
        layout.addLayout(text_layout)
        
        # أزرار التحكم
        controls_layout = QHBoxLayout()
        
        compare_btn = QPushButton(COMPARE_TEXTS_TITLE)
        compare_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        compare_btn.clicked.connect(self.compare_texts)
        
        clear_btn = QPushButton("مسح")
        clear_btn.clicked.connect(self.clear_texts)
        
        controls_layout.addWidget(compare_btn)
        controls_layout.addWidget(clear_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # منطقة النتائج
        self.results_text = QTextBrowser()
        self.results_text.setMaximumHeight(200)
        layout.addWidget(self.results_text)
        
    def compare_texts(self):
        """مقارنة النصين"""
        text1 = self.text1_edit.toPlainText().strip()
        text2 = self.text2_edit.toPlainText().strip()
        
        if not text1 or not text2:
            QMessageBox.warning(self, WARNING_TITLE, "الرجاء إدخال النصين للمقارنة")
            return
            
        # استخدام معالج النصوص للمقارنة
        processor = SimpleTextProcessor()

        # تطبيع النصوص
        norm_text1 = processor.normalize_arabic(text1)
        norm_text2 = processor.normalize_arabic(text2)

        # حساب التشابه
        similarity = processor.calculate_similarity(norm_text1, norm_text2)
        
        # إيجاد الاختلافات
        import difflib
        differ = difflib.unified_diff(
            norm_text1.split(),
            norm_text2.split(),
            lineterm='',
            fromfile='النص المرجعي',
            tofile='النص المستخرج'
        )
        
        # عرض النتائج
        results_html = f"""
        <h3>نتائج المقارنة:</h3>
        <p><b>نسبة التشابه:</b> {similarity:.2%}</p>
        <p><b>عدد أحرف النص المرجعي:</b> {len(text1)}</p>
        <p><b>عدد أحرف النص المستخرج:</b> {len(text2)}</p>
        <p><b>الفرق في عدد الأحرف:</b> {abs(len(text1) - len(text2))}</p>
        """
        
        # إضافة الاختلافات إن وجدت
        if similarity < 1.0:
            results_html += "<h4>الاختلافات:</h4><pre style='font-family: monospace;'>"
            for line in list(differ)[:20]:  # أول 20 اختلاف
                if line.startswith('+'):
                    results_html += f"<span style='color: green;'>{line}</span><br/>"
                elif line.startswith('-'):
                    results_html += f"<span style='color: red;'>{line}</span><br/>"
                else:
                    results_html += f"{line}<br/>"
            results_html += "</pre>"
            
        self.results_text.setHtml(results_html)
        
        # تمييز الاختلافات في النصوص
        self.highlight_differences(text1, text2)
        
    def highlight_differences(self, text1: str, text2: str):
        """تمييز الاختلافات بين النصين"""
        # This is a simplified version - a full implementation would use
        # more sophisticated diff algorithms
        
        # تمييز النص الأول
        cursor1 = self.text1_edit.textCursor()
        cursor1.select(QTextCursor.Document)
        cursor1.setCharFormat(QTextCharFormat())  # مسح التنسيق السابق
        
        # تمييز النص الثاني  
        cursor2 = self.text2_edit.textCursor()
        cursor2.select(QTextCursor.Document)
        cursor2.setCharFormat(QTextCharFormat())  # مسح التنسيق السابق
        
        # يمكن إضافة خوارزمية أكثر تطوراً لتمييز الاختلافات الفعلية
        
    def clear_texts(self):
        """مسح النصوص"""
        self.text1_edit.clear()
        self.text2_edit.clear()
        self.results_text.clear()
