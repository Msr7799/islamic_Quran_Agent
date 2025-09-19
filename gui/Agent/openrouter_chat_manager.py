#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import logging
import requests
import pandas as pd
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

@dataclass
class ChatConfig:
    """إعدادات المحادثة"""
    model: str = "qwen/qwen3-4b:free"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9
    stream: bool = False
    system_prompt: str = """أنت مساعد ذكي متخصص في القرآن الكريم والعلوم الإسلامية.

مهامك الأساسية:
- تفسير الآيات القرآنية والأحاديث الشريفة
- الإجابة على الأسئلة الدينية والفقهية
- البحث في قواعد البيانات القرآنية المتاحة
- مساعدة المستخدم في فهم النصوص العربية القديمة
- تقديم المعلومات الإسلامية الموثوقة

الأدوات المتاحة لك:
1. tavily_search: البحث في الإنترنت للحصول على معلومات محدثة
2. get_current_time: الحصول على التاريخ والوقت الحالي
3. convert_timezone: تحويل الأوقات بين المناطق الزمنية المختلفة
4. get_relative_time: حساب الفترة الزمنية منذ تاريخ معين

استخدم هذه الأدوات عند الحاجة لتقديم معلومات دقيقة ومحدثة.

قواعد مهمة:
1. استخدم المصادر الموثوقة فقط
2. اذكر المرجع عند الاقتباس
3. تجنب الفتاوى الشخصية
4. احترم جميع المذاهب الإسلامية
5. عند البحث عن معلومات حديثة، استخدم أداة البحث
6. عند الحاجة لمعلومات زمنية، استخدم أدوات الوقت المناسبة"""

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

class OpenRouterChatManager:
    """مدير المحادثة مع OpenRouter"""
    
    # ثوابت الرسائل
    TAVILY_CLIENT_NOT_AVAILABLE = "TavilyClient غير متوفر"
    
    # التعبيرات النمطية المحسنة
    URL_PATTERN = r'https?://[a-zA-Z\d$\-_.@&+!*(),]+(?:%[a-fA-F\d]{2})*'
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[ChatConfig] = None):
        """
        تهيئة مدير المحادثة
        
        Args:
            api_key: مفتاح API (اختياري، يمكن قراءته من البيئة)
            config: إعدادات المحادثة
        """
        # الحصول على مفاتيح API (أساسي واحتياطي)
        self.primary_api_key = api_key or os.getenv("OPEN_ROUTER_API")
        self.fallback_api_key = os.getenv("OPEN_ROUTER_API2") 
        self.current_api_key = self.primary_api_key
        
        if not self.primary_api_key and not self.fallback_api_key:
            raise ValueError("مفتاح OPEN_ROUTER_API أو OPEN_ROUTER_API2 مطلوب")
            
        # إعداد المسجل أولاً
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # تحميل النماذج المجانية من CSV
        self.available_models = self._load_free_models()

        # Client Tavily إعداد عميل 
        try:
            from tavily import TavilyClient
            tavily_key = os.getenv('TAVILY_API_KEY')
            self.tavily_client = TavilyClient(tavily_key) if tavily_key else None
            if self.tavily_client:
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
        
        # متغير لتوفير البيانات القرآنية كمعلومات إضافية
        self.use_quran_data = True
        self.quran_data_available = False
        self.quran_database = None
        
        # تحميل أدوات MCP المتاحة
        self.mcp_tools = self._load_mcp_tools()
        
        # إضافة رسالة النظام
        self._add_system_message()
        
    def _load_free_models(self) -> Dict[str, Dict[str, Any]]:
        """تحميل النماذج المجانية من ملف CSV"""
        models = {}
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               'openrouter_free_models_snapshot.csv')
        
        try:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                for _, row in df.iterrows():
                    models[row['model_id']] = {
                        "name": row['display_name'],
                        "vendor": row['vendor'],
                        "params": row['params'],
                        "context": row['context_window'],
                        "modalities": row['modalities'],
                        "description": row.get('notes', ''),
                        "pricing_input": row['pricing_input_per_million'],
                        "pricing_output": row['pricing_output_per_million']
                    }
                self.logger.info(f"✅ تم تحميل {len(models)} نموذج مجاني من OpenRouter")
            else:
                # نماذج احتياطية إذا لم يوجد الملف
                models = {
                    "qwen/qwen3-4b:free": {
                        "name": "Qwen3 4B (free)",
                        "vendor": "Qwen",
                        "params": "4B",
                        "context": "~96K",
                        "modalities": "text",
                        "description": "Entry-level Qwen3 open variant"
                    }
                }
                self.logger.warning("⚠️ لم يتم العثور على ملف CSV، استخدام نماذج افتراضية")
        except Exception as e:
            self.logger.error(f"خطأ في تحميل النماذج: {e}")
            models = {
                "qwen/qwen3-4b:free": {
                    "name": "Qwen3 4B (free)",
                    "vendor": "Qwen", 
                    "params": "4B",
                    "context": "96K",
                    "modalities": "text",
                    "description": "Entry-level Qwen3 variant"
                }
            }
        
        return models

    def _load_mcp_tools(self) -> Dict[str, Any]:
        """تحميل أدوات MCP المتاحة من ملف الإعدادات"""
        tools = {}
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                  'mcp_servers_config.json')
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    mcp_config = json.load(f)
                    
                # إضافة الأدوات المدمجة (Tavily و time-mcp)
                if mcp_config.get('tavily', {}).get('enabled', True):
                    tools['tavily_search'] = {
                        "type": "function",
                        "function": {
                            "name": "tavily_search",
                            "description": "بحث في الإنترنت باستخدام Tavily للحصول على معلومات محدثة",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "استعلام البحث"
                                    },
                                    "max_results": {
                                        "type": "integer", 
                                        "description": "عدد النتائج المطلوبة (افتراضي: 5)",
                                        "default": 5
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    }
                    
                if mcp_config.get('time-mcp', {}).get('enabled', True):
                    # إضافة أدوات time-mcp
                    time_tools = {
                        "get_current_time": {
                            "type": "function", 
                            "function": {
                                "name": "get_current_time",
                                "description": "الحصول على التاريخ والوقت الحالي",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "format": {
                                            "type": "string",
                                            "description": "تنسيق التاريخ والوقت",
                                            "default": "YYYY-MM-DD HH:mm:ss"
                                        },
                                        "timezone": {
                                            "type": "string", 
                                            "description": "المنطقة الزمنية",
                                            "default": "UTC"
                                        }
                                    }
                                }
                            }
                        },
                        "convert_timezone": {
                            "type": "function",
                            "function": {
                                "name": "convert_timezone", 
                                "description": "تحويل الوقت بين المناطق الزمنية",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "time": {
                                            "type": "string",
                                            "description": "التاريخ والوقت للتحويل"
                                        },
                                        "from_timezone": {
                                            "type": "string",
                                            "description": "المنطقة الزمنية المصدر"
                                        },
                                        "to_timezone": {
                                            "type": "string", 
                                            "description": "المنطقة الزمنية الهدف"
                                        }
                                    },
                                    "required": ["time", "from_timezone", "to_timezone"]
                                }
                            }
                        },
                        "get_relative_time": {
                            "type": "function",
                            "function": {
                                "name": "get_relative_time",
                                "description": "الحصول على الوقت النسبي منذ تاريخ معين",
                                "parameters": {
                                    "type": "object", 
                                    "properties": {
                                        "time": {
                                            "type": "string",
                                            "description": "التاريخ والوقت للمقارنة"
                                        }
                                    },
                                    "required": ["time"]
                                }
                            }
                        }
                    }
                    tools.update(time_tools)
                    
                # إضافة أي MCP servers إضافية من الملف
                for server_name, server_config in mcp_config.items():
                    if server_name not in ['tavily', 'time-mcp'] and server_config.get('enabled', False):
                        # يمكن إضافة منطق تحميل MCP servers مخصصة هنا
                        pass
                        
                self.logger.info(f"✅ تم تحميل {len(tools)} أداة MCP")
            else:
                # إعدادات افتراضية إذا لم يوجد ملف الإعدادات
                tools = {
                    'tavily_search': {
                        "type": "function",
                        "function": {
                            "name": "tavily_search", 
                            "description": "بحث في الإنترنت باستخدام Tavily",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "استعلام البحث"},
                                    "max_results": {"type": "integer", "default": 5}
                                },
                                "required": ["query"]
                            }
                        }
                    }
                }
                self.logger.info("⚠️ لم يتم العثور على ملف إعدادات MCP، استخدام إعدادات افتراضية")
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحميل أدوات MCP: {e}")
            tools = {}
            
        return tools

    def refresh_mcp_tools(self):
        """إعادة تحميل أدوات MCP من الإعدادات"""
        self.logger.info("🔄 إعادة تحميل أدوات MCP...")
        self.mcp_tools = self._load_mcp_tools()
        self.logger.info(f"✅ تم تحديث {len(self.mcp_tools)} أداة MCP")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """الحصول على قائمة الأدوات المتاحة للنموذج"""
        return list(self.mcp_tools.values())

    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """الحصول على قائمة النماذج المتاحة"""
        return self.available_models.copy()
        
    def set_model(self, model: str):
        """تغيير النموذج المستخدم"""
        if model not in self.available_models:
            raise ValueError(f"النموذج {model} غير متاح")
            
        self.config.model = model
        self.logger.info(f"تم تغيير النموذج إلى: {model}")

    def _add_system_message(self):
        """إضافة رسالة النظام الأولية مع دعم البيانات القرآنية"""
        content = self.config.system_prompt
        
        # إضافة معلومات حول توفر البيانات القرآنية كمصدر إضافي
        if getattr(self, 'use_quran_data', True) and getattr(self, 'quran_data_available', False):
            content += "\n\nمعلومة مهمة: لديك وصول لقاعدة بيانات قرآنية شاملة تحتوي على النص الكامل للقرآن الكريم مع التفسير والمعلومات الإضافية."
        
        # إضافة معلومات حول الأدوات المتاحة
        tools_available = []
        
        if self.tavily_client:
            tools_available.append("البحث في الإنترنت (tavily_search)")
        
        tools_available.extend([
            "الوقت والتاريخ (get_current_time, convert_timezone, get_relative_time)",
        ])
        
        if tools_available:
            content += f"\n\nأدوات متاحة: {', '.join(tools_available)} - يمكنك استخدام هذه الأدوات عند الحاجة لمعلومات حديثة أو حسابات الوقت."
        
        system_msg = Message(
            role="system",
            content=content
        )
        self.messages.append(system_msg)
        
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

    def _make_api_request(self, messages: List[Dict[str, str]], use_stream: bool = False) -> Any:
        """إرسال طلب لـ OpenRouter API"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.current_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://quran-ai-agent.local",
            "X-Title": "Quran AI Agent"
        }
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "stream": use_stream
        }
        
        # إضافة الأدوات المتاحة من MCP
        available_tools = self.get_available_tools()
        
        if available_tools:
            data["tools"] = available_tools
            data["tool_choice"] = "auto"
        
        try:
            response = requests.post(url, headers=headers, json=data, stream=use_stream)
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
                
            return response
            
        except Exception as e:
            # محاولة استخدام API احتياطي عند الفشل
            if self.current_api_key == self.primary_api_key and self.fallback_api_key:
                self.logger.warning(f"فشل المفتاح الأساسي: {e}. جاري التبديل للمفتاح الاحتياطي...")
                self.current_api_key = self.fallback_api_key
                headers["Authorization"] = f"Bearer {self.current_api_key}"
                
                try:
                    response = requests.post(url, headers=headers, json=data, stream=use_stream)
                    if response.status_code != 200:
                        raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
                    
                    self.logger.info("تم التبديل للمفتاح الاحتياطي بنجاح")
                    return response
                    
                except Exception as fallback_error:
                    self.logger.error(f"فشل كلا المفتاحين: {fallback_error}")
                    raise Exception(f"فشل في كلا API keys: الأساسي ({e}) والاحتياطي ({fallback_error})")
            else:
                raise e

    def get_response(self, user_input: str, context: Optional[List[Dict]] = None,
                    stream: Optional[bool] = None) -> str:
        """
        الحصول على رد من النموذج
        """
        # إضافة رسالة المستخدم
        self.add_message("user", user_input)
        
        # تحضير الرسائل
        messages = self._prepare_messages(context)
        
        # تحديد وضع البث
        use_stream = stream if stream is not None else self.config.stream
        
        try:
            return self._generate_response_with_metadata(messages, use_stream)
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على الرد: {str(e)}")
            return self._handle_api_error(e)

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
        
    def _get_standard_response(self, messages: List[Dict[str, str]]) -> str:
        """الحصول على رد عادي (غير متدفق)"""
        response = self._make_api_request(messages, use_stream=False)
        response_json = response.json()
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            choice = response_json['choices'][0]
            message = choice['message']
            
            # فحص إذا كان النموذج يريد استدعاء أداة (tools format الجديد)
            if message.get('tool_calls'):
                tool_calls = message['tool_calls']
                tool_results = []
                
                for tool_call in tool_calls:
                    function_data = tool_call.get('function', {})
                    tool_result = self._handle_function_call(function_data)
                    tool_results.append({
                        "tool_call_id": tool_call.get('id'),
                        "role": "tool",
                        "content": tool_result
                    })
                
                # إضافة نتيجة الأداة وإعادة الطلب
                updated_messages = messages + [
                    {
                        "role": "assistant", 
                        "content": None,
                        "tool_calls": message['tool_calls']
                    }
                ] + tool_results
                
                # إعادة الطلب للحصول على الرد النهائي
                final_response = self._make_api_request(updated_messages, use_stream=False)
                final_json = final_response.json()
                
                if 'choices' in final_json and len(final_json['choices']) > 0:
                    return final_json['choices'][0]['message']['content']
                else:
                    return "تم تنفيذ الأداة بنجاح"
            
            return message.get('content', '')
        else:
            raise Exception("لم يتم تلقي رد صحيح من OpenRouter")
            
    def _get_streaming_response(self, messages: List[Dict[str, str]]) -> str:
        """الحصول على رد متدفق"""
        response = self._make_api_request(messages, use_stream=True)
        
        response_text = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                response_text += content
                    except json.JSONDecodeError:
                        continue
                        
        return response_text

    def _handle_api_error(self, error: Exception) -> str:
        """معالجة أخطاء API بطريقة مناسبة"""
        error_str = str(error).lower()
        
        if "rate_limit" in error_str or "429" in error_str:
            return "عذراً، تم تجاوز حد الاستخدام. الرجاء المحاولة بعد قليل."
        elif "api_key" in error_str or "401" in error_str:
            return "خطأ في مفتاح API. الرجاء التحقق من الإعدادات."
        elif "model" in error_str or "404" in error_str:
            return f"النموذج {self.config.model} غير متاح حالياً."
        else:
            return f"حدث خطأ: {str(error)}"

    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات المحادثة"""
        user_messages = [m for m in self.messages if m.role == "user"]
        assistant_messages = [m for m in self.messages if m.role == "assistant"]
        
        return {
            "total_messages": len(self.messages) - 1,  # باستثناء رسالة النظام
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "current_model": self.config.model,
            "conversation_start": self.messages[0].timestamp if self.messages else None,
            "quran_data_enabled": self.use_quran_data,
            "quran_data_available": self.quran_data_available
        }

    # وظائف إضافية لدعم نفس الواجهة مثل GroqChatManager
    def set_quran_database(self, database):
        """تعيين قاعدة البيانات القرآنية كمصدر معلومات إضافي"""
        self.quran_database = database
        self.quran_data_available = database is not None
        self.logger.info(f"تم {'تعيين' if database else 'إزالة'} قاعدة البيانات القرآنية كمصدر معلومات إضافي")
        
    def toggle_quran_data(self, enabled: bool):
        """تفعيل أو إلغاء استخدام البيانات القرآنية كمعلومات إضافية"""
        self.use_quran_data = enabled
        self.logger.info(f"تم {'تفعيل' if enabled else 'إلغاء'} استخدام البيانات القرآنية كمعلومات إضافية")

    def toggle_internet(self, enabled: bool):
        """تفعيل أو إلغاء استخدام خدمات الإنترنت (Tavily)"""
        if enabled and not self.tavily_client:
            self.logger.warning("لا يمكن تفعيل البحث بالإنترنت - TavilyClient غير متوفر")
            return False
            
        self.use_internet = enabled
            
        if not enabled:
            self.original_tavily_client = getattr(self, 'tavily_client', None)
            self.tavily_client = None
        else:
            original_client = getattr(self, 'original_tavily_client', None)
            if original_client:
                self.tavily_client = original_client
                
        self.logger.info(f"تم {'تفعيل' if enabled else 'إلغاء'} استخدام خدمات الإنترنت")
        return True

    def _get_tavily_tools(self) -> List[Dict[str, Any]]:
        """تعريف أدوات Tavily للنماذج (تنسيق tools الجديد)"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "tavily_search",
                    "description": "البحث في الإنترنت للحصول على معلومات حديثة ومصادر موثوقة",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "استعلام البحث باللغة العربية أو الإنجليزية"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "عدد النتائج المطلوبة (افتراضي: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def _get_time_tools(self) -> List[Dict[str, Any]]:
        """تعريف أدوات time-mcp للنماذج (تنسيق tools الجديد)"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "description": "الحصول على الوقت والتاريخ الحالي",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "format": {
                                "type": "string",
                                "description": "تنسيق الوقت المطلوب (افتراضي: YYYY-MM-DD HH:mm:ss)",
                                "default": "YYYY-MM-DD HH:mm:ss"
                            },
                            "timezone": {
                                "type": "string",
                                "description": "المنطقة الزمنية (افتراضي: UTC)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "convert_timezone",
                    "description": "تحويل الوقت بين المناطق الزمنية",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sourceTimezone": {
                                "type": "string",
                                "description": "المنطقة الزمنية المصدر (مثل: Asia/Riyadh)"
                            },
                            "targetTimezone": {
                                "type": "string", 
                                "description": "المنطقة الزمنية المستهدفة (مثل: Europe/London)"
                            },
                            "time": {
                                "type": "string",
                                "description": "الوقت المراد تحويله بصيغة YYYY-MM-DD HH:mm:ss"
                            }
                        },
                        "required": ["sourceTimezone", "targetTimezone", "time"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_relative_time",
                    "description": "حساب الوقت النسبي (منذ متى أو بعد كم)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "time": {
                                "type": "string",
                                "description": "الوقت المرجعي بصيغة YYYY-MM-DD HH:mm:ss"
                            }
                        },
                        "required": ["time"]
                    }
                }
            }
        ]

    def _handle_function_call(self, function_call: Dict[str, Any]) -> str:
        """معالجة استدعاءات الأدوات من النماذج"""
        function_name = function_call.get("name")
        
        if function_name == "tavily_search":
            try:
                import json
                args = json.loads(function_call.get("arguments", "{}"))
                query = args.get("query", "")
                max_results = args.get("max_results", 5)
                
                if not query:
                    return "❌ خطأ: لم يتم توفير استعلام البحث"
                
                # تنفيذ البحث باستخدام Tavily
                search_results = self.tavily_client.search(
                    query=query,
                    max_results=max_results,
                    search_depth="basic"
                )
                
                # تنسيق النتائج
                formatted_results = self._format_tavily_results(search_results, query)
                return formatted_results
                
            except Exception as e:
                self.logger.error(f"خطأ في البحث: {e}")
                return f"❌ خطأ في البحث في الإنترنت: {str(e)}"
        
        # معالجة وظائف الوقت
        elif function_name in ["get_current_time", "convert_timezone", "get_relative_time"]:
            try:
                import json
                from datetime import datetime, timezone
                import pytz
                
                args = json.loads(function_call.get("arguments", "{}"))
                
                if function_name == "get_current_time":
                    format_str = args.get("format", "YYYY-MM-DD HH:mm:ss")
                    tz_name = args.get("timezone", "Asia/Riyadh")
                    
                    try:
                        tz = pytz.timezone(tz_name)
                        now = datetime.now(tz)
                        
                        # تحويل التنسيق
                        if format_str == "YYYY-MM-DD HH:mm:ss":
                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                        elif format_str == "YYYY-MM-DD":
                            formatted_time = now.strftime("%Y-%m-%d")
                        elif format_str == "h:mm A":
                            formatted_time = now.strftime("%I:%M %p")
                        else:
                            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
                            
                        return f"⏰ الوقت الحالي في {tz_name}: {formatted_time}"
                    except:
                        now = datetime.now()
                        return f"⏰ الوقت الحالي: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                
                elif function_name == "convert_timezone":
                    time_str = args.get("time", "")
                    source_tz = args.get("source_timezone", "Asia/Riyadh")
                    target_tz = args.get("target_timezone", "Europe/London")
                    
                    if not time_str:
                        return "❌ خطأ: لم يتم توفير الوقت للتحويل"
                    
                    try:
                        source_timezone = pytz.timezone(source_tz)
                        target_timezone = pytz.timezone(target_tz)
                        
                        # تحليل الوقت
                        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                        dt = source_timezone.localize(dt)
                        converted_dt = dt.astimezone(target_timezone)
                        
                        return f"🌍 تحويل الوقت:\n📍 من {source_tz}: {time_str}\n📍 إلى {target_tz}: {converted_dt.strftime('%Y-%m-%d %H:%M:%S')}"
                    except Exception as e:
                        return f"❌ خطأ في تحويل الوقت: {str(e)}"
                
                elif function_name == "get_relative_time":
                    time_str = args.get("time", "")
                    
                    if not time_str:
                        return "❌ خطأ: لم يتم توفير الوقت للمقارنة"
                    
                    try:
                        target_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                        now = datetime.now()
                        diff = now - target_dt
                        
                        if diff.days > 0:
                            return f"📅 منذ {diff.days} يوم"
                        elif diff.seconds > 3600:
                            hours = diff.seconds // 3600
                            return f"⏱️ منذ {hours} ساعة"
                        elif diff.seconds > 60:
                            minutes = diff.seconds // 60
                            return f"⏲️ منذ {minutes} دقيقة"
                        else:
                            return f"⚡ منذ {diff.seconds} ثانية"
                    except Exception as e:
                        return f"❌ خطأ في حساب الوقت النسبي: {str(e)}"
                        
            except Exception as e:
                self.logger.error(f"خطأ في معالجة الوقت: {e}")
                return f"❌ خطأ في معالجة الوقت: {str(e)}"
        
        return f"❌ وظيفة غير مدعومة: {function_name}"

    def _format_tavily_results(self, results: Dict[str, Any], query: str) -> str:
        """تنسيق نتائج Tavily للعرض"""
        try:
            formatted = f"🔍 **نتائج البحث لـ: {query}**\n\n"
            
            # الإجابة المباشرة إن وجدت
            if results.get('answer'):
                formatted += f"📝 **الإجابة المباشرة:**\n{results['answer']}\n\n"
            
            # النتائج
            search_results = results.get('results', [])
            if search_results:
                formatted += "📚 **المصادر:**\n"
                for i, result in enumerate(search_results[:5], 1):
                    title = result.get('title', 'بدون عنوان')
                    url = result.get('url', '')
                    content = result.get('content', '')[:200] + '...' if len(result.get('content', '')) > 200 else result.get('content', '')
                    
                    formatted += f"\n{i}. **{title}**\n"
                    if content:
                        formatted += f"   {content}\n"
                    if url:
                        formatted += f"   🔗 [المصدر]({url})\n"
            
            return formatted
            
        except Exception as e:
            self.logger.error(f"خطأ في تنسيق النتائج: {e}")
            return f"❌ خطأ في تنسيق النتائج: {str(e)}"

    def toggle_database(self, enabled: bool):
        """تفعيل أو إلغاء استخدام قاعدة البيانات القرآنية"""
        self.toggle_quran_data(enabled)
        self.logger.info(f"تم {'تفعيل' if enabled else 'إلغاء'} قاعدة البيانات القرآنية")
        return True

    def __del__(self):
        """تنظيف الموارد"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

# دالة مساعدة لاختبار المدير
def test_openrouter_manager():
    """اختبار مدير OpenRouter"""
    try:
        # إنشاء مدير
        manager = OpenRouterChatManager()
        
        print("✅ تم إنشاء مدير OpenRouter بنجاح")
        print(f"📋 النموذج المستخدم: {manager.config.model}")
        print(f"🔧 النماذج المتاحة: {len(manager.get_available_models())} نموذج")
        
        # عرض بعض النماذج
        models = manager.get_available_models()
        for i, (model_id, info) in enumerate(list(models.items())[:3]):
            print(f"  {i+1}. {info['name']} ({info['vendor']})")
        
        # اختبار محادثة بسيطة
        response = manager.get_response("ما هي سورة الفاتحة؟")
        print(f"\n💬 الرد: {response[:200]}...")
        
        # عرض الإحصائيات
        stats = manager.get_stats()
        print(f"\n📊 الإحصائيات: {stats}")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    test_openrouter_manager()
