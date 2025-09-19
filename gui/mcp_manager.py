"""
MCP Manager - إدارة Model Context Protocol Servers
يوفر واجهة لإدارة MCP servers وتكوينهم
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QTextEdit, QDialog, QScrollArea,
    QGroupBox, QCheckBox, QMessageBox, QInputDialog, QSplitter,
    QTabWidget, QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

@dataclass
class MCPServerConfig:
    """تكوين MCP Server"""
    name: str
    description: str
    enabled: bool = True
    tools: List[Dict[str, Any]] = None
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []
        if self.config is None:
            self.config = {}

class MCPConfigEditor(QDialog):
    """محرر JSON لتكوين MCP Servers"""
    
    def __init__(self, config: Optional[MCPServerConfig] = None, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("محرر MCP Configuration")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()
        
        if config:
            self.load_config(config)
            
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # معلومات أساسية
        info_group = QGroupBox("المعلومات الأساسية")
        info_layout = QVBoxLayout(info_group)
        
        # اسم الخادم
        self.name_edit = QTextEdit()
        self.name_edit.setMaximumHeight(30)
        self.name_edit.setPlainText("new-mcp-server")
        info_layout.addWidget(QLabel("اسم الخادم:"))
        info_layout.addWidget(self.name_edit)
        
        # الوصف
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlainText("وصف MCP Server الجديد")
        info_layout.addWidget(QLabel("الوصف:"))
        info_layout.addWidget(self.description_edit)
        
        # تمكين/تعطيل
        self.enabled_checkbox = QCheckBox("تمكين هذا الخادم")
        self.enabled_checkbox.setChecked(True)
        info_layout.addWidget(self.enabled_checkbox)
        
        layout.addWidget(info_group)
        
        # محرر JSON
        json_group = QGroupBox("تكوين JSON")
        json_layout = QVBoxLayout(json_group)
        
        # نص تفسيري
        help_text = QLabel("""
أدخل تكوين JSON للـ MCP Server:
- tools: قائمة بالأدوات المتاحة
- config: إعدادات إضافية للخادم
        """)
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #666; font-size: 12px;")
        json_layout.addWidget(help_text)
        
        # محرر JSON
        self.json_editor = QTextEdit()
        self.json_editor.setFont(QFont("Consolas, Monaco, monospace", 11))
        self.json_editor.setPlainText(self.get_default_json())
        json_layout.addWidget(self.json_editor)
        
        layout.addWidget(json_group)
        
        # أزرار
        buttons_layout = QHBoxLayout()
        
        self.validate_btn = QPushButton("✓ التحقق من JSON")
        self.validate_btn.clicked.connect(self.validate_json)
        self.validate_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        
        self.save_btn = QPushButton("💾 حفظ")
        self.save_btn.clicked.connect(self.save_config)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        self.cancel_btn = QPushButton("❌ إلغاء")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        buttons_layout.addWidget(self.validate_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
        
    def get_default_json(self) -> str:
        """إرجاع JSON افتراضي كمثال"""
        return json.dumps({
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "example_function",
                        "description": "مثال على وظيفة MCP",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "input": {
                                    "type": "string",
                                    "description": "المدخل المطلوب"
                                }
                            },
                            "required": ["input"]
                        }
                    }
                }
            ],
            "config": {
                "api_url": "https://api.example.com",
                "timeout": 30,
                "enabled_features": ["search", "analysis"]
            }
        }, indent=2, ensure_ascii=False)
        
    def validate_json(self):
        """التحقق من صحة JSON"""
        try:
            json_text = self.json_editor.toPlainText()
            parsed = json.loads(json_text)
            
            # التحقق من الهيكل المطلوب
            if not isinstance(parsed, dict):
                raise ValueError("JSON يجب أن يكون object")
                
            if "tools" in parsed and not isinstance(parsed["tools"], list):
                raise ValueError("tools يجب أن يكون array")
                
            if "config" in parsed and not isinstance(parsed["config"], dict):
                raise ValueError("config يجب أن يكون object")
                
            QMessageBox.information(self, "✓ نجح", "JSON صحيح!")
            return True
            
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "❌ خطأ JSON", f"خطأ في تفسير JSON:\n{str(e)}")
            return False
        except ValueError as e:
            QMessageBox.warning(self, "❌ خطأ في الهيكل", str(e))
            return False
            
    def load_config(self, config: MCPServerConfig):
        """تحميل تكوين موجود"""
        self.name_edit.setPlainText(config.name)
        self.description_edit.setPlainText(config.description)
        self.enabled_checkbox.setChecked(config.enabled)
        
        # تكوين JSON
        json_config = {
            "tools": config.tools,
            "config": config.config
        }
        self.json_editor.setPlainText(json.dumps(json_config, indent=2, ensure_ascii=False))
        
    def save_config(self):
        """حفظ التكوين"""
        if not self.validate_json():
            return
            
        try:
            name = self.name_edit.toPlainText().strip()
            description = self.description_edit.toPlainText().strip()
            enabled = self.enabled_checkbox.isChecked()
            
            if not name:
                QMessageBox.warning(self, "❌ خطأ", "اسم الخادم مطلوب")
                return
                
            json_text = self.json_editor.toPlainText()
            parsed = json.loads(json_text)
            
            self.config = MCPServerConfig(
                name=name,
                description=description,
                enabled=enabled,
                tools=parsed.get("tools", []),
                config=parsed.get("config", {})
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ خطأ", f"فشل في حفظ التكوين:\n{str(e)}")

class MCPManagerSidebar(QWidget):
    """Sidebar لإدارة MCP Servers"""
    
    mcp_changed = pyqtSignal(str, bool)  # server_name, enabled
    mcp_updated = pyqtSignal()  # تم تحديث قائمة MCP
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mcp_servers: Dict[str, MCPServerConfig] = {}
        self.config_file = "mcp_config.json"
        self.init_ui()
        self.load_saved_configs()
        self.load_default_servers()
        
    def init_ui(self):
        self.setMaximumHeight(400)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin: 5px 0px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #ffffff;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QListWidget {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555;
                margin: 2px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #007ACC;
            }
            QListWidget::item:hover {
                background-color: #4c4c4c;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # عنوان
        title = QLabel("MCP Servers")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # قائمة MCP Servers
        self.mcp_list = QListWidget()
        self.mcp_list.itemDoubleClicked.connect(self.edit_server)
        self.mcp_list.setMaximumHeight(120)
        self.mcp_list.setMinimumHeight(80)
        layout.addWidget(self.mcp_list)
        
        # أزرار التحكم مع القائمة الموجودة
        buttons_layout = QHBoxLayout()
        
        self.remove_btn = QPushButton("🗑️ حذف")
        self.remove_btn.clicked.connect(self.remove_selected_server)
        buttons_layout.addWidget(self.remove_btn)
        
        self.refresh_btn = QPushButton("🔄 تحديث")
        self.refresh_btn.clicked.connect(self.refresh_list)
        buttons_layout.addWidget(self.refresh_btn)
        
        self.add_btn = QPushButton("➕ إضافة MCP")
        self.add_btn.clicked.connect(self.add_new_server)
        buttons_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️ تعديل")
        self.edit_btn.clicked.connect(self.edit_selected_server)
        buttons_layout.addWidget(self.edit_btn)
        
        layout.addLayout(buttons_layout)
        
        # معلومات الخادم المحدد (مبسطة)
        self.server_info = QLabel("اختر خادم لعرض التفاصيل")
        self.server_info.setWordWrap(True)
        self.server_info.setMaximumHeight(40)
        self.server_info.setStyleSheet("color: #ccc; font-size: 11px; padding: 5px; border: 1px solid #555; border-radius: 3px;")
        layout.addWidget(self.server_info)
        
        # ربط الأحداث
        self.mcp_list.itemClicked.connect(self.show_server_info)
        
    def load_default_servers(self):
        """تحميل الخوادم الافتراضية"""
        default_servers = [
            MCPServerConfig(
                name="context7",
                description="Context7 - مكتبة توثيق البرمجيات",
                enabled=True,
                tools=[],
                config={"type": "documentation"}
            ),
            MCPServerConfig(
                name="fetch", 
                description="Fetch - جلب المحتوى من الإنترنت",
                enabled=True,
                tools=[],
                config={"type": "web_fetch"}
            ),
            MCPServerConfig(
                name="filesystem",
                description="Filesystem - إدارة الملفات والمجلدات", 
                enabled=True,
                tools=[],
                config={"type": "file_system"}
            ),
            MCPServerConfig(
                name="git",
                description="Git - إدارة repositories",
                enabled=True,
                tools=[],
                config={"type": "version_control"}
            ),
            MCPServerConfig(
                name="memory",
                description="Memory - إدارة الذاكرة والمعرفة",
                enabled=True,
                tools=[],
                config={"type": "knowledge_graph"}
            ),
            MCPServerConfig(
                name="sequential-thinking",
                description="Sequential Thinking - التفكير المتسلسل",
                enabled=True,
                tools=[],
                config={"type": "reasoning"}
            ),
            MCPServerConfig(
                name="time-mcp",
                description="Time MCP - إدارة الوقت والتواريخ",
                enabled=True,
                tools=[],
                config={"type": "time_utilities"}
            )
        ]
        
        for server in default_servers:
            if server.name not in self.mcp_servers:
                self.mcp_servers[server.name] = server
                
        self.refresh_list()
        
    def refresh_list(self):
        """تحديث قائمة الخوادم"""
        self.mcp_list.clear()
        
        for name, config in self.mcp_servers.items():
            item = QListWidgetItem()
            
            # أيقونة الحالة
            status_icon = "🟢" if config.enabled else "🔴"
            item.setText(f"{status_icon} {config.name}")
            item.setData(Qt.UserRole, name)
            
            # لون النص حسب الحالة
            if config.enabled:
                item.setForeground(QColor("#ffffff"))
            else:
                item.setForeground(QColor("#888888"))
                
            self.mcp_list.addItem(item)
            
    def show_server_info(self, item: QListWidgetItem):
        """عرض معلومات الخادم المحدد"""
        server_name = item.data(Qt.UserRole)
        if server_name in self.mcp_servers:
            config = self.mcp_servers[server_name]
            
            info_text = f"""
<b>الاسم:</b> {config.name}<br>
<b>الوصف:</b> {config.description}<br>
<b>الحالة:</b> {'مفعل' if config.enabled else 'معطل'}<br>
<b>عدد الأدوات:</b> {len(config.tools)}<br>
<b>إعدادات إضافية:</b> {len(config.config)} عنصر
            """
            self.server_info.setText(info_text)
            
    def add_new_server(self):
        """إضافة خادم جديد"""
        editor = MCPConfigEditor(parent=self)
        if editor.exec_() == QDialog.Accepted and editor.config:
            config = editor.config
            
            # التحقق من عدم وجود اسم مكرر
            if config.name in self.mcp_servers:
                reply = QMessageBox.question(
                    self, "خادم موجود", 
                    f"الخادم '{config.name}' موجود بالفعل. هل تريد استبداله؟"
                )
                if reply != QMessageBox.Yes:
                    return
                    
            self.mcp_servers[config.name] = config
            self.save_configs()
            self.refresh_list()
            self.mcp_updated.emit()
            
    def edit_selected_server(self):
        """تعديل الخادم المحدد"""
        current_item = self.mcp_list.currentItem()
        if current_item:
            self.edit_server(current_item)
            
    def edit_server(self, item: QListWidgetItem):
        """تعديل خادم محدد"""
        server_name = item.data(Qt.UserRole)
        if server_name in self.mcp_servers:
            config = self.mcp_servers[server_name]
            
            editor = MCPConfigEditor(config, parent=self)
            if editor.exec_() == QDialog.Accepted and editor.config:
                # حذف الاسم القديم إذا تغير
                if editor.config.name != server_name:
                    del self.mcp_servers[server_name]
                    
                self.mcp_servers[editor.config.name] = editor.config
                self.save_configs()
                self.refresh_list()
                self.mcp_updated.emit()
                
    def remove_selected_server(self):
        """حذف الخادم المحدد"""
        current_item = self.mcp_list.currentItem()
        if current_item:
            server_name = current_item.data(Qt.UserRole)
            
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                f"هل أنت متأكد من حذف الخادم '{server_name}'؟"
            )
            
            if reply == QMessageBox.Yes:
                if server_name in self.mcp_servers:
                    del self.mcp_servers[server_name]
                    self.save_configs()
                    self.refresh_list()
                    self.mcp_updated.emit()
                    
    def save_configs(self):
        """حفظ التكوينات في ملف"""
        try:
            config_data = {
                name: asdict(config) for name, config in self.mcp_servers.items()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            QMessageBox.warning(self, "خطأ في الحفظ", f"فشل في حفظ التكوينات:\n{str(e)}")
            
    def load_saved_configs(self):
        """تحميل التكوينات المحفوظة"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                for name, data in config_data.items():
                    self.mcp_servers[name] = MCPServerConfig(**data)
                    
        except Exception as e:
            print(f"خطأ في تحميل التكوينات: {e}")
            
    def get_enabled_servers(self) -> Dict[str, MCPServerConfig]:
        """الحصول على الخوادم المفعلة فقط"""
        return {
            name: config for name, config in self.mcp_servers.items() 
            if config.enabled
        }
        
    def toggle_server(self, server_name: str, enabled: bool):
        """تفعيل/تعطيل خادم"""
        if server_name in self.mcp_servers:
            self.mcp_servers[server_name].enabled = enabled
            self.save_configs()
            self.refresh_list()
            self.mcp_changed.emit(server_name, enabled)
