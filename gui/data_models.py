#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نماذج البيانات والكلاسات الأساسية
Data models and basic classes for Quran Text Analyzer
"""

from shared_imports import *


@dataclass
class AyahInfo:
    """معلومات الآية"""
    id: int
    surah_no: int
    surah_name_ar: str
    surah_name_en: str
    ayah_no: int
    ayah_text: str
    page: int
    juz: int
    line_start: int
    line_end: int
    coordinates: Optional[Tuple[float, float]] = None
    

@dataclass 
class TextAnalysisResult:
    """نتيجة تحليل النص"""
    original_text: str
    normalized_text: str
    character_count: int
    word_count: int
    unique_characters: List[str]
    character_frequencies: Dict[str, int]
    special_symbols: List[str]
    numbers: List[str]
    diacritics: List[str]
    similarity_score: Optional[float] = None


class SimpleTextProcessor:
    """معالج نصوص بسيط للاستخدام الاحتياطي"""

    def normalize_arabic(self, text: str) -> str:
        """تطبيع النص العربي"""
        # إزالة التشكيل
        text = re.sub(r'[\u064B-\u0652\u0670\u0640]', '', text)
        # توحيد الهمزات
        text = re.sub(r'[أإآ]', 'ا', text)
        text = text.replace('ؤ', 'و')
        text = text.replace('ئ', 'ي')
        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """حساب التشابه بين نصين"""
        # تطبيع النصوص
        norm1 = self.normalize_arabic(text1)
        norm2 = self.normalize_arabic(text2)

        # حساب التشابه البسيط
        if norm1 == norm2:
            return 1.0

        # حساب التشابه بناءً على الأحرف المشتركة
        set1 = set(norm1)
        set2 = set(norm2)

        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0
