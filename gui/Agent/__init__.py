#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مجلد Agent - مكونات الذكاء الاصطناعي
"""

from .groq_chat_manager import GroqChatManager
from .chat_history_manager import ChatHistoryManager, ChatMessage, ChatSession
from .quran_api_manager import QuranComplexAPI
from .ai_analyzer import AIAnalyzer
from .search_engine import TavilySearchEngine
from .text_processor_advanced import AdvancedTextProcessor, TextAnalysis
from .text_processor import ArabicTextProcessor
from .font_manager import AdvancedFontManager
# أضف فقط ما تحتاجه فعلاً

__all__ = [
    'GroqChatManager',
    'ChatHistoryManager',
    'ChatMessage',
    'ChatSession',
    'QuranComplexAPI',
    'AIAnalyzer',
    'TavilySearchEngine',
    'AdvancedTextProcessor',
    'ArabicTextProcessor',
    'TextAnalysis',
    'AdvancedFontManager'
]

print("✅ تم تحميل مكونات Agent بنجاح")
