#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
معالج النصوص - نقطة دخول موحدة
يعيد توجيه جميع الاستدعاءات إلى المعالج المتطور
"""

# إعادة تصدير المكونات المحددة من المعالج المتطور
from .text_processor_advanced import AdvancedTextProcessor, TextAnalysis

# للتوافق مع الإصدارات القديمة
ArabicTextProcessor = AdvancedTextProcessor

# إضافة دالة للتوافق
def normalize_arabic(text):
    """دالة للتوافق مع الكود القديم"""
    processor = AdvancedTextProcessor()
    return processor.normalize_text(text)

# إعادة تصدير للتوافق مع الكود الموجود
__all__ = [
    'AdvancedTextProcessor',
    'ArabicTextProcessor',
    'TextAnalysis',
]

# للاستخدام المباشر
if __name__ == "__main__":
    processor = AdvancedTextProcessor()
    print("✅ تم تحميل معالج النصوص المتطور بنجاح!")
