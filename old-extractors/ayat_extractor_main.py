#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مستخرج الآيات الرئيسي من ملفات SVG و PDF مع دعم الذكاء الاصطناعي
يستخدم مدير الخط المتطور ومعالج النصوص مع تحليل AI للحصول على أفضل دقة

المميزات:
- دعم متطور لملفات SVG مع معالجة التحويلات المعقدة
- استخراج من PDF مع دعم الطبقات المتعددة
- تحليل بالذكاء الاصطناعي باستخدام Groq API
- خوارزميات مطابقة ذكية متعددة المستويات
- معالجة متوازية للأداء العالي
- تقارير مفصلة وإحصائيات شاملة
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import xml.etree.ElementTree as ET
import fitz  # PyMuPDF
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from tqdm import tqdm
import re
from collections import defaultdict
import io

# استيراد المكونات المحلية
from gui.Agent.font_manager import AdvancedFontManager
from gui.Agent.text_processor import AdvancedTextProcessor
from gui.Agent.ai_analyzer import AIAnalyzer, PageAnalysis, TextRegion

@dataclass
class ExtractedText:
    """نص مستخرج مع معلوماته"""
    text: str
    bbox: List[float]  # [x1, y1, x2, y2]
    page: int
    source: str  # 'svg' أو 'pdf'
    line_number: Optional[int] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class MatchedAyah:
    """آية مطابقة مع معلوماتها"""
    page: int
    sura_no: int
    sura_name_ar: str
    sura_name_en: str
    aya_no: int
    text_uthmani: str
    text_extracted: str
    text_clean: str
    similarity: float
    bbox: List[float]
    source: str
    extraction_method: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
class AyatExtractor:
    """مستخرج الآيات الرئيسي مع دعم الذكاء الاصطناعي"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        تهيئة المستخرج
        
        Args:
            config: إعدادات التشغيل
        """
        self.config = config
        self.setup_logging()
        
        # تهيئة المكونات
        self.font_manager = AdvancedFontManager(
            config['font_file'],
            cache_dir=config.get('cache_dir', 'font_cache'),
            logger=self.logger
        )
        
        self.text_processor = AdvancedTextProcessor(
            font_manager=self.font_manager,
            logger=self.logger
        )
        
        # تهيئة محلل الذكاء الاصطناعي إن كان مفعلاً
        self.ai_analyzer = None
        if config.get('use_ai', False) and config.get('groq_api_key'):
            try:
                self.ai_analyzer = AIAnalyzer(
                    api_key=config['groq_api_key'],
                    cache_dir=config.get('ai_cache_dir', 'ai_cache'),
                    logger=self.logger
                )
                self.logger.info("✅ تم تفعيل محلل الذكاء الاصطناعي")
            except Exception as e:
                self.logger.warning(f"⚠️ فشل تفعيل الذكاء الاصطناعي: {e}")
                self.ai_analyzer = None
        
        # تحميل بيانات المصحف
        self.hafs_data = self._load_hafs_data()
        
        # إحصائيات
        self.stats = defaultdict(int)
        
    def setup_logging(self):
        """إعداد نظام التسجيل"""
        log_level = logging.DEBUG if self.config.get('verbose') else logging.INFO
        
        # إنشاء مجلد السجلات
        log_dir = Path(self.config.get('log_dir', 'logs'))
        log_dir.mkdir(exist_ok=True)
        
        # إعداد المسجل
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(
                    log_dir / f'ayat_extractor_{datetime.now():%Y%m%d_%H%M%S}.log',
                    encoding='utf-8'
                ),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("مستخرج الآيات المتطور - الإصدار 3.0")
        self.logger.info("=" * 60)
        
    def _load_hafs_data(self) -> pd.DataFrame:
        """تحميل بيانات المصحف"""
        csv_path = self.config['csv_path']
        
        try:
            # تحميل البيانات
            df = pd.read_csv(csv_path)
            
            # تنظيف البيانات
            df['aya_text'] = df['aya_text'].fillna('')
            df['aya_text_emlaey'] = df['aya_text_emlaey'].fillna('')
            
            self.logger.info(f"✅ تم تحميل {len(df)} آية من بيانات المصحف")
            
            # معالجة أولية للنصوص
            self.logger.info("معالجة النصوص المرجعية...")
            df['text_normalized'] = df['aya_text'].apply(
                lambda x: self.text_processor.normalize_text(x, level='basic')
            )
            df['text_clean'] = df['aya_text'].apply(
                lambda x: self.text_processor.clean_text(x)
            )
            
            return df
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحميل بيانات المصحف: {e}")
            raise
            
    def extract_from_svg_with_ai(self, svg_path: str) -> List[ExtractedText]:
        """استخراج النصوص من SVG مع دعم الذكاء الاصطناعي"""
        # الاستخراج التقليدي أولاً
        traditional_texts = self.extract_from_svg(svg_path)
        
        # إذا كان AI مفعلاً، نحسن النتائج
        if self.ai_analyzer and self.config.get('ai_enhance_svg', True):
            try:
                # تحليل الصفحة بالذكاء الاصطناعي
                page_analysis = self.ai_analyzer.analyze_page(
                    svg_path,
                    ['text_regions', 'ayah_detection']
                )
                
                # دمج نتائج AI مع النتائج التقليدية
                enhanced_texts = self._merge_ai_results(
                    traditional_texts,
                    page_analysis
                )
                
                self.stats['ai_enhanced_pages'] += 1
                return enhanced_texts
                
            except Exception as e:
                self.logger.warning(f"فشل تحسين AI للصفحة: {e}")
                return traditional_texts
        
        return traditional_texts
    
    def _merge_ai_results(self, traditional_texts: List[ExtractedText], 
                         ai_analysis: PageAnalysis) -> List[ExtractedText]:
        """دمج نتائج الاستخراج التقليدي مع تحليل AI"""
        merged = []
        used_ai_regions = set()
        
        # مطابقة النصوص التقليدية مع مناطق AI
        for trad_text in traditional_texts:
            best_match = None
            best_overlap = 0.0
            
            for idx, ai_region in enumerate(ai_analysis.text_regions):
                if idx in used_ai_regions:
                    continue
                    
                # حساب التداخل بين المناطق
                overlap = self._calculate_bbox_overlap(
                    trad_text.bbox,
                    ai_region.bbox
                )
                
                if overlap > best_overlap and overlap > 0.5:
                    best_overlap = overlap
                    best_match = (idx, ai_region)
            
            if best_match:
                idx, ai_region = best_match
                used_ai_regions.add(idx)
                
                # دمج المعلومات
                enhanced_text = ExtractedText(
                    text=trad_text.text,  # نثق بالنص المستخرج
                    bbox=ai_region.bbox,   # نستخدم إحداثيات AI الأدق
                    page=trad_text.page,
                    source='svg_ai_enhanced',
                    confidence=max(trad_text.confidence, ai_region.confidence),
                    metadata={
                        **trad_text.metadata,
                        'ai_text_type': ai_region.text_type,
                        'ai_font_type': ai_region.font_type,
                        'ai_confidence': ai_region.confidence
                    }
                )
                merged.append(enhanced_text)
            else:
                # لم نجد مطابقة AI، نستخدم النص التقليدي
                merged.append(trad_text)
        
        # إضافة مناطق AI التي لم تطابق أي نص تقليدي
        for idx, ai_region in enumerate(ai_analysis.text_regions):
            if idx not in used_ai_regions and ai_region.text_type == 'ayah':
                merged.append(ExtractedText(
                    text=ai_region.text or '',
                    bbox=ai_region.bbox,
                    page=ai_analysis.page_number,
                    source='ai_only',
                    confidence=ai_region.confidence,
                    metadata={
                        'ai_text_type': ai_region.text_type,
                        'ai_font_type': ai_region.font_type
                    }
                ))
        
        return merged
    
    def _calculate_bbox_overlap(self, bbox1: List[float], 
                               bbox2: List[float]) -> float:
        """حساب نسبة التداخل بين مربعين محيطين"""
        x1_min, y1_min, x1_max, y1_max = bbox1
        x2_min, y2_min, x2_max, y2_max = bbox2
        
        # حساب التقاطع
        x_overlap = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
        y_overlap = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
        
        intersection = x_overlap * y_overlap
        
        # حساب الاتحاد
        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        area2 = (x2_max - x2_min) * (y2_max - y2_min)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def remove_unwanted_elements(self, page_num: int) -> Optional[ExtractedText]:
        """إزالة العناصر غير المرغوبة من الصفحة باستخدام AI"""
        if not self.ai_analyzer:
            return None
            
        try:
            # الحصول على مسار الصورة
            svg_path = Path(self.config['svg_folder']) / f"page_{page_num:03d}.svg"
            
            if not svg_path.exists():
                return None
            
            # تحليل الصفحة
            analysis = self.ai_analyzer.analyze_page(
                str(svg_path),
                ['text_regions', 'layout']
            )
            
            # إزالة العناصر المحددة
            elements_to_remove = self.config.get('remove_elements', [
                'page_number', 'decoration', 'footnote'
            ])
            
            # إنشاء صورة نظيفة
            clean_image = self.ai_analyzer.remove_page_elements(
                str(svg_path),
                elements_to_remove
            )
            
            # حفظ الصورة النظيفة
            clean_path = Path(self.config.get('clean_pages_dir', 'clean_pages'))
            clean_path.mkdir(exist_ok=True)
            
            output_file = clean_path / f"page_{page_num:03d}_clean.png"
            clean_image.save(output_file)
            
            self.logger.info(f"✅ تم تنظيف الصفحة {page_num}")
            self.stats['cleaned_pages'] += 1
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"خطأ في تنظيف الصفحة {page_num}: {e}")
            return None

    def extract_from_svg(self, svg_path: str) -> List[ExtractedText]:
        """استخراج النصوص من ملف SVG"""
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            texts = []
            # البحث عن جميع عناصر النص
            for elem in root.iter():
                # معالجة عناصر use مع data-text
                if elem.tag.endswith('use') and 'data-text' in elem.attrib:
                    text_content = elem.get('data-text', '')
                    transform = elem.get('transform', '')
                    if text_content.strip():
                        coords = self._extract_svg_coordinates(transform, elem)
                        if coords:
                            text_content = self._decode_html_entities(text_content)
                            texts.append(ExtractedText(
                                text=text_content,
                                bbox=coords,
                                page=self._get_page_from_filename(svg_path),
                                source='svg',
                                metadata={
                                    'transform': transform,
                                    'element_id': elem.get('id', ''),
                                    'href': elem.get('{http://www.w3.org/1999/xlink}href', '')
                                }
                            ))
                # معالجة عناصر text
                elif elem.tag.endswith('text'):
                    text_content = self._extract_text_element_content(elem)
                    if text_content.strip():
                        x = float(elem.get('x', 0))
                        y = float(elem.get('y', 0))
                        bbox = self._estimate_text_bbox(text_content, x, y)
                        texts.append(ExtractedText(
                            text=text_content,
                            bbox=bbox,
                            page=self._get_page_from_filename(svg_path),
                            source='svg',
                            metadata={
                                'element_type': 'text',
                                'font_size': elem.get('font-size', ''),
                                'font_family': elem.get('font-family', '')
                            }
                        ))
            processed_texts = self._process_svg_texts(texts)
            self.logger.info(f"📄 SVG: استخرج {len(processed_texts)} نص من {svg_path}")
            return processed_texts
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة SVG {svg_path}: {e}")
            return []
            
    def _extract_svg_coordinates(self, transform: str, elem: ET.Element) -> Optional[List[float]]:
        """استخراج الإحداثيات من SVG transform"""
        try:
            # معالجة matrix transform
            matrix_match = re.search(
                r'matrix\(([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^)]+)\)',
                transform
            )
            
            if matrix_match:
                # استخراج قيم المصفوفة
                a, b, c, d, e, f = map(float, matrix_match.groups())
                x, y = e, f
            else:
                # معالجة translate
                translate_match = re.search(
                    r'translate\(([^,]+)(?:,([^)]+))?\)',
                    transform
                )
                
                if translate_match:
                    x = float(translate_match.group(1))
                    y = float(translate_match.group(2) or 0)
                else:
                    # محاولة الحصول على x,y من الخصائص
                    x = float(elem.get('x', 0))
                    y = float(elem.get('y', 0))
                    
            # تقدير الحدود
            width = 100  # تقدير افتراضي
            height = 20  # تقدير افتراضي
            
            return [x, y - height, x + width, y]
            
        except Exception as e:
            self.logger.debug(f"فشل استخراج الإحداثيات: {e}")
            return None
            
    def _decode_html_entities(self, text: str) -> str:
        """فك تشفير HTML entities"""
        # معالجة &#x...;
        text = re.sub(
            r'&#x([0-9a-fA-F]+);',
            lambda m: chr(int(m.group(1), 16)),
            text
        )
        
        # معالجة &#...;
        text = re.sub(
            r'&#([0-9]+);',
            lambda m: chr(int(m.group(1))),
            text
        )
        
        return text
        
    def _extract_text_element_content(self, elem: ET.Element) -> str:
        """استخراج محتوى عنصر text مع معالجة tspan"""
        text_parts = []
        
        # النص المباشر
        if elem.text:
            text_parts.append(elem.text)
            
        # معالجة tspan
        for tspan in elem.findall('.//{http://www.w3.org/2000/svg}tspan'):
            if tspan.text:
                text_parts.append(tspan.text)
                
        # النص بعد العناصر
        if elem.tail:
            text_parts.append(elem.tail)
            
        return ''.join(text_parts)
        
    def _estimate_text_bbox(self, text: str, x: float, y: float) -> List[float]:
        """تقدير حدود النص"""
        # استخدام معلومات الخط إن أمكن
        if self.font_manager:
            rendering_info = self.font_manager.get_rendering_info(text)
            estimated_width = rendering_info['estimated_width'] * 0.1  # تحويل من وحدات الخط
        else:
            # تقدير بسيط
            estimated_width = len(text) * 10
            
        estimated_height = 20
        
        return [x, y - estimated_height, x + estimated_width, y]
        
    def _get_page_from_filename(self, filename: str) -> int:
        """استخراج رقم الصفحة من اسم الملف"""
        match = re.search(r'page[_-]?(\d+)', filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
            
        match = re.search(r'(\d+)', filename)
        if match:
            return int(match.group(1))
            
        return 1
        
    def _process_svg_texts(self, texts: List[ExtractedText]) -> List[ExtractedText]:
        """معالجة وتجميع النصوص من SVG"""
        if not texts:
            return []
            
        # ترتيب حسب الموضع
        texts.sort(key=lambda t: (-t.bbox[1], t.bbox[0]))
        
        # تجميع النصوص في أسطر
        lines = []
        current_line = []
        current_y = None
        line_threshold = self.config.get('line_threshold', 10)
        
        for text in texts:
            y_center = (text.bbox[1] + text.bbox[3]) / 2
            
            if current_y is None:
                current_y = y_center
                current_line = [text]
            elif abs(y_center - current_y) <= line_threshold:
                # نفس السطر
                current_line.append(text)
            else:
                # سطر جديد
                if current_line:
                    lines.append(self._merge_line_texts(current_line))
                current_line = [text]
                current_y = y_center
                
        # إضافة السطر الأخير
        if current_line:
            lines.append(self._merge_line_texts(current_line))
            
        return lines
        
    def _merge_line_texts(self, line_texts: List[ExtractedText]) -> ExtractedText:
        """دمج نصوص السطر الواحد"""
        # ترتيب من اليمين لليسار (للعربية)
        line_texts.sort(key=lambda t: -t.bbox[0])
        
        # دمج النصوص
        merged_text = ''.join(t.text for t in line_texts)
        
        # حساب الحدود الكلية
        min_x = min(t.bbox[0] for t in line_texts)
        min_y = min(t.bbox[1] for t in line_texts)
        max_x = max(t.bbox[2] for t in line_texts)
        max_y = max(t.bbox[3] for t in line_texts)
        
        return ExtractedText(
            text=merged_text,
            bbox=[min_x, min_y, max_x, max_y],
            page=line_texts[0].page,
            source='svg',
            confidence=min(t.confidence for t in line_texts),
            metadata={
                'merged_from': len(line_texts),
                'original_texts': [t.text for t in line_texts]
            }
        )
        
    def extract_from_pdf(self, pdf_path: str, page_num: int) -> List[ExtractedText]:
        """استخراج النصوص من صفحة PDF"""
        try:
            doc = fitz.open(pdf_path)
            
            if page_num < 0 or page_num >= doc.page_count:
                self.logger.error(f"رقم الصفحة {page_num} خارج النطاق")
                return []
                
            page = doc[page_num]
            texts = []
            
            # استخراج النصوص مع الإحداثيات
            text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_LIGATURES)
            
            for block in text_dict["blocks"]:
                if block["type"] == 0:  # نص
                    for line in block["lines"]:
                        line_text = ""
                        line_bbox = None
                        
                        for span in line["spans"]:
                            span_text = span["text"]
                            
                            # معالجة النص
                            if span_text.strip():
                                line_text += span_text
                                
                                # تحديث الحدود
                                span_bbox = span["bbox"]
                                if line_bbox is None:
                                    line_bbox = list(span_bbox)
                                else:
                                    line_bbox[0] = min(line_bbox[0], span_bbox[0])
                                    line_bbox[1] = min(line_bbox[1], span_bbox[1])
                                    line_bbox[2] = max(line_bbox[2], span_bbox[2])
                                    line_bbox[3] = max(line_bbox[3], span_bbox[3])
                                    
                        if line_text.strip() and line_bbox:
                            texts.append(ExtractedText(
                                text=line_text.strip(),
                                bbox=line_bbox,
                                page=page_num + 1,
                                source='pdf',
                                line_number=line["line_no"],
                                metadata={
                                    'font': span.get("font", ""),
                                    'size': span.get("size", 0),
                                    'flags': span.get("flags", 0),
                                    'color': span.get("color", 0)
                                }
                            ))
                            
            doc.close()
            
            self.logger.info(f"📄 PDF: استخرج {len(texts)} نص من الصفحة {page_num + 1}")
            return texts
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة PDF: {e}")
            return []
            
    def match_ayat_with_texts(self, ayat_df: pd.DataFrame, extracted_texts: List[ExtractedText],
                             page_num: int) -> List[MatchedAyah]:
        """مطابقة الآيات مع النصوص المستخرجة"""
        # فلترة آيات الصفحة
        page_ayat = ayat_df[ayat_df['page'] == page_num].copy()
        
        if page_ayat.empty:
            self.logger.warning(f"لا توجد آيات في الصفحة {page_num}")
            return []
            
        matches = []
        used_texts = set()
        
        # معالجة كل آية
        for idx, aya_row in page_ayat.iterrows():
            # إعداد النص المرجعي
            ref_text = aya_row['aya_text']
            ref_clean = aya_row['text_clean']
            aya_number = int(aya_row['aya_no'])
            
            # البحث عن أفضل مطابقة
            best_match = None
            best_score = 0.0
            best_text_idx = -1
            
            for text_idx, extracted in enumerate(extracted_texts):
                if text_idx in used_texts:
                    continue
                    
                # حساب التشابه
                score = self._calculate_match_score(
                    ref_text, ref_clean, extracted.text, aya_number
                )
                
                if score > best_score and score >= self.config['min_similarity']:
                    best_score = score
                    best_match = extracted
                    best_text_idx = text_idx
                    
            # إنشاء المطابقة
            if best_match:
                used_texts.add(best_text_idx)
                
                match = MatchedAyah(
                    page=page_num,
                    sura_no=int(aya_row['sura_no']),
                    sura_name_ar=aya_row['sura_name_ar'],
                    sura_name_en=aya_row['sura_name_en'],
                    aya_no=aya_number,
                    text_uthmani=ref_text,
                    text_extracted=best_match.text,
                    text_clean=self.text_processor.clean_text(best_match.text),
                    similarity=best_score,
                    bbox=best_match.bbox,
                    source=best_match.source,
                    extraction_method=self._determine_extraction_method(best_match),
                    confidence=best_match.confidence * best_score,
                    metadata={
                        'line_number': best_match.line_number,
                        'text_analysis': self.text_processor.analyze_text(best_match.text).__dict__,
                        'match_details': self._get_match_details(ref_text, best_match.text)
                    }
                )
                
                matches.append(match)
                self.stats['matched'] += 1
                
                self.logger.debug(
                    f"✓ مطابقة {aya_row['sura_no']}:{aya_number} "
                    f"(تشابه: {best_score:.3f}, مصدر: {best_match.source})"
                )
            else:
                self.stats['unmatched'] += 1
                self.logger.warning(
                    f"✗ لم يتم مطابقة {aya_row['sura_no']}:{aya_number}"
                )
                
        return matches
        
    def _calculate_match_score(self, ref_text: str, ref_clean: str, 
                              extracted_text: str, aya_number: int) -> float:
        """حساب درجة المطابقة المتقدمة"""
        # التشابه الأساسي
        basic_score = self.text_processor.text_similarity(
            ref_text, extracted_text, method='combined'
        )
        
        # مكافأة رقم الآية
        verse_bonus = 0.0
        extracted_verses = self.text_processor.extract_verse_numbers(extracted_text)
        
        if extracted_verses:
            for verse in extracted_verses:
                if verse['value'] == aya_number:
                    verse_bonus = 0.15
                    break
                    
        # مكافأة الرموز العثمانية
        symbols_bonus = 0.0
        if self.font_manager:
            ref_symbols = set()
            ext_symbols = set()
            
            for char in ref_text:
                if self.font_manager.is_uthmani_symbol(char):
                    ref_symbols.add(char)
                    
            for char in extracted_text:
                if self.font_manager.is_uthmani_symbol(char):
                    ext_symbols.add(char)
                    
            if ref_symbols and ext_symbols:
                common = len(ref_symbols.intersection(ext_symbols))
                total = len(ref_symbols.union(ext_symbols))
                symbols_bonus = (common / total) * 0.1 if total > 0 else 0.0
                
        # الدرجة النهائية
        final_score = min(basic_score + verse_bonus + symbols_bonus, 1.0)
        
        return final_score
        
    def _determine_extraction_method(self, extracted: ExtractedText) -> str:
        """تحديد طريقة الاستخراج"""
        if extracted.source == 'svg':
            if extracted.metadata.get('merged_from', 0) > 1:
                return 'svg_merged'
            else:
                return 'svg_direct'
        else:
            return 'pdf_text'
            
    def _get_match_details(self, ref_text: str, extracted_text: str) -> Dict[str, Any]:
        """الحصول على تفاصيل المطابقة"""
        return {
            'ref_length': len(ref_text),
            'extracted_length': len(extracted_text),
            'length_ratio': len(extracted_text) / len(ref_text) if len(ref_text) > 0 else 0,
            'ref_words': len(ref_text.split()),
            'extracted_words': len(extracted_text.split()),
            'has_verse_number': bool(self.text_processor.extract_verse_numbers(extracted_text)),
            'ref_symbols': len([c for c in ref_text if self.font_manager and self.font_manager.is_uthmani_symbol(c)]),
            'extracted_symbols': len([c for c in extracted_text if self.font_manager and self.font_manager.is_uthmani_symbol(c)])
        }
        
    def process_page(self, page_num: int) -> List[MatchedAyah]:
        """معالجة صفحة واحدة مع دعم الذكاء الاصطناعي"""
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"معالجة الصفحة {page_num}")
        self.logger.info(f"{'='*50}")
        
        # تنظيف الصفحة بـ AI إن كان مطلوباً
        if self.ai_analyzer and self.config.get('ai_clean_pages', False):
            clean_result = self.remove_unwanted_elements(page_num)
            if clean_result:
                self.logger.info(f"تم تنظيف الصفحة بنجاح")
        
        extracted_texts = []
        
        # محاولة SVG أولاً مع تحسين AI
        if self.config.get('prefer_svg', True) and self.config.get('svg_folder'):
            svg_path = Path(self.config['svg_folder']) / f"page_{page_num:03d}.svg"
            
            if svg_path.exists():
                if self.ai_analyzer and self.config.get('use_ai_for_svg', True):
                    svg_texts = self.extract_from_svg_with_ai(str(svg_path))
                else:
                    svg_texts = self.extract_from_svg(str(svg_path))
                    
                extracted_texts.extend(svg_texts)
                self.stats['svg_pages'] += 1
                
        # إذا لم نحصل على نصوص كافية، نجرب PDF
        if len(extracted_texts) < 5 and self.config.get('pdf_path'):
            pdf_texts = self.extract_from_pdf(
                self.config['pdf_path'], 
                page_num - 1  # PDF zero-indexed
            )
            extracted_texts.extend(pdf_texts)
            self.stats['pdf_pages'] += 1
            
        # تحليل AI إضافي إذا لم نحصل على نتائج جيدة
        if self.ai_analyzer and len(extracted_texts) < 3:
            self.logger.info("نتائج قليلة، محاولة تحليل AI مباشر...")
            
            try:
                # تحليل مباشر للصفحة
                page_path = None
                if self.config.get('svg_folder'):
                    svg_path = Path(self.config['svg_folder']) / f"page_{page_num:03d}.svg"
                    if svg_path.exists():
                        page_path = str(svg_path)
                        
                if page_path:
                    ai_analysis = self.ai_analyzer.analyze_page(
                        page_path,
                        ['text_regions', 'ayah_detection']
                    )
                    
                    # تحويل مناطق AI إلى ExtractedText
                    for region in ai_analysis.text_regions:
                        if region.text_type == 'ayah':
                            extracted_texts.append(ExtractedText(
                                text=region.text or '',
                                bbox=region.bbox,
                                page=page_num,
                                source='ai_direct',
                                confidence=region.confidence,
                                metadata={
                                    'ai_font_type': region.font_type
                                }
                            ))
                            
                    self.stats['ai_direct_pages'] += 1
                    
            except Exception as e:
                self.logger.error(f"خطأ في التحليل المباشر بـ AI: {e}")
            
        if not extracted_texts:
            self.logger.warning(f"لم يتم استخراج أي نصوص من الصفحة {page_num}")
            return []
            
        # مطابقة الآيات
        matches = self.match_ayat_with_texts(
            self.hafs_data, extracted_texts, page_num
        )
        
        self.stats['total_pages'] += 1
        self.logger.info(
            f"الصفحة {page_num}: {len(matches)} آية مطابقة من "
            f"{len(extracted_texts)} نص مستخرج"
        )
        
        return matches
        
    def process_pages(self, start_page: int, end_page: int, 
                     parallel: bool = True) -> List[MatchedAyah]:
        """معالجة نطاق من الصفحات"""
        all_matches = []
        pages = list(range(start_page, end_page + 1))
        
        if parallel and len(pages) > 1:
            # معالجة متوازية
            max_workers = min(self.config.get('max_workers', 4), len(pages))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # إرسال المهام
                futures = {
                    executor.submit(self.process_page, page): page 
                    for page in pages
                }
                
                # جمع النتائج مع شريط التقدم
                with tqdm(total=len(pages), desc="معالجة الصفحات") as pbar:
                    for future in as_completed(futures):
                        page = futures[future]
                        try:
                            matches = future.result()
                            all_matches.extend(matches)
                        except Exception as e:
                            self.logger.error(f"خطأ في معالجة الصفحة {page}: {e}")
                        finally:
                            pbar.update(1)
        else:
            # معالجة تسلسلية
            for page in tqdm(pages, desc="معالجة الصفحات"):
                try:
                    matches = self.process_page(page)
                    all_matches.extend(matches)
                except Exception as e:
                    self.logger.error(f"خطأ في معالجة الصفحة {page}: {e}")
                    
        return all_matches
        
    def save_results(self, matches: List[MatchedAyah], output_file: str):
        """حفظ النتائج في ملف JSON"""
        # تحويل إلى قاموس
        results = []
        for match in matches:
            result = {
                'page': match.page,
                'sura_no': match.sura_no,
                'sura_name_ar': match.sura_name_ar,
                'sura_name_en': match.sura_name_en,
                'aya_no': match.aya_no,
                'text_uthmani': match.text_uthmani,
                'text_extracted': match.text_extracted,
                'text_clean': match.text_clean,
                'similarity': round(match.similarity, 4),
                'bbox': match.bbox,
                'source': match.source,
                'extraction_method': match.extraction_method,
                'confidence': round(match.confidence, 4),
                'metadata': match.metadata
            }
            results.append(result)
            
        # إضافة معلومات عامة
        output_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_ayat': len(results),
                'pages_processed': self.stats['total_pages'],
                'config': self.config,
                'statistics': dict(self.stats),
                'script_version': '3.0'
            },
            'results': results
        }
        
        # حفظ الملف
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"✅ تم حفظ النتائج في: {output_path}")
        
    def generate_report(self, matches: List[MatchedAyah]) -> Dict[str, Any]:
        """توليد تقرير مفصل"""
        if not matches:
            return {'error': 'لا توجد نتائج'}
            
        # إحصائيات عامة
        total = len(matches)
        similarities = [m.similarity for m in matches]
        confidences = [m.confidence for m in matches]
        
        # تصنيف حسب الجودة
        excellent = sum(1 for s in similarities if s >= 0.8)
        good = sum(1 for s in similarities if 0.6 <= s < 0.8)
        fair = sum(1 for s in similarities if 0.4 <= s < 0.6)
        poor = sum(1 for s in similarities if s < 0.4)
        
        # تصنيف حسب المصدر
        by_source = defaultdict(int)
        by_method = defaultdict(int)
        
        for match in matches:
            by_source[match.source] += 1
            by_method[match.extraction_method] += 1
            
        # صفحات بها مشاكل
        pages_with_issues = []
        page_stats = defaultdict(lambda: {'total': 0, 'poor': 0})
        
        for match in matches:
            page_stats[match.page]['total'] += 1
            if match.similarity < 0.4:
                page_stats[match.page]['poor'] += 1
                
        for page, stats in page_stats.items():
            if stats['poor'] / stats['total'] > 0.2:
                pages_with_issues.append({
                    'page': page,
                    'total': stats['total'],
                    'poor': stats['poor'],
                    'ratio': stats['poor'] / stats['total']
                })
                
        report = {
            'summary': {
                'total_ayat': total,
                'pages_processed': self.stats['total_pages'],
                'avg_similarity': np.mean(similarities),
                'std_similarity': np.std(similarities),
                'min_similarity': np.min(similarities),
                'max_similarity': np.max(similarities),
                'avg_confidence': np.mean(confidences),
            },
            'quality_distribution': {
                'excellent': {'count': excellent, 'percentage': excellent/total*100},
                'good': {'count': good, 'percentage': good/total*100},
                'fair': {'count': fair, 'percentage': fair/total*100},
                'poor': {'count': poor, 'percentage': poor/total*100}
            },
            'by_source': dict(by_source),
            'by_method': dict(by_method),
            'pages_with_issues': sorted(pages_with_issues, key=lambda x: x['ratio'], reverse=True),
            'recommendations': self._generate_recommendations(matches, similarities)
        }
        
        return report
        
    def _generate_recommendations(self, matches: List[MatchedAyah], 
                                 similarities: List[float]) -> List[str]:
        """توليد التوصيات"""
        recommendations = []
        
        avg_sim = np.mean(similarities)
        poor_ratio = sum(1 for s in similarities if s < 0.4) / len(similarities)
        
        if avg_sim < 0.6:
            recommendations.append("متوسط التشابه منخفض، يُنصح بمراجعة إعدادات المعالجة")
            
        if poor_ratio > 0.2:
            recommendations.append(f"{poor_ratio*100:.1f}% من المطابقات ضعيفة، قد تحتاج لتحسين جودة الملفات المصدر")
            
        svg_ratio = self.stats.get('svg_pages', 0) / self.stats.get('total_pages', 1)
        if svg_ratio < 0.5:
            recommendations.append("الاعتماد على PDF أكثر من SVG، استخدام SVG قد يحسن الدقة")
            
        if self.stats.get('unmatched', 0) > self.stats.get('matched', 1) * 0.1:
            recommendations.append("نسبة عالية من الآيات غير المطابقة، تحقق من جودة الاستخراج")
            
        return recommendations
        
    def print_report(self, report: Dict[str, Any]):
        """طباعة التقرير"""
        print("\n" + "="*60)
        print("تقرير الاستخراج النهائي")
        print("="*60)
        
        summary = report['summary']
        print(f"\nالملخص:")
        print(f"  إجمالي الآيات: {summary['total_ayat']}")
        print(f"  الصفحات المعالجة: {summary['pages_processed']}")
        print(f"  متوسط التشابه: {summary['avg_similarity']:.3f} ± {summary['std_similarity']:.3f}")
        print(f"  نطاق التشابه: {summary['min_similarity']:.3f} - {summary['max_similarity']:.3f}")
        print(f"  متوسط الثقة: {summary['avg_confidence']:.3f}")
        
        print(f"\nتوزيع الجودة:")
        for level, data in report['quality_distribution'].items():
            print(f"  {level}: {data['count']} ({data['percentage']:.1f}%)")
            
        print(f"\nحسب المصدر:")
        for source, count in report['by_source'].items():
            print(f"  {source}: {count}")
            
        print(f"\nحسب الطريقة:")
        for method, count in report['by_method'].items():
            print(f"  {method}: {count}")
            
        if report['pages_with_issues']:
            print(f"\nصفحات بها مشاكل:")
            for page_issue in report['pages_with_issues'][:5]:
                print(f"  الصفحة {page_issue['page']}: "
                      f"{page_issue['poor']}/{page_issue['total']} "
                      f"({page_issue['ratio']*100:.1f}% ضعيف)")
                      
        if report['recommendations']:
            print(f"\nالتوصيات:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
                
def main():
    """الوظيفة الرئيسية"""
    # معالج المعاملات
    parser = argparse.ArgumentParser(
        description='مستخرج الآيات المتطور من ملفات SVG و PDF مع دعم الذكاء الاصطناعي',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--pdf-path', required=True,
                       help='مسار ملف PDF')
    parser.add_argument('--svg-folder', required=True,
                       help='مجلد ملفات SVG')
    parser.add_argument('--csv-path', required=True,
                       help='مسار ملف بيانات المصحف CSV')
    parser.add_argument('--font-file', required=True,
                       help='مسار ملف الخط TTF')
    parser.add_argument('--output', '-o', default='reports/ayat_coordinates.json',
                       help='ملف الإخراج JSON')
    parser.add_argument('--pages', nargs=2, type=int, metavar=('START', 'END'),
                       default=[1, 604], help='نطاق الصفحات')
    parser.add_argument('--min-similarity', type=float, default=0.3,
                       help='الحد الأدنى للتشابه')
    parser.add_argument('--line-threshold', type=int, default=10,
                       help='عتبة تجميع الأسطر')
    parser.add_argument('--prefer-pdf', action='store_true',
                       help='تفضيل PDF على SVG')
    parser.add_argument('--parallel', action='store_true', default=True,
                       help='معالجة متوازية')
    parser.add_argument('--max-workers', type=int, default=4,
                       help='عدد العمليات المتوازية')
    parser.add_argument('--cache-dir', default='font_cache',
                       help='مجلد التخزين المؤقت')
    parser.add_argument('--log-dir', default='logs',
                       help='مجلد السجلات')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='عرض تفاصيل أكثر')
    parser.add_argument('--report', action='store_true', default=True,
                       help='عرض التقرير النهائي')
    
    # معاملات الذكاء الاصطناعي
    ai_group = parser.add_argument_group('خيارات الذكاء الاصطناعي')
    ai_group.add_argument('--use-ai', action='store_true',
                         help='تفعيل تحليل الذكاء الاصطناعي')
    ai_group.add_argument('--groq-api-key', 
                         default=os.getenv('GROQ_API_KEY'),
                         help='مفتاح Groq API (أو من متغير البيئة GROQ_API_KEY)')
    ai_group.add_argument('--ai-model', 
                         choices=['fast', 'accurate', 'arabic', 'balanced'],
                         default='balanced',
                         help='نموذج الذكاء الاصطناعي المستخدم')
    ai_group.add_argument('--ai-clean-pages', action='store_true',
                         help='تنظيف الصفحات بالذكاء الاصطناعي')
    ai_group.add_argument('--remove-elements', nargs='+',
                         default=['page_number', 'decoration'],
                         help='العناصر المراد إزالتها')
    ai_group.add_argument('--use-ai-for-svg', action='store_true', default=True,
                         help='استخدام AI لتحسين استخراج SVG')
    ai_group.add_argument('--ai-cache-dir', default='ai_cache',
                         help='مجلد تخزين AI المؤقت')
    ai_group.add_argument('--clean-pages-dir', default='clean_pages',
                         help='مجلد الصفحات النظيفة')
    
    args = parser.parse_args()
    
    # التحقق من مفتاح API إذا كان AI مفعلاً
    if args.use_ai and not args.groq_api_key:
        print("❌ خطأ: --use-ai يتطلب توفير --groq-api-key أو تعيين GROQ_API_KEY")
        sys.exit(1)
    
    # إعداد التكوين
    config = {
        'pdf_path': args.pdf_path,
        'svg_folder': args.svg_folder,
        'csv_path': args.csv_path,
        'font_file': args.font_file,
        'min_similarity': args.min_similarity,
        'line_threshold': args.line_threshold,
        'prefer_svg': not args.prefer_pdf,
        'max_workers': args.max_workers,
        'cache_dir': args.cache_dir,
        'log_dir': args.log_dir,
        'verbose': args.verbose,
        # إعدادات AI
        'use_ai': args.use_ai,
        'groq_api_key': args.groq_api_key,
        'ai_model': args.ai_model,
        'ai_clean_pages': args.ai_clean_pages,
        'remove_elements': args.remove_elements,
        'use_ai_for_svg': args.use_ai_for_svg,
        'ai_cache_dir': args.ai_cache_dir,
        'clean_pages_dir': args.clean_pages_dir
    }
    
    # إنشاء المستخرج
    extractor = AyatExtractor(config)
    
    # عرض معلومات AI إن كانت مفعلة
    if config['use_ai']:
        print(f"\n🤖 الذكاء الاصطناعي مفعل")
        print(f"   النموذج: {config['ai_model']}")
        print(f"   تنظيف الصفحات: {'نعم' if config['ai_clean_pages'] else 'لا'}")
        print(f"   العناصر المحذوفة: {', '.join(config['remove_elements'])}")
    
    # معالجة الصفحات
    print(f"\nمعالجة الصفحات {args.pages[0]} إلى {args.pages[1]}...")
    matches = extractor.process_pages(
        args.pages[0], 
        args.pages[1],
        parallel=args.parallel
    )
    
    # حفظ النتائج
    if matches:
        extractor.save_results(matches, args.output)
        
        # عرض التقرير
        if args.report:
            report = extractor.generate_report(matches)
            
            # إضافة إحصائيات AI للتقرير
            if config['use_ai']:
                report['ai_statistics'] = {
                    'ai_enhanced_pages': extractor.stats.get('ai_enhanced_pages', 0),
                    'ai_direct_pages': extractor.stats.get('ai_direct_pages', 0),
                    'cleaned_pages': extractor.stats.get('cleaned_pages', 0)
                }
            
            extractor.print_report(report)
            
            # حفظ التقرير
            report_file = Path(args.output).with_suffix('.report.json')
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
                
        print(f"\n✅ اكتمل الاستخراج بنجاح!")
        print(f"النتائج: {args.output}")
        
        # عرض إحصائيات AI
        if config['use_ai']:
            print(f"\n📊 إحصائيات الذكاء الاصطناعي:")
            print(f"   صفحات محسنة بـ AI: {extractor.stats.get('ai_enhanced_pages', 0)}")
            print(f"   صفحات بتحليل AI مباشر: {extractor.stats.get('ai_direct_pages', 0)}")
            print(f"   صفحات منظفة: {extractor.stats.get('cleaned_pages', 0)}")
    else:
        print("\n❌ لم يتم استخراج أي نتائج")
        
if __name__ == "__main__":
    import sys
    main()
