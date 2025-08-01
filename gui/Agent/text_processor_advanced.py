#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
معالج النصوص المتطور للنصوص القرآنية العثمانية
يتعامل مع جميع أنواع النصوص والرموز العثمانية بدقة عالية

المميزات:
- تطبيع متطور للنصوص العربية والعثمانية
- خوارزميات مطابقة ذكية متعددة المستويات  
- معالجة الرموز المركبة والمتداخلة
- دعم اللهجات والقراءات المختلفة
- تحليل شامل للنصوص
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Optional, Set, Any
from difflib import SequenceMatcher
from collections import Counter, defaultdict
import numpy as np
from dataclasses import dataclass
import Levenshtein
import logging
from functools import lru_cache
import arabic_reshaper
from bidi.algorithm import get_display

@dataclass
class TextAnalysis:
    """نتائج تحليل النص"""
    original_text: str
    normalized_text: str
    clean_text: str
    character_count: Dict[str, int]
    word_count: int
    line_count: int
    symbols_analysis: Dict[str, Any]
    verse_numbers: List[Dict[str, Any]]
    special_marks: List[Dict[str, Any]]
    language_confidence: float
    
class AdvancedTextProcessor:
    """معالج النصوص المتطور للنصوص القرآنية"""
    
    # قواميس التطبيع الشاملة
    NORMALIZATION_RULES = {
        # الألف وأشكالها
        'alef_variants': {
            'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا',
            'ﺃ': 'ا', 'ﺇ': 'ا', 'ﺁ': 'ا', 'ﺍ': 'ا', 'ﺎ': 'ا',
            '\u0671': 'ا',  # ألف وصل
            '\u0672': 'ا',  # ألف مع وصلة
            '\u0673': 'ا',  # ألف مع وصلة ممدودة
            '\u0675': 'ا',  # ألف مع رأس واو
        },
        
        # الياء والألف المقصورة
        'yaa_variants': {
            'ى': 'ي', 'ﻯ': 'ي', 'ﻰ': 'ي', 'ﻱ': 'ي', 'ﻲ': 'ي',
            '\u0649': 'ي',  # ألف مقصورة
            '\u064A': 'ي',  # ياء
            '\u06CC': 'ي',  # ياء فارسية
        },
        
        # التاء المربوطة والهاء
        'taa_marbuta': {
            'ة': 'ه', 'ﺓ': 'ه', 'ﺔ': 'ه',
        },
        
        # الواو وأشكالها
        'waw_variants': {
            'ؤ': 'و', 'ﻭ': 'و', 'ﻮ': 'و',
            '\u06C4': 'و',  # واو مع نقطة فوقية
            '\u06C5': 'و',  # واو مع حرف صغير فوقي
            '\u06C6': 'و',  # واو مع حرف صغير تحتي
        },
        
        # الهمزة وأشكالها
        'hamza_variants': {
            'ء': '', 'ئ': 'ي', 'ؤ': 'و',
            '\u0674': '',  # همزة عالية
            '\u0675': '',  # همزة مع واو
        },
        
        # أشكال الحروف المختلفة (Presentation Forms)
        'letter_forms': {
            # الباء
            'ﺏ': 'ب', 'ﺐ': 'ب', 'ﺑ': 'ب', 'ﺒ': 'ب',
            # التاء
            'ﺕ': 'ت', 'ﺖ': 'ت', 'ﺗ': 'ت', 'ﺘ': 'ت',
            # الثاء
            'ﺙ': 'ث', 'ﺚ': 'ث', 'ﺛ': 'ث', 'ﺜ': 'ث',
            # الجيم
            'ﺝ': 'ج', 'ﺞ': 'ج', 'ﺟ': 'ج', 'ﺠ': 'ج',
            # الحاء
            'ﺡ': 'ح', 'ﺢ': 'ح', 'ﺣ': 'ح', 'ﺤ': 'ح',
            # الخاء
            'ﺥ': 'خ', 'ﺦ': 'خ', 'ﺧ': 'خ', 'ﺨ': 'خ',
            # الدال
            'ﺩ': 'د', 'ﺪ': 'د',
            # الذال
            'ﺫ': 'ذ', 'ﺬ': 'ذ',
            # الراء
            'ﺭ': 'ر', 'ﺮ': 'ر',
            # الزاي
            'ﺯ': 'ز', 'ﺰ': 'ز',
            # السين
            'ﺱ': 'س', 'ﺲ': 'س', 'ﺳ': 'س', 'ﺴ': 'س',
            # الشين
            'ﺵ': 'ش', 'ﺶ': 'ش', 'ﺷ': 'ش', 'ﺸ': 'ش',
            # الصاد
            'ﺹ': 'ص', 'ﺺ': 'ص', 'ﺻ': 'ص', 'ﺼ': 'ص',
            # الضاد
            'ﺽ': 'ض', 'ﺾ': 'ض', 'ﺿ': 'ض', 'ﻀ': 'ض',
            # الطاء
            'ﻁ': 'ط', 'ﻂ': 'ط', 'ﻃ': 'ط', 'ﻄ': 'ط',
            # الظاء
            'ﻅ': 'ظ', 'ﻆ': 'ظ', 'ﻇ': 'ظ', 'ﻈ': 'ظ',
            # العين
            'ﻉ': 'ع', 'ﻊ': 'ع', 'ﻋ': 'ع', 'ﻌ': 'ع',
            # الغين
            'ﻍ': 'غ', 'ﻎ': 'غ', 'ﻏ': 'غ', 'ﻐ': 'غ',
            # الفاء
            'ﻑ': 'ف', 'ﻒ': 'ف', 'ﻓ': 'ف', 'ﻔ': 'ف',
            # القاف
            'ﻕ': 'ق', 'ﻖ': 'ق', 'ﻗ': 'ق', 'ﻘ': 'ق',
            # الكاف
            'ﻙ': 'ك', 'ﻚ': 'ك', 'ﻛ': 'ك', 'ﻜ': 'ك',
            '\u06A9': 'ك',  # كاف فارسية
            '\u06AA': 'ك',  # كاف سواحيلية
            # اللام
            'ﻝ': 'ل', 'ﻞ': 'ل', 'ﻟ': 'ل', 'ﻠ': 'ل',
            # الميم
            'ﻡ': 'م', 'ﻢ': 'م', 'ﻣ': 'م', 'ﻤ': 'م',
            # النون
            'ﻥ': 'ن', 'ﻦ': 'ن', 'ﻧ': 'ن', 'ﻨ': 'ن',
            # الهاء
            'ﻩ': 'ه', 'ﻪ': 'ه', 'ﻫ': 'ه', 'ﻬ': 'ه',
            # اللام ألف
            'ﻻ': 'لا', 'ﻼ': 'لا',
        }
    }
    
    # رموز التشكيل والعلامات العثمانية
    DIACRITIC_RANGES = [
        (0x064B, 0x0652),  # تشكيل أساسي
        (0x0653, 0x065F),  # رموز عثمانية خاصة
        (0x0670, 0x0671),  # ألف خنجرية وألف وصل
        (0x06D6, 0x06ED),  # علامات وقف وتجويد
        (0x08D3, 0x08FF),  # رموز عربية ممتدة
        (0xFBB2, 0xFBC1),  # رموز عثمانية في Presentation Forms
    ]
    
    # أنماط الأرقام
    ARABIC_NUMBERS = {
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
        # أرقام فارسية/أردية
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
    }
    
    def __init__(self, font_manager=None, logger=None):
        """
        تهيئة معالج النصوص
        
        Args:
            font_manager: مدير الخط العثماني
            logger: كائن التسجيل
        """
        self.font_manager = font_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # بناء أنماط التطبيع
        self._build_normalization_patterns()
        
    def _build_normalization_patterns(self):
        """بناء أنماط التطبيع المجمعة"""
        # دمج جميع قواعد التطبيع
        self.all_normalizations = {}
        for category, rules in self.NORMALIZATION_RULES.items():
            self.all_normalizations.update(rules)
            
        # بناء نمط regex للتشكيل
        diacritic_chars = []
        for start, end in self.DIACRITIC_RANGES:
            diacritic_chars.extend([chr(i) for i in range(start, end + 1)])
        
        self.diacritic_pattern = re.compile(f'[{"".join(diacritic_chars)}]')
        
        # نمط الأرقام العربية
        arabic_nums = ''.join(self.ARABIC_NUMBERS.keys())
        self.arabic_number_pattern = re.compile(f'[{arabic_nums}]+')
        
    @lru_cache(maxsize=10000)
    def normalize_text(self, text: str, level: str = 'full') -> str:
        """
        تطبيع النص بمستويات مختلفة
        
        Args:
            text: النص المدخل
            level: مستوى التطبيع ('minimal', 'basic', 'full', 'aggressive')
            
        Returns:
            النص المطبع
        """
        if not text:
            return ""
            
        # المستوى الأدنى - فقط Unicode
        text = unicodedata.normalize('NFKC', text)
        
        if level == 'minimal':
            return text
            
        # المستوى الأساسي - تطبيع الحروف
        if level in ['basic', 'full', 'aggressive']:
            for old, new in self.all_normalizations.items():
                text = text.replace(old, new)
                
        # المستوى الكامل - إزالة التشكيل
        if level in ['full', 'aggressive']:
            text = self.diacritic_pattern.sub('', text)
            
        # المستوى الشامل - تنظيف كامل
        if level == 'aggressive':
            # إزالة جميع الرموز غير الحروف
            text = re.sub(r'[^\u0621-\u064A\u0671-\u06D3\s]', ' ', text)
            # تنظيف المسافات
            text = re.sub(r'\s+', ' ', text)
            
        return text.strip()
        
    def clean_text(self, text: str, keep_verse_numbers: bool = False) -> str:
        """
        تنظيف النص من الرموز والأرقام
        
        Args:
            text: النص المدخل
            keep_verse_numbers: الاحتفاظ بأرقام الآيات
            
        Returns:
            النص النظيف
        """
        if not text:
            return ""
            
        # تطبيع أولي
        text = self.normalize_text(text, level='basic')
        
        # إزالة التشكيل
        text = self.diacritic_pattern.sub('', text)
        
        # معالجة الأرقام
        if not keep_verse_numbers:
            # إزالة جميع الأرقام
            text = re.sub(r'[\d٠-٩۰-۹]+', ' ', text)
        else:
            # تحويل الأرقام العربية إلى إنجليزية
            for ar, en in self.ARABIC_NUMBERS.items():
                text = text.replace(ar, en)
                
        # إزالة الرموز الخاصة
        text = re.sub(r'[﴾﴿۝۞\[\](){}«»"]', ' ', text)
        
        # تنظيف المسافات
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
        
    def extract_verse_numbers(self, text: str) -> List[Dict[str, Any]]:
        """استخراج أرقام الآيات من النص"""
        verse_numbers = []
        
        # البحث عن أرقام عربية
        for match in self.arabic_number_pattern.finditer(text):
            arabic_num = match.group()
            english_num = ''.join(self.ARABIC_NUMBERS.get(c, c) for c in arabic_num)
            
            try:
                verse_numbers.append({
                    'arabic': arabic_num,
                    'english': english_num,
                    'value': int(english_num),
                    'position': match.start(),
                    'context': text[max(0, match.start()-10):match.end()+10]
                })
            except ValueError:
                continue
                
        # البحث عن أرقام إنجليزية
        for match in re.finditer(r'\d+', text):
            num = match.group()
            if not any(v['english'] == num for v in verse_numbers):
                try:
                    verse_numbers.append({
                        'arabic': num,
                        'english': num,
                        'value': int(num),
                        'position': match.start(),
                        'context': text[max(0, match.start()-10):match.end()+10]
                    })
                except ValueError:
                    continue
                    
        return sorted(verse_numbers, key=lambda x: x['position'])
        
    def analyze_text(self, text: str) -> TextAnalysis:
        """تحليل شامل للنص"""
        # التطبيع بمستويات مختلفة
        normalized = self.normalize_text(text, level='basic')
        clean = self.clean_text(text)
        
        # عد الأحرف
        char_count = Counter(text)
        
        # عد الكلمات والأسطر
        words = clean.split()
        word_count = len(words)
        line_count = text.count('\n') + 1
        
        # تحليل الرموز
        symbols_analysis = self._analyze_symbols(text)
        
        # استخراج أرقام الآيات
        verse_numbers = self.extract_verse_numbers(text)
        
        # استخراج العلامات الخاصة
        special_marks = self._extract_special_marks(text)
        
        # حساب ثقة اللغة
        language_confidence = self._calculate_language_confidence(text)
        
        return TextAnalysis(
            original_text=text,
            normalized_text=normalized,
            clean_text=clean,
            character_count=dict(char_count),
            word_count=word_count,
            line_count=line_count,
            symbols_analysis=symbols_analysis,
            verse_numbers=verse_numbers,
            special_marks=special_marks,
            language_confidence=language_confidence
        )
        
    def _analyze_symbols(self, text: str) -> Dict[str, Any]:
        """تحليل الرموز في النص"""
        symbols = {
            'diacritics': [],
            'waqf_marks': [],
            'special_symbols': [],
            'punctuation': [],
            'numbers': []
        }
        
        for i, char in enumerate(text):
            unicode_val = ord(char)
            
            # تشكيل
            if any(start <= unicode_val <= end for start, end in self.DIACRITIC_RANGES[:2]):
                symbols['diacritics'].append({
                    'char': char,
                    'position': i,
                    'unicode': f'U+{unicode_val:04X}',
                    'name': unicodedata.name(char, 'UNNAMED')
                })
                
            # علامات وقف
            elif 0x06D6 <= unicode_val <= 0x06DC:
                symbols['waqf_marks'].append({
                    'char': char,
                    'position': i,
                    'unicode': f'U+{unicode_val:04X}',
                    'name': self._get_waqf_name(char)
                })
                
            # رموز خاصة
            elif unicode_val in [0x06DD, 0x06DE, 0x06E9]:
                symbols['special_symbols'].append({
                    'char': char,
                    'position': i,
                    'unicode': f'U+{unicode_val:04X}',
                    'name': self._get_special_symbol_name(char)
                })
                
        return symbols
        
    def _extract_special_marks(self, text: str) -> List[Dict[str, Any]]:
        """استخراج العلامات الخاصة من النص"""
        marks = []
        
        # علامات نهاية الآية
        for match in re.finditer(r'[﴾﴿](\d+|[٠-٩]+)[﴾﴿]', text):
            marks.append({
                'type': 'verse_end',
                'text': match.group(),
                'position': match.start(),
                'verse_number': self.extract_verse_numbers(match.group())[0] if self.extract_verse_numbers(match.group()) else None
            })
            
        # علامات السجدة
        for match in re.finditer(r'۩', text):
            marks.append({
                'type': 'sajda',
                'text': match.group(),
                'position': match.start()
            })
            
        return marks
        
    def _calculate_language_confidence(self, text: str) -> float:
        """حساب ثقة كون النص عربي"""
        if not text:
            return 0.0
            
        arabic_chars = sum(1 for c in text if 0x0600 <= ord(c) <= 0x06FF)
        total_chars = len(text.replace(' ', ''))
        
        return arabic_chars / total_chars if total_chars > 0 else 0.0
        
    def _get_waqf_name(self, char: str) -> str:
        """الحصول على اسم علامة الوقف"""
        waqf_names = {
            '\u06D6': 'صلى',
            '\u06D7': 'قلى', 
            '\u06D8': 'ميم صغيرة',
            '\u06D9': 'لا',
            '\u06DA': 'جيم',
            '\u06DB': 'ثلاث نقاط',
            '\u06DC': 'صاد لام ياء'
        }
        return waqf_names.get(char, 'علامة وقف')
        
    def _get_special_symbol_name(self, char: str) -> str:
        """الحصول على اسم الرمز الخاص"""
        symbol_names = {
            '\u06DD': 'نهاية آية',
            '\u06DE': 'رأس حزب',
            '\u06E9': 'سجدة'
        }
        return symbol_names.get(char, 'رمز خاص')
        
    def text_similarity(self, text1: str, text2: str, method: str = 'combined') -> float:
        """
        حساب التشابه بين نصين
        
        Args:
            text1: النص الأول
            text2: النص الثاني
            method: طريقة الحساب ('simple', 'levenshtein', 'advanced', 'combined')
            
        Returns:
            درجة التشابه (0.0 - 1.0)
        """
        if not text1 or not text2:
            return 0.0
            
        # تنظيف النصوص
        clean1 = self.clean_text(text1)
        clean2 = self.clean_text(text2)
        
        if method == 'simple':
            return self._simple_similarity(clean1, clean2)
        elif method == 'levenshtein':
            return self._levenshtein_similarity(clean1, clean2)
        elif method == 'advanced':
            return self._advanced_similarity(text1, text2, clean1, clean2)
        elif method == 'combined':
            return self._combined_similarity(text1, text2, clean1, clean2)
        else:
            return self._simple_similarity(clean1, clean2)
            
    def _simple_similarity(self, text1: str, text2: str) -> float:
        """تشابه بسيط باستخدام SequenceMatcher"""
        return SequenceMatcher(None, text1, text2).ratio()
        
    def _levenshtein_similarity(self, text1: str, text2: str) -> float:
        """تشابه باستخدام مسافة Levenshtein"""
        distance = Levenshtein.distance(text1, text2)
        max_len = max(len(text1), len(text2))
        return 1.0 - (distance / max_len) if max_len > 0 else 0.0
        
    def _advanced_similarity(self, orig1: str, orig2: str, clean1: str, clean2: str) -> float:
        """تشابه متقدم مع مراعاة خصائص النص"""
        # تشابه الكلمات
        words1 = set(clean1.split())
        words2 = set(clean2.split())
        
        word_similarity = 0.0
        if words1 and words2:
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            word_similarity = intersection / union if union > 0 else 0.0
            
        # تشابه الأحرف
        chars1 = set(clean1.replace(' ', ''))
        chars2 = set(clean2.replace(' ', ''))
        
        char_similarity = 0.0
        if chars1 and chars2:
            intersection = len(chars1.intersection(chars2))
            union = len(chars1.union(chars2))
            char_similarity = intersection / union if union > 0 else 0.0
            
        # تشابه الطول
        len1, len2 = len(clean1), len(clean2)
        length_similarity = min(len1, len2) / max(len1, len2) if max(len1, len2) > 0 else 0.0
        
        # مكافأة للرموز العثمانية المتطابقة
        symbols_bonus = self._calculate_symbols_bonus(orig1, orig2)
        
        # حساب المتوسط المرجح
        return (
            word_similarity * 0.4 +
            char_similarity * 0.3 +
            length_similarity * 0.2 +
            symbols_bonus * 0.1
        )
        
    def _combined_similarity(self, orig1: str, orig2: str, clean1: str, clean2: str) -> float:
        """تشابه مدمج يستخدم جميع الطرق"""
        simple = self._simple_similarity(clean1, clean2)
        levenshtein = self._levenshtein_similarity(clean1, clean2)
        advanced = self._advanced_similarity(orig1, orig2, clean1, clean2)
        
        # مكافأة إضافية لتطابق أرقام الآيات
        verse_bonus = self._calculate_verse_number_bonus(orig1, orig2)
        
        # وزن مختلف لكل طريقة
        combined = (
            simple * 0.3 +
            levenshtein * 0.3 +
            advanced * 0.3 +
            verse_bonus * 0.1
        )
        
        return min(combined, 1.0)
        
    def _calculate_symbols_bonus(self, text1: str, text2: str) -> float:
        """حساب مكافأة تطابق الرموز العثمانية"""
        if not self.font_manager:
            return 0.0
            
        symbols1 = set()
        symbols2 = set()
        
        for char in text1:
            if self.font_manager.is_uthmani_symbol(char):
                symbols1.add(char)
                
        for char in text2:
            if self.font_manager.is_uthmani_symbol(char):
                symbols2.add(char)
                
        if not symbols1 and not symbols2:
            return 0.0
            
        if symbols1 and symbols2:
            intersection = len(symbols1.intersection(symbols2))
            union = len(symbols1.union(symbols2))
            return intersection / union if union > 0 else 0.0
            
        return 0.0
        
    def _calculate_verse_number_bonus(self, text1: str, text2: str) -> float:
        """حساب مكافأة تطابق أرقام الآيات"""
        verses1 = self.extract_verse_numbers(text1)
        verses2 = self.extract_verse_numbers(text2)
        
        if not verses1 or not verses2:
            return 0.0
            
        # مقارنة أرقام الآيات
        values1 = {v['value'] for v in verses1}
        values2 = {v['value'] for v in verses2}
        
        if values1 == values2:
            return 1.0
        elif values1.intersection(values2):
            return 0.5
        else:
            return 0.0
            
    def find_best_match(self, target: str, candidates: List[str], 
                       min_similarity: float = 0.3) -> Tuple[Optional[str], float]:
        """
        إيجاد أفضل مطابقة من قائمة المرشحين
        
        Args:
            target: النص المستهدف
            candidates: قائمة النصوص المرشحة
            min_similarity: الحد الأدنى للتشابه
            
        Returns:
            (أفضل مطابقة، درجة التشابه)
        """
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            score = self.text_similarity(target, candidate, method='combined')
            
            if score > best_score and score >= min_similarity:
                best_score = score
                best_match = candidate
                
        return best_match, best_score
        
    def split_into_words(self, text: str, preserve_marks: bool = True) -> List[str]:
        """
        تقسيم النص إلى كلمات مع خيار الحفاظ على العلامات
        
        Args:
            text: النص المدخل
            preserve_marks: الحفاظ على علامات التشكيل
            
        Returns:
            قائمة الكلمات
        """
        if preserve_marks:
            # تقسيم مع الحفاظ على التشكيل
            words = re.split(r'[\s\u200C\u200D]+', text)
        else:
            # تقسيم بعد إزالة التشكيل
            clean = self.clean_text(text)
            words = clean.split()
            
        return [w for w in words if w]
        
    def reshape_arabic_text(self, text: str) -> str:
        """إعادة تشكيل النص العربي للعرض الصحيح"""
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except:
            return text
            
    def detect_text_direction(self, text: str) -> str:
        """كشف اتجاه النص (RTL/LTR)"""
        if not text:
            return 'ltr'
            
        # حساب نسبة الأحرف العربية
        arabic_chars = sum(1 for c in text if 0x0600 <= ord(c) <= 0x06FF)
        total_chars = len(text.replace(' ', ''))
        
        if total_chars == 0:
            return 'ltr'
            
        arabic_ratio = arabic_chars / total_chars
        
        return 'rtl' if arabic_ratio > 0.5 else 'ltr'
        
    def segment_text(self, text: str) -> List[Dict[str, Any]]:
        """تقسيم النص إلى مقاطع (آيات، جمل، إلخ)"""
        segments = []
        
        # تقسيم حسب علامات نهاية الآية
        verse_pattern = re.compile(r'[^﴾﴿]+[﴾﴿]\s*(?:\d+|[٠-٩]+)\s*[﴾﴿]')
        
        matches = list(verse_pattern.finditer(text))
        
        if matches:
            for i, match in enumerate(matches):
                verse_nums = self.extract_verse_numbers(match.group())
                
                segments.append({
                    'type': 'verse',
                    'text': match.group().strip(),
                    'start': match.start(),
                    'end': match.end(),
                    'verse_number': verse_nums[0]['value'] if verse_nums else None,
                    'index': i
                })
        else:
            # تقسيم حسب الأسطر أو الجمل
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    segments.append({
                        'type': 'line',
                        'text': line.strip(),
                        'start': text.find(line),
                        'end': text.find(line) + len(line),
                        'index': i
                    })
                    
        return segments
        
    def merge_segments(self, segments: List[str], separator: str = ' ') -> str:
        """دمج المقاطع مع معالجة التشكيل والرموز"""
        if not segments:
            return ""
            
        # تنظيف المقاطع
        cleaned = [s.strip() for s in segments if s.strip()]
        
        # دمج مع معالجة المسافات
        merged = separator.join(cleaned)
        
        # تنظيف المسافات المتعددة
        merged = re.sub(r'\s+', ' ', merged)
        
        return merged.strip()
