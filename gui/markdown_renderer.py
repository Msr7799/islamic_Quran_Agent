#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محرك عرض Markdown متطور مع دعم CodeBlock
Advanced Markdown Renderer with CodeBlock Support
مستوحى من ملف TSX المرفق لتوفير تجربة مستخدم متميزة
"""

import re
import os
import json
import html
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from shared_imports import *

class SyntaxHighlighter:
    """محرك Syntax Highlighting متطور"""
    
    # قاموس الألوان للغات المختلفة
    LANGUAGE_COLORS = {
        'python': {
            'keyword': '#ff7f50',  # أحمر برتقالي
            'string': '#98fb98',   # أخضر فاتح  
            'comment': '#87ceeb',  # أزرق سماوي
            'number': '#dda0dd',   # بنفسجي فاتح
            'function': '#f0e68c', # أصفر فاتح
            'class': '#ffa07a',    # سالمون فاتح
            'operator': '#ffffff', # أبيض
            'variable': '#e6e6fa'  # بنفسجي شاحب
        },
        'javascript': {
            'keyword': '#569cd6',  # أزرق
            'string': '#ce9178',   # بني فاتح
            'comment': '#6a994e', # أخضر
            'number': '#b5cea8',   # أخضر فاتح
            'function': '#dcdcaa', # أصفر فاتح
            'class': '#4ec9b0',    # سماوي
            'operator': '#d4d4d4', # رمادي فاتح
            'variable': '#9cdcfe'  # أزرق فاتح
        },
        'json': {
            'key': '#92c5f8',      # أزرق فاتح
            'string': '#ce9178',   # بني فاتح
            'number': '#b5cea8',   # أخضر فاتح
            'boolean': '#569cd6',  # أزرق
            'null': '#ff6b6b'      # أحمر فاتح
        },
        'html': {
            'tag': '#569cd6',      # أزرق
            'attribute': '#92c5f8', # أزرق فاتح
            'string': '#ce9178',   # بني فاتح
            'text': '#d4d4d4'      # رمادي فاتح
        },
        'css': {
            'selector': '#d7ba7d', # ذهبي
            'property': '#92c5f8', # أزرق فاتح
            'value': '#ce9178',    # بني فاتح
            'important': '#ff6b6b' # أحمر فاتح
        }
    }
    
    # قواميس الكلمات المفتاحية
    KEYWORDS = {
        'python': [
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'return',
            'import', 'from', 'try', 'except', 'finally', 'with', 'as',
            'async', 'await', 'yield', 'True', 'False', 'None', 'and',
            'or', 'not', 'is', 'in', 'pass', 'break', 'continue', 'lambda',
            'global', 'nonlocal', 'del', 'assert', 'raise'
        ],
        'javascript': [
            'function', 'var', 'let', 'const', 'if', 'else', 'for', 'while',
            'return', 'import', 'export', 'default', 'class', 'extends',
            'super', 'this', 'new', 'try', 'catch', 'finally', 'throw',
            'async', 'await', 'yield', 'true', 'false', 'null', 'undefined',
            'typeof', 'instanceof', 'in', 'of', 'do', 'switch', 'case',
            'break', 'continue', 'debugger', 'with'
        ]
    }
    
    @classmethod
    def highlight_line(cls, line: str, language: str) -> str:
        """تطبيق syntax highlighting على سطر واحد"""
        language = language.lower()
        
        if language == 'python':
            return cls._highlight_python(line)
        elif language in ['javascript', 'js']:
            return cls._highlight_javascript(line)
        elif language == 'json':
            return cls._highlight_json(line)
        elif language in ['html', 'htm']:
            return cls._highlight_html(line)
        elif language == 'css':
            return cls._highlight_css(line)
        else:
            return cls._escape_html(line)
    
    @classmethod
    def _highlight_python(cls, line: str) -> str:
        """تطبيق highlighting للبايثون"""
        colors = cls.LANGUAGE_COLORS['python']
        
        # التعامل مع التعليقات أولاً
        if line.strip().startswith('#'):
            return f'<span style="color: {colors["comment"]}; font-style: italic;">{cls._escape_html(line)}</span>'
        
        # التعامل مع النصوص
        line = cls._highlight_strings(line, colors['string'])
        
        # التعامل مع الكلمات المفتاحية
        for keyword in cls.KEYWORDS['python']:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            replacement = f'<span style="color: {colors["keyword"]}; font-weight: bold;">{keyword}</span>'
            line = re.sub(pattern, replacement, line)
        
        # التعامل مع الأرقام
        line = re.sub(r'\b\d+\.?\d*\b', 
                     f'<span style="color: {colors["number"]}">' + r'\g<0>' + '</span>', line)
        
        # التعامل مع الدوال
        line = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                     f'<span style="color: {colors["function"]}">' + r'\g<1>' + '</span>(', line)
        
        return line
    
    @classmethod
    def _highlight_javascript(cls, line: str) -> str:
        """تطبيق highlighting للجافاسكريبت"""
        colors = cls.LANGUAGE_COLORS['javascript']
        
        # التعامل مع التعليقات
        if line.strip().startswith('//'):
            return f'<span style="color: {colors["comment"]}; font-style: italic;">{cls._escape_html(line)}</span>'
        
        # التعامل مع النصوص
        line = cls._highlight_strings(line, colors['string'])
        
        # التعامل مع الكلمات المفتاحية
        for keyword in cls.KEYWORDS['javascript']:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            replacement = f'<span style="color: {colors["keyword"]}; font-weight: bold;">{keyword}</span>'
            line = re.sub(pattern, replacement, line)
        
        return line
    
    @classmethod
    def _highlight_json(cls, line: str) -> str:
        """تطبيق highlighting للJSON"""
        colors = cls.LANGUAGE_COLORS['json']
        
        # المفاتيح
        line = re.sub(r'"([^"]*)"(\s*:)',
                     f'<span style="color: {colors["key"]}">"' + r'\g<1>' + '"</span>' + r'\g<2>', line)
        
        # القيم النصية
        line = re.sub(r':\s*"([^"]*)"',
                     f': <span style="color: {colors["string"]}">"' + r'\g<1>' + '"</span>', line)
        
        # الأرقام
        line = re.sub(r'\b\d+\.?\d*\b',
                     f'<span style="color: {colors["number"]}">' + r'\g<0>' + '</span>', line)
        
        # القيم المنطقية و null
        for val, color_key in [('true', 'boolean'), ('false', 'boolean'), ('null', 'null')]:
            line = re.sub(r'\b' + val + r'\b',
                         f'<span style="color: {colors[color_key]}">{val}</span>', line)
        
        return line
    
    @classmethod
    def _highlight_html(cls, line: str) -> str:
        """تطبيق highlighting للHTML"""
        colors = cls.LANGUAGE_COLORS['html']
        
        # العلامات
        line = re.sub(r'<(/?)([^>]+)>',
                     f'<span style="color: {colors["tag"]}">&lt;' + r'\g<1>' + r'\g<2>' + '&gt;</span>', line)
        
        return line
    
    @classmethod
    def _highlight_css(cls, line: str) -> str:
        """تطبيق highlighting للCSS"""
        colors = cls.LANGUAGE_COLORS['css']
        
        # المحددات
        line = re.sub(r'^([^{]+)\s*{',
                     f'<span style="color: {colors["selector"]}">' + r'\g<1>' + '</span> {', line)
        
        # الخصائص
        line = re.sub(r'([^:]+):',
                     f'<span style="color: {colors["property"]}">' + r'\g<1>' + '</span>:', line)
        
        return line
    
    @classmethod
    def _highlight_strings(cls, line: str, color: str) -> str:
        """تمييز النصوص بين الاقتباسات"""
        # نصوص بين اقتباسات مفردة
        line = re.sub(r"'([^']*)'",
                     f'<span style="color: {color}">\'' + r'\g<1>' + '\'</span>', line)
        
        # نصوص بين اقتباسات مزدوجة
        line = re.sub(r'"([^"]*)"',
                     f'<span style="color: {color}">&quot;' + r'\g<1>' + '&quot;</span>', line)
        
        return line
    
    @classmethod
    def _escape_html(cls, text: str) -> str:
        """تشفير HTML للنص العادي"""
        return html.escape(text)


class CodeBlockWidget(QWidget):
    """ويدجت CodeBlock متطور مع جميع الميزات"""
    
    # إشارات مخصصة
    codeEdited = pyqtSignal(str, str)  # original_code, edited_code
    copyRequested = pyqtSignal(str)    # code
    downloadRequested = pyqtSignal(str, str)  # code, language
    
    # قاموس امتدادات الملفات
    FILE_EXTENSIONS = {
        'python': 'py', 'javascript': 'js', 'typescript': 'ts',
        'html': 'html', 'css': 'css', 'json': 'json',
        'java': 'java', 'cpp': 'cpp', 'c': 'c', 'csharp': 'cs',
        'php': 'php', 'ruby': 'rb', 'go': 'go', 'rust': 'rs',
        'kotlin': 'kt', 'swift': 'swift', 'xml': 'xml',
        'yaml': 'yml', 'markdown': 'md', 'bash': 'sh',
        'sql': 'sql', 'r': 'r', 'matlab': 'm'
    }
    
    # معلومات اللغات مع الأيقونات والألوان
    LANGUAGE_INFO = {
        'python': {'name': 'Python', 'icon': '🐍', 'color': '#3776ab'},
        'javascript': {'name': 'JavaScript', 'icon': '⚡', 'color': '#f7df1e'},
        'typescript': {'name': 'TypeScript', 'icon': '🔷', 'color': '#3178c6'},
        'html': {'name': 'HTML', 'icon': '🌐', 'color': '#e34c26'},
        'css': {'name': 'CSS', 'icon': '🎨', 'color': '#1572b6'},
        'json': {'name': 'JSON', 'icon': '📄', 'color': '#00d2ff'},
        'markdown': {'name': 'Markdown', 'icon': '📝', 'color': '#083fa1'},
        'bash': {'name': 'Bash', 'icon': '💻', 'color': '#4eaa25'},
        'sql': {'name': 'SQL', 'icon': '🗃️', 'color': '#336791'},
    }
    
    def __init__(self, code: str, language: str = 'text', parent=None):
        super().__init__(parent)
        self.original_code = code
        self.current_code = code
        self.language = language.lower()
        self.is_editing = False
        self.is_expanded = False
        self.is_fullscreen = False
        
        # حساب عدد الأسطر
        self.lines = code.split('\n')
        self.line_count = len(self.lines)
        self.should_truncate = self.line_count > 20
        
        # إعداد الواجهة
        self.setup_ui()
        self.setup_shortcuts()
        
        # متغيرات التحكم في النسخ
        self.copy_success_timer = QTimer()
        self.copy_success_timer.setSingleShot(True)
        self.copy_success_timer.timeout.connect(self.hide_copy_success)
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # إنشاء الحاوية الرئيسية
        self.container = QFrame()
        self.container.setFrameStyle(QFrame.Box)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
            }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # إنشاء شريط الرأس
        self.create_header()
        container_layout.addWidget(self.header)
        
        # إنشاء منطقة المحتوى
        self.create_content_area()
        container_layout.addWidget(self.content_area)
        
        main_layout.addWidget(self.container)
        
        # رسائل الحالة
        self.create_status_messages()
        
    def create_header(self):
        """إنشاء شريط رأس CodeBlock"""
        self.header = QFrame()
        self.header.setFixedHeight(60)
        self.header.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: none;
                border-bottom: 1px solid #3c3c3c;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        # منطقة اليسار - نقاط التحكم ومعلومات اللغة
        left_section = QWidget()
        left_layout = QHBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # نقاط التحكم (macOS style)
        dots_widget = QWidget()
        dots_layout = QHBoxLayout(dots_widget)
        dots_layout.setContentsMargins(0, 0, 0, 0)
        dots_layout.setSpacing(8)
        
        for color in ['#ff5f57', '#ffbd2e', '#28ca42']:
            dot = QLabel()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    border-radius: 6px;
                }}
            """)
            dots_layout.addWidget(dot)
        
        # معلومات اللغة
        self.create_language_info()
        
        left_layout.addWidget(dots_widget)
        left_layout.addWidget(self.language_badge)
        if self.line_count > 1:
            left_layout.addWidget(self.lines_badge)
        left_layout.addStretch()
        
        # منطقة اليمين - أزرار التحكم
        right_section = QWidget()
        right_layout = QHBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        self.create_control_buttons(right_layout)
        
        header_layout.addWidget(left_section)
        header_layout.addStretch()
        header_layout.addWidget(right_section)
        
    def create_language_info(self):
        """إنشاء شارة معلومات اللغة"""
        lang_info = self.LANGUAGE_INFO.get(self.language, {
            'name': self.language.upper(),
            'icon': '📄',
            'color': '#888888'
        })
        
        # شارة اللغة
        self.language_badge = QFrame()
        self.language_badge.setStyleSheet("""
            QFrame {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 15px;
                padding: 5px 10px;
            }
        """)
        
        badge_layout = QHBoxLayout(self.language_badge)
        badge_layout.setContentsMargins(8, 4, 8, 4)
        badge_layout.setSpacing(6)
        
        # أيقونة اللغة
        icon_label = QLabel(lang_info['icon'])
        icon_label.setStyleSheet("font-size: 14px;")
        
        # اسم اللغة
        name_label = QLabel(lang_info['name'])
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {lang_info['color']};
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        
        badge_layout.addWidget(icon_label)
        badge_layout.addWidget(name_label)
        
        # شارة عدد الأسطر
        if self.line_count > 1:
            self.lines_badge = QLabel(f"{self.line_count} lines")
            self.lines_badge.setStyleSheet("""
                QLabel {
                    color: #cccccc;
                    background-color: #404040;
                    border: 1px solid #555555;
                    border-radius: 10px;
                    padding: 4px 8px;
                    font-size: 11px;
                }
            """)
        
    def create_control_buttons(self, layout):
        """إنشاء أزرار التحكم"""
        
        # زر التوسع (إذا كان الكود طويل)
        if self.should_truncate:
            self.expand_btn = self.create_button(
                "👁️" if not self.is_expanded else "🙈",
                "عرض كامل" if not self.is_expanded else "إخفاء",
                self.toggle_expand
            )
            layout.addWidget(self.expand_btn)
        
        # زر ملء الشاشة
        self.fullscreen_btn = self.create_button(
            "⛶" if not self.is_fullscreen else "⚏",
            "ملء الشاشة" if not self.is_fullscreen else "تصغير",
            self.toggle_fullscreen
        )
        layout.addWidget(self.fullscreen_btn)
        
        # زر التحرير
        self.edit_btn = self.create_button(
            "✏️" if not self.is_editing else "💾",
            "تحرير" if not self.is_editing else "حفظ",
            self.toggle_edit
        )
        layout.addWidget(self.edit_btn)
        
        # زر النسخ
        self.copy_btn = self.create_button(
            "📋", "نسخ", self.copy_code
        )
        layout.addWidget(self.copy_btn)
        
        # زر التحميل
        self.download_btn = self.create_button(
            "⬇️", "تحميل", self.download_code
        )
        layout.addWidget(self.download_btn)
        
        # زر المعاينة (للHTML فقط)
        if self.language in ['html', 'htm']:
            self.preview_btn = self.create_button(
                "👁️", "معاينة", self.preview_html
            )
            layout.addWidget(self.preview_btn)
    
    def create_button(self, icon: str, tooltip: str, callback) -> QPushButton:
        """إنشاء زر تحكم مخصص"""
        btn = QPushButton(icon)
        btn.setFixedSize(32, 32)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 6px;
                color: #cccccc;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
        """)
        btn.clicked.connect(callback)
        return btn
    
    def create_content_area(self):
        """إنشاء منطقة المحتوى"""
        self.content_area = QWidget()
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # إنشاء منطقة الكود
        self.create_code_area()
        content_layout.addWidget(self.code_area)
        
        # إنشاء محرر النصوص (مخفي افتراضياً)
        self.create_editor()
        content_layout.addWidget(self.editor)
        self.editor.hide()
        
    def create_code_area(self):
        """إنشاء منطقة عرض الكود"""
        self.code_area = QScrollArea()
        self.code_area.setWidgetResizable(True)
        self.code_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.code_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.code_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
        """)
        
        # ويدجت المحتوى
        self.code_widget = QWidget()
        self.code_layout = QVBoxLayout(self.code_widget)
        self.code_layout.setContentsMargins(20, 15, 20, 15)
        self.code_layout.setSpacing(0)
        
        self.render_code()
        self.code_area.setWidget(self.code_widget)
    
    def create_editor(self):
        """إنشاء محرر النصوص"""
        self.editor = QTextEdit()
        self.editor.setPlainText(self.current_code)
        self.editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: none;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
                padding: 15px;
            }
        """)
        
        # إعداد الخط
        font = QFont('Consolas', 13)
        font.setFixedPitch(True)
        self.editor.setFont(font)
        
    def render_code(self):
        """عرض الكود مع syntax highlighting"""
        # تنظيف التخطيط السابق
        while self.code_layout.count():
            child = self.code_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # تحديد الأسطر المراد عرضها
        lines_to_show = self.lines
        if self.should_truncate and not self.is_expanded and not self.is_fullscreen:
            lines_to_show = self.lines[:20]
        
        # إنشاء container للأسطر
        lines_container = QWidget()
        lines_layout = QVBoxLayout(lines_container)
        lines_layout.setContentsMargins(0, 0, 0, 0)
        lines_layout.setSpacing(2)
        
        # عرض كل سطر
        for i, line in enumerate(lines_to_show):
            line_widget = self.create_line_widget(i + 1, line)
            lines_layout.addWidget(line_widget)
        
        self.code_layout.addWidget(lines_container)
        
        # إضافة زر "عرض المزيد" إذا كان مقطوع
        if self.should_truncate and not self.is_expanded and not self.is_fullscreen:
            self.create_show_more_button()
    
    def create_line_widget(self, line_number: int, line_content: str) -> QWidget:
        """إنشاء ويدجت لسطر واحد"""
        line_widget = QWidget()
        line_widget.setStyleSheet("""
            QWidget:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)
        
        line_layout = QHBoxLayout(line_widget)
        line_layout.setContentsMargins(0, 2, 0, 2)
        line_layout.setSpacing(15)
        
        # رقم السطر
        line_num_label = QLabel(f"{line_number:3d}")
        line_num_label.setStyleSheet("""
            QLabel {
                color: #6e7681;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                min-width: 30px;
                padding-right: 10px;
            }
        """)
        line_num_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
        # محتوى السطر مع syntax highlighting
        highlighted_content = SyntaxHighlighter.highlight_line(line_content, self.language)
        
        content_label = QLabel()
        content_label.setText(highlighted_content)
        content_label.setTextFormat(Qt.RichText)
        content_label.setWordWrap(False)
        content_label.setStyleSheet("""
            QLabel {
                color: #e6edf3;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
                padding: 1px 0;
            }
        """)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        line_layout.addWidget(line_num_label)
        line_layout.addWidget(content_label, 1)
        
        return line_widget
    
    def create_show_more_button(self):
        """إنشاء زر عرض المزيد"""
        remaining_lines = self.line_count - 20
        
        button_container = QWidget()
        button_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 30, 30, 0),
                    stop:0.7 rgba(30, 30, 30, 0.8),
                    stop:1 rgba(30, 30, 30, 1));
                padding: 20px;
            }
        """)
        
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 20, 0, 10)
        
        show_more_btn = QPushButton(f"👁️ عرض {remaining_lines} سطر إضافي")
        show_more_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0969da, stop:1 #8b5cf6);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0860ca, stop:1 #7c3aed);
            }
        """)
        show_more_btn.clicked.connect(self.toggle_expand)
        
        button_layout.addStretch()
        button_layout.addWidget(show_more_btn)
        button_layout.addStretch()
        
        self.code_layout.addWidget(button_container)
    
    def create_status_messages(self):
        """إنشاء رسائل الحالة"""
        # رسالة نجاح النسخ
        self.copy_success_widget = QWidget(self)
        self.copy_success_widget.setStyleSheet("""
            QWidget {
                background-color: #238636;
                border: 1px solid #2ea043;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.copy_success_widget.hide()
        
        success_layout = QHBoxLayout(self.copy_success_widget)
        success_layout.setContentsMargins(10, 5, 10, 5)
        
        success_icon = QLabel("✅")
        success_text = QLabel("تم النسخ بنجاح!")
        success_text.setStyleSheet("color: white; font-weight: bold;")
        
        success_layout.addWidget(success_icon)
        success_layout.addWidget(success_text)
        success_layout.addStretch()
        
    def setup_shortcuts(self):
        """إعداد اختصارات لوحة المفاتيح"""
        # نسخ الكود
        copy_shortcut = QShortcut(QKeySequence.Copy, self)
        copy_shortcut.activated.connect(self.copy_code)
        
        # حفظ التعديلات (أثناء التحرير)
        save_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        save_shortcut.activated.connect(self.save_edit)
        
        # إلغاء التحرير
        cancel_shortcut = QShortcut(QKeySequence.Cancel, self)
        cancel_shortcut.activated.connect(self.cancel_edit)
        
        # ملء الشاشة
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
    
    # === وظائف التحكم ===
    
    def toggle_expand(self):
        """تبديل حالة التوسع"""
        self.is_expanded = not self.is_expanded
        if hasattr(self, 'expand_btn'):
            self.expand_btn.setText("🙈" if self.is_expanded else "👁️")
            self.expand_btn.setToolTip("إخفاء" if self.is_expanded else "عرض كامل")
        self.render_code()
    
    def toggle_fullscreen(self):
        """تبديل حالة ملء الشاشة"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            # حفظ الحالة الحالية
            self.normal_parent = self.parent()
            self.normal_geometry = self.geometry()
            
            # إزالة من الوالد الحالي
            self.setParent(None)
            self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
            self.showMaximized()
            
            self.fullscreen_btn.setText("⚏")
            self.fullscreen_btn.setToolTip("تصغير")
        else:
            # العودة للحالة العادية
            self.setWindowFlags(Qt.Widget)
            if hasattr(self, 'normal_parent') and self.normal_parent:
                self.setParent(self.normal_parent)
            self.showNormal()
            
            self.fullscreen_btn.setText("⛶")
            self.fullscreen_btn.setToolTip("ملء الشاشة")
        
        self.render_code()
    
    def toggle_edit(self):
        """تبديل وضع التحرير"""
        if not self.is_editing:
            # بدء التحرير
            self.is_editing = True
            self.editor.setPlainText(self.current_code)
            self.code_area.hide()
            self.editor.show()
            
            self.edit_btn.setText("💾")
            self.edit_btn.setToolTip("حفظ")
            
            # التركيز على المحرر
            self.editor.setFocus()
        else:
            # حفظ التعديلات
            self.save_edit()
    
    def save_edit(self):
        """حفظ التعديلات"""
        if self.is_editing:
            new_code = self.editor.toPlainText()
            if new_code != self.current_code:
                self.codeEdited.emit(self.current_code, new_code)
                self.current_code = new_code
                self.lines = new_code.split('\n')
                self.line_count = len(self.lines)
            
            self.cancel_edit()
    
    def cancel_edit(self):
        """إلغاء التحرير"""
        self.is_editing = False
        self.editor.hide()
        self.code_area.show()
        
        self.edit_btn.setText("✏️")
        self.edit_btn.setToolTip("تحرير")
        
        self.render_code()
    
    def copy_code(self):
        """نسخ الكود إلى الحافظة"""
        code_to_copy = self.current_code
        
        clipboard = QApplication.clipboard()
        clipboard.setText(code_to_copy)
        
        self.copyRequested.emit(code_to_copy)
        self.show_copy_success()
    
    def download_code(self):
        """تحميل الكود كملف"""
        extension = self.FILE_EXTENSIONS.get(self.language, 'txt')
        filename = f"code.{extension}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ الكود", filename, f"*.{extension};;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_code)
                
                self.downloadRequested.emit(self.current_code, self.language)
                QMessageBox.information(self, "نجح", "تم حفظ الملف بنجاح!")
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حفظ الملف:\n{str(e)}")
    
    def preview_html(self):
        """معاينة HTML في نافذة جديدة"""
        if self.language in ['html', 'htm']:
            # إنشاء نافذة معاينة
            preview_window = QDialog(self)
            preview_window.setWindowTitle("معاينة HTML")
            preview_window.resize(800, 600)
            
            layout = QVBoxLayout(preview_window)
            
            # إنشاء QWebEngineView للمعاينة
            try:
                from PyQt5.QtWebEngineWidgets import QWebEngineView
                web_view = QWebEngineView()
                web_view.setHtml(self.current_code)
                layout.addWidget(web_view)
            except ImportError:
                # بديل باستخدام QTextBrowser
                text_browser = QTextBrowser()
                text_browser.setHtml(self.current_code)
                layout.addWidget(text_browser)
            
            preview_window.exec_()
    
    def show_copy_success(self):
        """عرض رسالة نجاح النسخ"""
        # تحديد موقع الرسالة
        self.copy_success_widget.move(
            self.width() - self.copy_success_widget.width() - 20,
            20
        )
        self.copy_success_widget.show()
        self.copy_success_widget.raise_()
        
        # إخفاء الرسالة بعد ثانيتين
        self.copy_success_timer.start(2000)
    
    def hide_copy_success(self):
        """إخفاء رسالة نجاح النسخ"""
        self.copy_success_widget.hide()
    
    def resizeEvent(self, event):
        """تحديث موقع رسائل الحالة عند تغيير الحجم"""
        super().resizeEvent(event)
        if hasattr(self, 'copy_success_widget') and self.copy_success_widget.isVisible():
            self.copy_success_widget.move(
                self.width() - self.copy_success_widget.width() - 20,
                20
            )


class MarkdownRenderer(QWidget):
    """محرك عرض Markdown متطور"""
    
    def __init__(self, content: str = "", parent=None):
        super().__init__(parent)
        self.original_content = content
        self.setup_ui()
        if content:
            self.render_content(content)
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        
        # منطقة التمرير
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # ويدجت المحتوى
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)
    
    def render_content(self, content: str):
        """عرض محتوى Markdown"""
        # تنظيف المحتوى السابق
        self.clear_content()
        
        # تحليل المحتوى
        blocks = self.parse_markdown(content)
        
        # عرض كل بلوك
        for block in blocks:
            widget = self.create_block_widget(block)
            if widget:
                self.content_layout.addWidget(widget)
        
        # إضافة مساحة مرنة في النهاية
        self.content_layout.addStretch()
    
    def clear_content(self):
        """تنظيف المحتوى السابق"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def parse_markdown(self, content: str) -> List[Dict]:
        """تحليل محتوى Markdown إلى بلوكات"""
        blocks = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Code blocks
            if line.startswith('```'):
                language = line[3:].strip()
                code_lines = []
                i += 1
                
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                blocks.append({
                    'type': 'code',
                    'language': language,
                    'content': '\n'.join(code_lines)
                })
                
            # Headers
            elif line.startswith('#'):
                level = 0
                while level < len(line) and line[level] == '#':
                    level += 1
                
                blocks.append({
                    'type': 'header',
                    'level': level,
                    'content': line[level:].strip()
                })
                
            # Lists
            elif line.startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\. ', line):
                list_items = []
                list_type = 'ordered' if re.match(r'^\d+\. ', line) else 'unordered'
                
                while i < len(lines):
                    current_line = lines[i].strip()
                    if current_line.startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\. ', current_line):
                        if current_line.startswith(('- ', '* ', '+ ')):
                            item_content = current_line[2:].strip()
                        else:
                            item_content = re.sub(r'^\d+\. ', '', current_line)
                        list_items.append(item_content)
                        i += 1
                    elif current_line == '':
                        i += 1
                        break
                    else:
                        break
                
                blocks.append({
                    'type': 'list',
                    'list_type': list_type,
                    'items': list_items
                })
                continue
                
            # Tables
            elif '|' in line:
                table_rows = []
                while i < len(lines) and '|' in lines[i]:
                    row = [cell.strip() for cell in lines[i].split('|')[1:-1]]
                    table_rows.append(row)
                    i += 1
                
                if table_rows:
                    blocks.append({
                        'type': 'table',
                        'rows': table_rows
                    })
                continue
                
            # Blockquotes
            elif line.startswith('>'):
                quote_lines = []
                while i < len(lines) and lines[i].strip().startswith('>'):
                    quote_lines.append(lines[i].strip()[1:].strip())
                    i += 1
                
                blocks.append({
                    'type': 'blockquote',
                    'content': '\n'.join(quote_lines)
                })
                continue
                
            # Horizontal rules
            elif line in ['---', '***', '___']:
                blocks.append({
                    'type': 'hr'
                })
                
            # Regular paragraphs
            elif line:
                paragraph_lines = []
                while i < len(lines) and lines[i].strip():
                    paragraph_lines.append(lines[i].strip())
                    i += 1
                
                if paragraph_lines:
                    blocks.append({
                        'type': 'paragraph',
                        'content': '\n'.join(paragraph_lines)
                    })
                continue
            
            i += 1
        
        return blocks
    
    def create_block_widget(self, block: Dict) -> Optional[QWidget]:
        """إنشاء ويدجت لبلوك معين"""
        block_type = block.get('type')
        
        if block_type == 'code':
            return CodeBlockWidget(
                block.get('content', ''),
                block.get('language', 'text'),
                self
            )
            
        elif block_type == 'header':
            return self.create_header_widget(block)
            
        elif block_type == 'paragraph':
            return self.create_paragraph_widget(block)
            
        elif block_type == 'list':
            return self.create_list_widget(block)
            
        elif block_type == 'table':
            return self.create_table_widget(block)
            
        elif block_type == 'blockquote':
            return self.create_blockquote_widget(block)
            
        elif block_type == 'hr':
            return self.create_hr_widget()
        
        return None
    
    def create_header_widget(self, block: Dict) -> QWidget:
        """إنشاء ويدجت للعناوين"""
        level = block.get('level', 1)
        content = block.get('content', '')
        
        header = QLabel(content)
        header.setWordWrap(True)
        header.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # تحديد حجم الخط حسب المستوى
        font_sizes = {1: 24, 2: 20, 3: 18, 4: 16, 5: 14, 6: 12}
        font_size = font_sizes.get(level, 12)
        
        header.setStyleSheet(f"""
            QLabel {{
                color: #e6edf3;
                font-size: {font_size}px;
                font-weight: bold;
                margin: 15px 0 10px 0;
                padding-bottom: 8px;
                border-bottom: {2 if level <= 2 else 0}px solid #30363d;
            }}
        """)
        
        return header
    
    def create_paragraph_widget(self, block: Dict) -> QWidget:
        """إنشاء ويدجت للفقرات"""
        content = block.get('content', '')
        
        # معالجة التنسيق الداخلي
        content = self.process_inline_formatting(content)
        
        paragraph = QLabel(content)
        paragraph.setWordWrap(True)
        paragraph.setTextInteractionFlags(Qt.TextSelectableByMouse)
        paragraph.setTextFormat(Qt.RichText)
        paragraph.setStyleSheet("""
            QLabel {
                color: #c9d1d9;
                font-size: 14px;
                line-height: 1.6;
                margin: 8px 0;
            }
        """)
        
        return paragraph
    
    def create_list_widget(self, block: Dict) -> QWidget:
        """إنشاء ويدجت للقوائم"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 5, 0, 5)
        layout.setSpacing(5)
        
        items = block.get('items', [])
        list_type = block.get('list_type', 'unordered')
        
        for i, item in enumerate(items):
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(8)
            
            # نقطة أو رقم القائمة
            if list_type == 'ordered':
                marker = QLabel(f"{i+1}.")
            else:
                marker = QLabel("•")
            
            marker.setStyleSheet("""
                QLabel {
                    color: #58a6ff;
                    font-weight: bold;
                    min-width: 20px;
                }
            """)
            marker.setAlignment(Qt.AlignTop)
            
            # محتوى العنصر
            content = self.process_inline_formatting(item)
            item_label = QLabel(content)
            item_label.setWordWrap(True)
            item_label.setTextFormat(Qt.RichText)
            item_label.setStyleSheet("""
                QLabel {
                    color: #c9d1d9;
                    font-size: 14px;
                }
            """)
            
            item_layout.addWidget(marker)
            item_layout.addWidget(item_label, 1)
            layout.addWidget(item_widget)
        
        return container
    
    def create_table_widget(self, block: Dict) -> QWidget:
        """إنشاء ويدجت للجداول"""
        rows = block.get('rows', [])
        if not rows:
            return None
        
        table = QTableWidget()
        table.setRowCount(len(rows))
        table.setColumnCount(len(rows[0]) if rows else 0)
        
        # إعداد البيانات
        for i, row in enumerate(rows):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                table.setItem(i, j, item)
        
        # إعداد الستايل
        table.setStyleSheet("""
            QTableWidget {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                gridline-color: #21262d;
            }
            QTableWidget::item {
                color: #c9d1d9;
                padding: 8px;
                border-bottom: 1px solid #21262d;
            }
            QHeaderView::section {
                background-color: #161b22;
                color: #f0f6fc;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
        """)
        
        # إخفاء أرقام الصفوف والأعمدة
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        
        # تحجيم تلقائي
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        
        return table
    
    def create_blockquote_widget(self, block: Dict) -> QWidget:
        """إنشاء ويدجت للاقتباسات"""
        content = block.get('content', '')
        content = self.process_inline_formatting(content)
        
        quote_container = QWidget()
        quote_layout = QHBoxLayout(quote_container)
        quote_layout.setContentsMargins(0, 10, 0, 10)
        quote_layout.setSpacing(15)
        
        # خط جانبي ملون
        border_line = QFrame()
        border_line.setFixedWidth(4)
        border_line.setStyleSheet("""
            QFrame {
                background-color: #58a6ff;
                border-radius: 2px;
            }
        """)
        
        # محتوى الاقتباس
        quote_label = QLabel(content)
        quote_label.setWordWrap(True)
        quote_label.setTextFormat(Qt.RichText)
        quote_label.setStyleSheet("""
            QLabel {
                color: #8b949e;
                font-size: 14px;
                font-style: italic;
                background-color: rgba(88, 166, 255, 0.1);
                padding: 15px;
                border-radius: 6px;
            }
        """)
        
        quote_layout.addWidget(border_line)
        quote_layout.addWidget(quote_label, 1)
        
        return quote_container
    
    def create_hr_widget(self) -> QWidget:
        """إنشاء خط فاصل"""
        hr = QFrame()
        hr.setFrameShape(QFrame.HLine)
        hr.setStyleSheet("""
            QFrame {
                color: #30363d;
                background-color: #30363d;
                height: 2px;
                margin: 20px 0;
            }
        """)
        return hr
    
    def process_inline_formatting(self, text: str) -> str:
        """معالجة التنسيق الداخلي للنص"""
        # Bold text
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        
        # Italic text
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
        
        # Inline code
        text = re.sub(r'`(.*?)`', r'<code style="background-color: rgba(110, 118, 129, 0.4); padding: 2px 4px; border-radius: 3px; color: #f85149;">\1</code>', text)
        
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color: #58a6ff; text-decoration: none;">\1</a>', text)
        
        # Strikethrough
        text = re.sub(r'~~(.*?)~~', r'<s>\1</s>', text)
        
        return text


# === الكلاس الرئيسي للتصدير ===

class MessageContentRenderer(QWidget):
    """محرك عرض محتوى الرسائل مع دعم Markdown و CodeBlock"""
    
    def __init__(self, content: str = "", parent=None):
        super().__init__(parent)
        self.content = content
        self.setup_ui()
        if content:
            self.render_content(content)
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # إنشاء محرك Markdown
        self.markdown_renderer = MarkdownRenderer("", self)
        self.layout.addWidget(self.markdown_renderer)
    
    def render_content(self, content: str):
        """عرض المحتوى"""
        self.content = content
        self.markdown_renderer.render_content(content)
    
    def update_content(self, content: str):
        """تحديث المحتوى"""
        self.render_content(content)


if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # مثال لاختبار النظام
    test_content = '''
# مرحباً بك في محرك Markdown المتطور! 🚀

هذا **نص عريض** و *نص مائل* و `كود داخلي` و ~~نص مشطوب~~.

## مثال على الكود:

```python
def hello_world():
    """دالة بسيطة لطباعة السلام"""
    print("مرحباً بالعالم!")
    
    for i in range(5):
        print(f"العدد: {i}")
    
    return "تم بنجاح"

# استدعاء الدالة
result = hello_world()
```

### قائمة بالميزات:

- ✅ دعم **Syntax Highlighting** متطور
- ✅ نسخ وتحميل الأكواد
- ✅ وضع ملء الشاشة
- ✅ تحرير الأكواد
- ✅ أرقام الأسطر
- ✅ كشف اللغة تلقائياً

### مثال JavaScript:

```javascript
// دالة لحساب المجموع
function calculateSum(numbers) {
    return numbers.reduce((sum, num) => {
        return sum + num;
    }, 0);
}

const numbers = [1, 2, 3, 4, 5];
const result = calculateSum(numbers);
console.log(`المجموع: ${result}`);
```

> هذا اقتباس مهم يوضح قوة النظام في عرض المحتوى بشكل جميل ومنسق.

---

**شكراً لاستخدام النظام!** 🎉
'''
    
    window = MessageContentRenderer(test_content)
    window.resize(800, 600)
    window.show()
    
    sys.exit(app.exec_())