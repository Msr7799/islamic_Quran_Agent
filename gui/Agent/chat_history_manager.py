#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدير تاريخ المحادثات
يدير حفظ وتحميل المحادثات مع الذكاء الاصطناعي
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import re

# محاولة استيراد معالج النصوص المتقدم
try:
    from .text_processor_advanced import AdvancedTextProcessor
    TEXT_PROCESSOR_AVAILABLE = True
except ImportError:
    TEXT_PROCESSOR_AVAILABLE = False

@dataclass
class ChatMessage:
    """رسالة في المحادثة"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str
    message_id: Optional[str] = None
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())

@dataclass
class ChatSession:
    """جلسة محادثة"""
    session_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[ChatMessage]
    
    def __post_init__(self):
        if not self.messages:
            self.messages = []

class ChatHistoryManager:
    """مدير تاريخ المحادثات"""
    
    def __init__(self, base_dir: str = "Agent/chats_log_and_memory_history"):
        print("✅ [ChatHistoryManager] بدأ تنفيذ __init__...")
        # إنشاء المسار الكامل بناءً على المسار الحالي
        if not os.path.isabs(base_dir):
            # إذا كان المسار نسبي، نبحث عنه في نفس مجلد الملف الحالي
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.base_dir = os.path.join(current_dir, "chats_log_and_memory_history")
        else:
            self.base_dir = base_dir
        self.current_session_id = None
        self.current_session = None
        self.user_input_history = []  # تاريخ مدخلات المستخدم
        
        # إنشاء المجلد إذا لم يكن موجوداً
        os.makedirs(self.base_dir, exist_ok=True)
        
        # تحميل آخر جلسة أو إنشاء جلسة جديدة
        self.load_or_create_session()
    
    def generate_session_title(self, first_message: str) -> str:
        """توليد عنوان للجلسة بناءً على أول رسالة"""
        # تنظيف النص
        clean_text = re.sub(r'[^\w\s\u0600-\u06FF]', '', first_message)
        words = clean_text.split()[:5]  # أول 5 كلمات
        
        if not words:
            return f"محادثة {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        title = ' '.join(words)
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title
    
    def create_new_session(self, title: str = None) -> str:
        """إنشاء جلسة محادثة جديدة"""
        session_id = str(uuid.uuid4())
        
        if title is None:
            title = f"محادثة جديدة {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        self.current_session = ChatSession(
            session_id=session_id,
            title=title,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            messages=[]
        )
        
        self.current_session_id = session_id
        self.user_input_history = []  # إعادة تعيين تاريخ المدخلات
        self.save_current_session()
        
        return session_id
    
    def load_session(self, session_id: str) -> bool:
        """تحميل جلسة محادثة"""
        file_path = os.path.join(self.base_dir, f"{session_id}.json")
        
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # تحويل الرسائل إلى كائنات ChatMessage
            messages = []
            for msg_data in data.get('messages', []):
                messages.append(ChatMessage(**msg_data))
            
            self.current_session = ChatSession(
                session_id=data['session_id'],
                title=data['title'],
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                messages=messages
            )
            
            self.current_session_id = session_id
            
            # استخراج تاريخ مدخلات المستخدم
            self.user_input_history = [
                msg.content for msg in messages if msg.role == "user"
            ]
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تحميل الجلسة {session_id}: {e}")
            return False
    
    def save_current_session(self):
        """حفظ الجلسة الحالية"""
        if not self.current_session:
            return
        
        self.current_session.updated_at = datetime.now().isoformat()
        
        file_path = os.path.join(self.base_dir, f"{self.current_session_id}.json")
        
        try:
            # تحويل الجلسة إلى قاموس
            session_dict = asdict(self.current_session)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_dict, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ خطأ في حفظ الجلسة: {e}")
    
    def add_message(self, role: str, content: str) -> str:
        """إضافة رسالة للجلسة الحالية"""
        if not self.current_session:
            self.create_new_session()
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        
        self.current_session.messages.append(message)
        
        # إضافة لتاريخ المدخلات إذا كانت رسالة مستخدم
        if role == "user":
            self.user_input_history.append(content)
            
            # تحديث عنوان الجلسة إذا كانت أول رسالة
            if len([msg for msg in self.current_session.messages if msg.role == "user"]) == 1:
                self.current_session.title = self.generate_session_title(content)
        
        self.save_current_session()
        return message.message_id
    
    def get_user_input_history(self) -> List[str]:
        """الحصول على تاريخ مدخلات المستخدم"""
        return self.user_input_history.copy()
    
    def get_previous_input(self, current_index: int) -> Optional[str]:
        """الحصول على المدخل السابق"""
        if not self.user_input_history or current_index >= len(self.user_input_history):
            return None
        
        return self.user_input_history[-(current_index + 1)]
    
    def load_or_create_session(self):
        """تحميل آخر جلسة أو إنشاء جلسة جديدة"""
        sessions = self.get_all_sessions()
        
        if sessions:
            # تحميل آخر جلسة
            latest_session = max(sessions, key=lambda x: x['updated_at'])
            self.load_session(latest_session['session_id'])
        else:
            # إنشاء جلسة جديدة
            self.create_new_session()
    
    def get_all_sessions(self) -> List[Dict]:
        """الحصول على جميع الجلسات"""
        sessions = []
        
        if not os.path.exists(self.base_dir):
            return sessions
        
        for filename in os.listdir(self.base_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.base_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    sessions.append({
                        'session_id': data['session_id'],
                        'title': data['title'],
                        'created_at': data['created_at'],
                        'updated_at': data['updated_at'],
                        'message_count': len(data.get('messages', []))
                    })
                    
                except Exception as e:
                    print(f"❌ خطأ في قراءة الملف {filename}: {e}")
        
        # ترتيب حسب آخر تحديث
        sessions.sort(key=lambda x: x['updated_at'], reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """حذف جلسة محادثة"""
        file_path = os.path.join(self.base_dir, f"{session_id}.json")
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                
                # إذا كانت الجلسة المحذوفة هي الحالية، إنشاء جلسة جديدة
                if session_id == self.current_session_id:
                    self.create_new_session()
                
                return True
            return False
            
        except Exception as e:
            print(f"❌ خطأ في حذف الجلسة {session_id}: {e}")
            return False
    
    def clear_all_sessions(self) -> bool:
        """مسح جميع الجلسات"""
        try:
            if os.path.exists(self.base_dir):
                for filename in os.listdir(self.base_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(self.base_dir, filename)
                        os.remove(file_path)
            
            # إنشاء جلسة جديدة
            self.create_new_session()
            return True
            
        except Exception as e:
            print(f"❌ خطأ في مسح الجلسات: {e}")
            return False
    
    def get_current_session_messages(self) -> List[ChatMessage]:
        """الحصول على رسائل الجلسة الحالية"""
        if self.current_session:
            return self.current_session.messages.copy()
        return []
    
    def get_session_context_for_ai(self, limit: int = 10) -> List[Dict]:
        """الحصول على سياق الجلسة للذكاء الاصطناعي"""
        if not self.current_session:
            return []
        
        # أخذ آخر رسائل محددة
        recent_messages = self.current_session.messages[-limit:] if len(self.current_session.messages) > limit else self.current_session.messages
        
        context = []
        for msg in recent_messages:
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return context
