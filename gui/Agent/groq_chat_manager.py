#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import json
import time
import logging
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️ مكتبة groq غير مثبتة. الرجاء تثبيتها: pip install groq")


@dataclass
class ChatConfig:
    """إعدادات المحادثة"""
    model: str = "mixtral-8x7b-32768"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9
    stream: bool = False
    system_prompt: str = """أنت مساعد ذكي متخصص في القرآن الكريم والعلوم الإسلامية.
    
مهامك الأساسية:

قواعد مهمة:
    system_prompt: str = """


@dataclass
class Message:
    """رسالة في المحادثة"""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
            
    def to_dict(self) -> Dict[str, str]:
        """تحويل إلى قاموس للAPI"""
        return {
            "role": self.role,
            "content": self.content
        }


class GroqChatManager:
    """مدير المحادثة مع Groq"""
    
    # ثوابت الرسائل
    TAVILY_CLIENT_NOT_AVAILABLE = "TavilyClient غير متوفر"
    
    # التعبيرات النمطية المحسنة
    URL_PATTERN = r'https?://[a-zA-Z\d$\-_.@&+!*(),]+(?:%[a-fA-F\d]{2})*'
    
    # النماذج المتاحة
    AVAILABLE_MODELS = {
        "mixtral-8x7b-32768": {
            "name": "Mixtral 8x7B",
            "context": 32768,
            "description": "نموذج قوي متعدد الاستخدامات"
        },
        "llama3-70b-8192": {
            "name": "Llama 3 70B",
            "context": 8192,
            "description": "نموذج متقدم من Meta"
        },
        "llama3-8b-8192": {
            "name": "Llama 3 8B",
            "context": 8192,
            "description": "نموذج سريع وفعال"
        },
        "gemma-7b-it": {
            "name": "Gemma 7B",
            "context": 8192,
            "description": "نموذج من Google"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[ChatConfig] = None):
        """
        تهيئة مدير المحادثة
        
        Args:
            api_key: مفتاح API (اختياري، يمكن قراءته من البيئة)
            config: إعدادات المحادثة
        """
        # التحقق من توفر المكتبة
        if not GROQ_AVAILABLE:
            raise ImportError("مكتبة groq غير مثبتة")
            
        # الحصول على مفتاح API
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("مفتاح GROQ_API_KEY مطلوب")
            
        # تهيئة العميل
        self.client = Groq(api_key=self.api_key)
        
        # إعداد المسجل أولاً
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Client Tavily إعداد عميل 
        try:
            from tavily import TavilyClient
            tavily_key = os.getenv('TAVILY_API_KEY')
            self.tavily_client = TavilyClient(tavily_key)
            self.logger.info("تم إعداد TavilyClient بنجاح")
        except ImportError as e:
            self.tavily_client = None
            self.logger.error(f"خطأ في إعداد TavilyClient: {e}")

        # الإعدادات
        self.config = config or ChatConfig()
        
        # سجل المحادثة
        self.messages: List[Message] = []
        
        # معالج الخيوط للعمليات المتزامنة
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # متغير لتوفير البيانات القرآنية كمعلومات إضافية (ليس تقييد)
        self.use_quran_data = True
        self.quran_data_available = False
        self.quran_database = None
        
        # إضافة رسالة النظام
        self._add_system_message()
        
    def set_quran_database(self, database):
        """
        تعيين قاعدة البيانات القرآنية كمصدر معلومات إضافي
        Args:
            database: قاعدة البيانات القرآنية
        """
        self.quran_database = database
        self.quran_data_available = database is not None
        self.logger.info(f"تم {'تعيين' if database else 'إزالة'} قاعدة البيانات القرآنية كمصدر معلومات إضافي")
        
    def toggle_quran_data(self, enabled: bool):
        """
        تفعيل أو إلغاء استخدام البيانات القرآنية كمعلومات إضافية
        Args:
            enabled: إذا True يتم استخدام البيانات، إذا False لا يتم استخدامها
        """
        self.use_quran_data = enabled
        self.logger.info(f"تم {'تفعيل' if enabled else 'إلغاء'} استخدام البيانات القرآنية كمعلومات إضافية")

    def toggle_internet(self, enabled: bool):
        """
        تفعيل أو إلغاء استخدام خدمات الإنترنت (Tavily)
        Args:
            enabled: إذا True يتم تفعيل البحث بالإنترنت، إذا False يتم إلغاؤه
        """
        if enabled and not self.tavily_client:
            self.logger.warning("لا يمكن تفعيل البحث بالإنترنت - TavilyClient غير متوفر")
            return False
            
        # تعيين حالة استخدام الإنترنت
        self.use_internet = enabled
            
        if not enabled:
            self.original_tavily_client = getattr(self, 'tavily_client', None)
            self.tavily_client = None
        else:
            # استعادة العميل الأصلي إذا كان متوفراً
            original_client = getattr(self, 'original_tavily_client', None)
            if original_client:
                self.tavily_client = original_client
                
        self.logger.info(f"تم {'تفعيل' if enabled else 'إلغاء'} استخدام خدمات الإنترنت")
        return True

    def toggle_database(self, enabled: bool):
        """
        تفعيل أو إلغاء استخدام قاعدة البيانات القرآنية
        Args:
            enabled: إذا True يتم تفعيل قاعدة البيانات، إذا False يتم إلغاؤها
        """
        # هذه الدالة مشابهة لدالة toggle_quran_data
        self.toggle_quran_data(enabled)
        self.logger.info(f"تم {'تفعيل' if enabled else 'إلغاء'} قاعدة البيانات القرآنية")
        return True
        
    def _add_system_message(self):
        """إضافة رسالة النظام الأولية مع دعم البيانات القرآنية"""
        content = self.config.system_prompt
        
        # إضافة معلومات حول توفر البيانات القرآنية كمصدر إضافي
        if getattr(self, 'use_quran_data', True) and getattr(self, 'quran_data_available', False):
            content += "\n\nمعلومة مهمة: لديك وصول لقاعدة بيانات قرآنية شاملة تحتوي على النص الكامل للقرآن الكريم مع التفسير والمعلومات الإضافية. يمكنك استخدام هذه البيانات مع معرفتك الطبيعية لتقديم إجابات أكثر دقة وتفصيلاً."
        
        system_msg = Message(
            role="system",
            content=content
        )
        self.messages.append(system_msg)
        
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """الحصول على قائمة النماذج المتاحة"""
        return self.AVAILABLE_MODELS.copy()
        
    def set_model(self, model: str):
        """تغيير النموذج المستخدم"""
        if model not in self.AVAILABLE_MODELS:
            raise ValueError(f"النموذج {model} غير متاح")
            
        self.config.model = model
        self.logger.info(f"تم تغيير النموذج إلى: {model}")
        
    def clear_conversation(self):
        """مسح سجل المحادثة"""
        self.messages = []
        self._add_system_message()
        self.logger.info("تم مسح سجل المحادثة")
        
    def add_message(self, role: str, content: str) -> Message:
        """إضافة رسالة للسجل"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        return message
        
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """الحصول على سجل المحادثة"""
        return [asdict(msg) for msg in self.messages]
        
    def _prepare_messages(self, context: Optional[List[Dict]] = None) -> List[Dict[str, str]]:
        """تحضير الرسائل للإرسال"""
        messages = []
        
        # إضافة رسالة النظام
        messages.append(self.messages[0].to_dict())
        
        # إضافة السياق إن وجد
        if context:
            for ctx in context:
                messages.append({
                    "role": ctx.get("role", "user"),
                    "content": ctx.get("content", "")
                })
                
        # إضافة الرسائل الأخيرة من السجل (مع حد أقصى)
        recent_messages = self.messages[-10:] if len(self.messages) > 10 else self.messages[1:]
        for msg in recent_messages:
            messages.append(msg.to_dict())
            
        return messages
        
    def use_tavily_search(self, query: str) -> str:
        """البحث باستخدام Tavily"""
        try:
            if not self.tavily_client:
                return self.TAVILY_CLIENT_NOT_AVAILABLE
            
            results = self.tavily_client.search(query=query)
            return f"نتائج البحث عن '{query}': {results}"
        except Exception as e:
            self.logger.error(f"خطأ في البحث: {e}")
            return f"خطأ في البحث: {str(e)}"
    
    def use_tavily_extract(self, urls: list) -> str:
        """استخراج محتوى من URLs باستخدام Tavily"""
        try:
            if not self.tavily_client:
                return self.TAVILY_CLIENT_NOT_AVAILABLE
            
            results = self.tavily_client.extract(urls=urls)
            return f"نتائج الاستخراج من {len(urls)} رابط: {results}"
        except Exception as e:
            self.logger.error(f"خطأ في الاستخراج: {e}")
            return f"خطأ في الاستخراج: {str(e)}"
    
    def use_tavily_crawl(self, url: str, depth: str = "advanced") -> str:
        """تتبع موقع باستخدام Tavily"""
        try:
            if not self.tavily_client:
                return self.TAVILY_CLIENT_NOT_AVAILABLE
            
            results = self.tavily_client.crawl(url=url, extract_depth=depth)
            return f"نتائج تتبع الموقع '{url}': {results}"
        except Exception as e:
            self.logger.error(f"خطأ في التتبع: {e}")
            return f"خطأ في التتبع: {str(e)}"
    
    def detect_and_use_tavily(self, user_input: str) -> Optional[str]:
        """كشف واستخدام أدوات Tavily بناءً على المدخل"""
        if not self.tavily_client:
            return None
        
        user_input_lower = user_input.lower()
        
        # كشف طلبات البحث
        search_keywords = ['ابحث', 'بحث', 'search', 'find', 'معلومات عن', 'ما هو']
        if any(keyword in user_input_lower for keyword in search_keywords):
            # استخراج الاستعلام من النص
            query = user_input
            for keyword in search_keywords:
                if keyword in user_input_lower:
                    query = user_input.split(keyword)[-1].strip()
                    break
            
            search_result = self.use_tavily_search(query)
            return search_result
        
        # كشف طلبات الاستخراج
        extract_keywords = ['استخرج', 'extract', 'اقرأ من', 'محتوى']
        if any(keyword in user_input_lower for keyword in extract_keywords):
            # البحث عن URLs في النص
            import re
            urls = re.findall(self.URL_PATTERN, user_input)
            if urls:
                extract_result = self.use_tavily_extract(urls)
                return extract_result
        
        # كشف طلبات التتبع
        crawl_keywords = ['تتبع', 'crawl', 'اكتشف الموقع', 'اقرأ الموقع']
        if any(keyword in user_input_lower for keyword in crawl_keywords):
            import re
            urls = re.findall(self.URL_PATTERN, user_input)
            if urls:
                crawl_result = self.use_tavily_crawl(urls[0])
                return crawl_result
        
        return None
    
    def _prepare_enhanced_context(self, user_input: str, context: Optional[List[Dict]] = None) -> List[Dict]:
        """تحضير السياق المحسن مع البيانات الإضافية"""
        enhanced_context = context or []
        
        # محاولة استخدام أدوات Tavily
        tavily_result = self.detect_and_use_tavily(user_input)
        if tavily_result:
            enhanced_context.append({
                "role": "system",
                "content": f"معلومات من الإنترنت: {tavily_result}"
            })
        
        # إضافة البيانات القرآنية إذا كانت متاحة
        if self.use_quran_data and self.quran_data_available and self.quran_database:
            quran_context = self._get_relevant_quran_data(user_input)
            if quran_context:
                enhanced_context.append({
                    "role": "system",
                    "content": f"بيانات قرآنية ذات صلة: {quran_context}"
                })
        
        return enhanced_context

    def _handle_api_error(self, error: Exception) -> str:
        """معالجة أخطاء API بطريقة مناسبة"""
        error_str = str(error).lower()
        
        if "rate_limit" in error_str:
            return "عذراً، تم تجاوز حد الاستخدام. الرجاء المحاولة بعد قليل."
        elif "api_key" in error_str:
            return "خطأ في مفتاح API. الرجاء التحقق من الإعدادات."
        elif "model" in error_str:
            return f"النموذج {self.config.model} غير متاح حالياً."
        else:
            return f"حدث خطأ: {str(error)}"

    def _generate_response_with_metadata(self, messages: List[Dict[str, str]], use_stream: bool) -> str:
        """توليد الرد مع حفظ البيانات الوصفية"""
        start_time = time.time()
        
        if use_stream:
            response_text = self._get_streaming_response(messages)
        else:
            response_text = self._get_standard_response(messages)
            
        # حساب وقت الاستجابة وحفظ البيانات الوصفية
        response_time = time.time() - start_time
        assistant_msg = self.add_message("assistant", response_text)
        assistant_msg.metadata = {
            "model": self.config.model,
            "response_time": response_time,
            "tokens": len(response_text.split())
        }
        
        self.logger.info(f"تم الحصول على رد في {response_time:.2f} ثانية")
        return response_text
    
    def get_response(self, user_input: str, context: Optional[List[Dict]] = None,
                    stream: Optional[bool] = None) -> str:
        """
        الحصول على رد من النموذج
        
        Args:
            user_input: مدخل المستخدم
            context: سياق إضافي للمحادثة
            stream: تفعيل الرد المتدفق
            
        Returns:
            رد النموذج
        """
        # إضافة رسالة المستخدم
        self.add_message("user", user_input)
        
        # تحضير السياق المحسن
        enhanced_context = self._prepare_enhanced_context(user_input, context)
        
        # تحضير الرسائل
        messages = self._prepare_messages(enhanced_context)
        
        # تحديد وضع البث
        use_stream = stream if stream is not None else self.config.stream
        
        try:
            return self._generate_response_with_metadata(messages, use_stream)
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على الرد: {str(e)}")
            return self._handle_api_error(e)
                
    def _get_standard_response(self, messages: List[Dict[str, str]]) -> str:
        """الحصول على رد عادي (غير متدفق)"""
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            top_p=self.config.top_p,
            stream=False
        )
        
        return response.choices[0].message.content
        
    def _get_streaming_response(self, messages: List[Dict[str, str]]) -> str:
        """الحصول على رد متدفق"""
        stream = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            top_p=self.config.top_p,
            stream=True
        )
        
        response_text = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response_text += chunk.choices[0].delta.content
                
        return response_text
        
    async def get_response_async(self, user_input: str, 
                                context: Optional[List[Dict]] = None) -> str:
        """الحصول على رد بشكل غير متزامن"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.get_response,
            user_input,
            context,
            False
        )
        
    def stream_response(self, user_input: str, 
                       context: Optional[List[Dict]] = None) -> Generator[str, None, None]:
        """
        الحصول على رد متدفق
        
        Yields:
            أجزاء من الرد
        """
        # إضافة رسالة المستخدم
        self.add_message("user", user_input)
        
        # تحضير الرسائل
        messages = self._prepare_messages(context)
        
        try:
            stream = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
                    
            # إضافة الرد الكامل للسجل
            self.add_message("assistant", full_response)
            
        except Exception as e:
            self.logger.error(f"خطأ في البث: {str(e)}")
            yield f"خطأ: {str(e)}"
            
    def export_conversation(self, format: str = "json") -> str:
        """
        تصدير المحادثة
        
        Args:
            format: صيغة التصدير ("json", "text", "markdown")
            
        Returns:
            المحادثة المصدرة
        """
        if format == "json":
            return json.dumps(
                self.get_conversation_history(),
                ensure_ascii=False,
                indent=2
            )
        elif format == "text":
            text = ""
            for msg in self.messages[1:]:  # تخطي رسالة النظام
                text += f"{msg.role.upper()}: {msg.content}\n\n"
            return text.strip()
        elif format == "markdown":
            md = "# سجل المحادثة\n\n"
            for msg in self.messages[1:]:
                if msg.role == "user":
                    md += f"### 👤 المستخدم\n{msg.content}\n\n"
                elif msg.role == "assistant":
                    md += f"### 🤖 المساعد\n{msg.content}\n\n"
            return md
        else:
            raise ValueError(f"صيغة غير مدعومة: {format}")
            
    def get_token_count(self) -> int:
        """حساب عدد التوكنات المستخدمة (تقريبي)"""
        total_tokens = 0
        for msg in self.messages:
            # تقدير: كلمة واحدة = 1.3 توكن تقريباً
            total_tokens += int(len(msg.content.split()) * 1.3)
        return total_tokens
        
    def _get_relevant_quran_data(self, user_input: str) -> Optional[str]:
        """
        البحث عن بيانات قرآنية ذات صلة بسؤال المستخدم
        
        Args:
            user_input: سؤال المستخدم
            
        Returns:
            نص يحتوي على البيانات القرآنية ذات الصلة
        """
        if not self.quran_database:
            return None
            
        try:
            # تطبيق منطق البحث في قاعدة البيانات القرآنية
            # يمكن تحسين هذا الجزء لاحقاً
            keywords = user_input.split()
            relevant_data = []
            
            # البحث عن آيات أو سور ذات صلة
            for keyword in keywords:
                if len(keyword) > 2:  # تجاهل الكلمات القصيرة
                    # هنا يمكن إضافة منطق البحث الفعلي
                    pass
                    
            return "\n".join(relevant_data) if relevant_data else None
            
        except Exception as e:
            self.logger.error(f"خطأ في البحث عن البيانات القرآنية: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات المحادثة"""
        user_messages = [m for m in self.messages if m.role == "user"]
        assistant_messages = [m for m in self.messages if m.role == "assistant"]
        
        return {
            "total_messages": len(self.messages) - 1,  # باستثناء رسالة النظام
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "estimated_tokens": self.get_token_count(),
            "current_model": self.config.model,
            "conversation_start": self.messages[0].timestamp if self.messages else None,
            "quran_data_enabled": self.use_quran_data,
            "quran_data_available": self.quran_data_available
        }
        
    def __del__(self):
        """تنظيف الموارد"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# دالة مساعدة لاختبار المدير
def test_groq_manager():
    """اختبار مدير Groq"""
    try:
        # إنشاء مدير
        manager = GroqChatManager()
        
        print("✅ تم إنشاء مدير Groq بنجاح")
        print(f"📋 النموذج المستخدم: {manager.config.model}")
        print(f"🔧 النماذج المتاحة: {list(manager.get_available_models().keys())}")
        
        # اختبار محادثة بسيطة
        response = manager.get_response("ما هي سورة الفاتحة؟")
        print(f"\n💬 الرد: {response[:200]}...")
        
        # عرض الإحصائيات
        stats = manager.get_stats()
        print(f"\n📊 الإحصائيات: {stats}")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")


if __name__ == "__main__":
    test_groq_manager()
