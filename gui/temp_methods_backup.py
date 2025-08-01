#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
الوظائف المتبقية لنافذة الشات الاحترافية
Remaining methods for ProfessionalChatWindow
"""

from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QDialog
from PyQt5.QtCore import QTimer

# استيراد الكلاسات المطلوبة من الملفات الأخرى
try:
    from chat_components import ChatHistoryDialog
    GROQ_AVAILABLE = True  # يجب أن تأتي من إعدادات المشروع
except ImportError:
    ChatHistoryDialog = None
    GROQ_AVAILABLE = False

# بديل مؤقت لـ MessageBubble حتى يتم إنشاؤه
class MessageBubble:
    """فئة بديلة مؤقتة لفقاعة الرسالة"""
    def __init__(self, message, is_user):
        self.message = message
        self.is_user = is_user

# هذه الوظائف يجب إضافتها لفئة ProfessionalChatWindow

def add_message(self, message: str, is_user: bool = True):
    """إضافة رسالة جديدة للمحادثة"""
    # إنشاء فقاعة الرسالة
    bubble = MessageBubble(message, is_user)
    
    # إضافة الفقاعة قبل الـ stretch
    self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
    
    # حفظ الرسالة في القائمة
    self.messages.append({
        'message': message,
        'is_user': is_user,
        'timestamp': datetime.now().isoformat()
    })
    
    # التمرير للأسفل
    QTimer.singleShot(100, self.scroll_to_bottom)

def scroll_to_bottom(self):
    """التمرير لأسفل منطقة الرسائل"""
    scrollbar = self.messages_area.verticalScrollBar()
    scrollbar.setValue(scrollbar.maximum())

def send_message(self, message: str):
    """إرسال رسالة جديدة"""
    if not message.strip():
        return
    
    # إضافة رسالة المستخدم
    self.add_message(message, is_user=True)
    
    # تعطيل الإدخال مؤقتاً
    self.input_widget.set_enabled(False)
    self.status_label.setText("جاري المعالجة...")
    
    # إرسال للذكاء الاصطناعي
    if self.chat_manager and GROQ_AVAILABLE:
        try:
            # إرسال الرسالة والحصول على الرد
            response = self.chat_manager.send_message(message)
            
            # إضافة رد الذكاء الاصطناعي
            if response:
                self.add_message(response, is_user=False)
                
                # حفظ المحادثة
                if self.history_manager and self.current_session_id:
                    self.history_manager.add_message(
                        self.current_session_id,
                        message,
                        response
                    )
            else:
                self.add_message("عذراً، لم أتمكن من الحصول على رد.", is_user=False)
                
        except Exception as e:
            self.add_message(f"خطأ في الاتصال: {str(e)}", is_user=False)
            print(f"خطأ في إرسال الرسالة: {e}")
    else:
        # رد تجريبي في حالة عدم توفر الذكاء الاصطناعي
        demo_response = f"تم استلام رسالتك: '{message}'. هذا رد تجريبي لأن الذكاء الاصطناعي غير متوفر."
        self.add_message(demo_response, is_user=False)
    
    # إعادة تفعيل الإدخال
    self.input_widget.set_enabled(True)
    self.status_label.setText("جاهز للمحادثة")

def start_new_session(self):
    """بدء جلسة محادثة جديدة"""
    # مسح الرسائل الحالية
    self.clear_messages()
    
    # إنشاء جلسة جديدة
    if self.history_manager:
        self.current_session_id = self.history_manager.create_session(
            title="محادثة جديدة"
        )
    
    # رسالة ترحيب
    welcome_msg = "مرحباً! أنا مساعدك الذكي لتحليل النصوص القرآنية. كيف يمكنني مساعدتك اليوم؟"
    self.add_message(welcome_msg, is_user=False)
    
    self.status_label.setText("بدأت محادثة جديدة")

def clear_messages(self):
    """مسح جميع الرسائل"""
    # حذف جميع فقاعات الرسائل
    for i in reversed(range(self.messages_layout.count())):
        item = self.messages_layout.itemAt(i)
        if item and item.widget() and isinstance(item.widget(), MessageBubble):
            item.widget().deleteLater()
    
    # مسح قائمة الرسائل
    self.messages.clear()

def show_history(self):
    """عرض تاريخ المحادثات"""
    if not self.history_manager:
        QMessageBox.information(
            self, 
            "تاريخ المحادثات", 
            "تاريخ المحادثات غير متوفر حالياً."
        )
        return
    
    try:
        dialog = ChatHistoryDialog(self, self.history_manager)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_session_id:
            self.load_session(dialog.selected_session_id)
    except Exception as e:
        QMessageBox.warning(
            self,
            "خطأ",
            f"خطأ في عرض تاريخ المحادثات: {str(e)}"
        )

def show_settings(self):
    """عرض إعدادات الشات"""
    QMessageBox.information(
        self,
        "الإعدادات",
        "إعدادات الشات ستكون متوفرة قريباً."
    )

def load_session(self, session_id: str):
    """تحميل جلسة محادثة محفوظة"""
    try:
        # مسح الرسائل الحالية
        self.clear_messages()
        
        # تحميل الرسائل من التاريخ
        messages = self.history_manager.get_session_messages(session_id)
        
        for msg in messages:
            # إضافة رسالة المستخدم
            if 'user_message' in msg:
                self.add_message(msg['user_message'], is_user=True)
            
            # إضافة رد الذكاء الاصطناعي
            if 'ai_response' in msg:
                self.add_message(msg['ai_response'], is_user=False)
        
        self.current_session_id = session_id
        self.status_label.setText("تم تحميل المحادثة")
        
    except Exception as e:
        QMessageBox.warning(
            self,
            "خطأ",
            f"خطأ في تحميل المحادثة: {str(e)}"
        )
