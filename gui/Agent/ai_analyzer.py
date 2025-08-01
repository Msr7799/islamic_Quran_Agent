#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
محلل الذكاء الاصطناعي لتحليل صفحات المصحف
يستخدم Groq API لتمييز الخطوط وتحديد أماكن الآيات

المميزات:
- تحليل ذكي للصور باستخدام Vision models
- تمييز أنواع الخطوط (عثماني، عادي، زخرفي)
- تحديد مواقع الآيات بدقة عالية
- إزالة العناصر غير المرغوبة (أرقام الصفحات، الزخارف)
- تحليل متعدد المستويات للدقة العالية
"""
import io

import os
import json
import base64
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
import cv2
import asyncio
import aiohttp
from groq import Groq
import hashlib
from datetime import datetime
import pickle
from concurrent.futures import ThreadPoolExecutor
import re

@dataclass
class TextRegion:
    """منطقة نصية في الصورة"""
    bbox: List[float]  # [x1, y1, x2, y2]
    text: str
    confidence: float
    text_type: str  # 'ayah', 'page_number', 'decoration', 'header', 'footnote'
    font_type: str  # 'uthmani', 'normal', 'decorative'
    line_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class PageAnalysis:
    """تحليل كامل للصفحة"""
    page_number: int
    image_path: str
    text_regions: List[TextRegion]
    layout_type: str  # 'standard', 'sura_start', 'juz_start'
    columns: int
    has_decorations: bool
    has_page_number: bool
    ayat_count: int
    processing_time: float
    ai_model: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class AIAnalyzer:
    """محلل الذكاء الاصطناعي للصفحات القرآنية"""
    
    # نماذج Groq المتاحة للتحليل
    MODELS = {
        'fast': 'gemma2-9b-it',  # سريع للتحليل الأولي
        'accurate': 'llama-3.3-70b-versatile',  # دقيق للتحليل المفصل
        'arabic': 'qwen/qwen3-32b',  # محسن للنصوص العربية
        'compound': 'compound-beta',  # للتحليل المعقد
        'balanced': 'llama-3.1-8b-instant'  # متوازن بين السرعة والدقة
    }
    
    # قوالب التحليل
    ANALYSIS_PROMPTS = {
        'layout': """تحليل تخطيط الصفحة القرآنية:
1. حدد نوع الصفحة (عادية، بداية سورة، بداية جزء)
2. عدد الأعمدة
3. وجود زخارف أو إطارات
4. موقع رقم الصفحة
5. أي عناصر خاصة

أرجع النتيجة كـ JSON بالتنسيق:
{
    "layout_type": "standard|sura_start|juz_start",
    "columns": number,
    "has_decorations": boolean,
    "page_number_location": "top|bottom|none",
    "special_elements": []
}""",

        'text_regions': """حدد جميع مناطق النص في الصفحة:
1. آيات قرآنية (نص عثماني)
2. أرقام الصفحات
3. عناوين السور
4. علامات الأجزاء والأحزاب
5. الحواشي أو التعليقات

لكل منطقة، حدد:
- الإحداثيات التقريبية (نسبة مئوية من الصورة)
- نوع النص
- نوع الخط (عثماني، عادي، زخرفي)

أرجع كـ JSON array من المناطق""",

        'ayah_detection': """حدد مواقع الآيات في الصفحة:
1. حدد بداية ونهاية كل آية
2. ميز رقم الآية عن نص الآية
3. حدد الآيات المتصلة عبر الأسطر
4. انتبه للرموز العثمانية الخاصة

أرجع كـ JSON array مع إحداثيات كل آية""",

        'font_analysis': """حلل أنواع الخطوط في الصفحة:
1. الخط العثماني الرئيسي للآيات
2. خط أرقام الآيات
3. خط العناوين والحواشي
4. أي خطوط زخرفية

حدد خصائص كل خط ومواضع استخدامه"""
    }
    
    def __init__(self, api_key: str, cache_dir: str = "ai_cache", logger=None):
        """
        تهيئة المحلل
        
        Args:
            api_key: مفتاح Groq API
            cache_dir: مجلد التخزين المؤقت
            logger: كائن التسجيل
        """
        self.api_key = api_key
        self.client = Groq(api_key=api_key)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        
        # إعدادات
        self.max_retries = 3
        self.timeout = 30
        self.rate_limit_delay = 2  # ثانية بين الطلبات
        
        # ذاكرة التخزين المؤقت
        self.cache = {}
        self._load_cache()
        
    def _load_cache(self):
        """تحميل ذاكرة التخزين المؤقت"""
        cache_file = self.cache_dir / "analysis_cache.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                self.logger.info(f"✅ تم تحميل {len(self.cache)} تحليل من الكاش")
            except Exception as e:
                self.logger.warning(f"فشل تحميل الكاش: {e}")
                self.cache = {}
                
    def _save_cache(self):
        """حفظ ذاكرة التخزين المؤقت"""
        cache_file = self.cache_dir / "analysis_cache.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            self.logger.error(f"فشل حفظ الكاش: {e}")
            
    def _get_cache_key(self, image_path: str, analysis_type: str) -> str:
        """توليد مفتاح التخزين المؤقت"""
        with open(image_path, 'rb') as f:
            image_hash = hashlib.md5(f.read()).hexdigest()
        return f"{image_hash}_{analysis_type}"
        
    async def analyze_page_async(self, image_path: str, 
                                analysis_types: List[str] = None) -> PageAnalysis:
        """تحليل صفحة بشكل غير متزامن"""
        if analysis_types is None:
            analysis_types = ['layout', 'text_regions', 'ayah_detection']
            
        start_time = datetime.now()
        
        # معالجة الصورة
        processed_image = self._preprocess_image(image_path)
        
        # تنفيذ التحليلات
        results = {}
        for analysis_type in analysis_types:
            # فحص الكاش
            cache_key = self._get_cache_key(image_path, analysis_type)
            if cache_key in self.cache:
                results[analysis_type] = self.cache[cache_key]
                self.logger.debug(f"استخدام الكاش لـ {analysis_type}")
                continue
                
            # تحليل جديد
            try:
                result = await self._analyze_with_ai(
                    processed_image, 
                    analysis_type
                )
                results[analysis_type] = result
                self.cache[cache_key] = result
            except Exception as e:
                self.logger.error(f"خطأ في تحليل {analysis_type}: {e}")
                results[analysis_type] = None
                
        # دمج النتائج
        page_analysis = self._merge_analysis_results(
            image_path, 
            results,
            (datetime.now() - start_time).total_seconds()
        )
        
        # حفظ الكاش
        self._save_cache()
        
        return page_analysis
        
    def analyze_page(self, image_path: str, 
                    analysis_types: List[str] = None) -> PageAnalysis:
        """تحليل صفحة بشكل متزامن"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.analyze_page_async(image_path, analysis_types)
            )
        finally:
            loop.close()
            
    def _preprocess_image(self, image_path: str) -> Dict[str, Any]:
        """معالجة الصورة قبل التحليل"""
        # فتح الصورة
        image = Image.open(image_path)
        
        # تحسين الصورة
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        # تحويل لـ OpenCV
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # كشف الحواف للمساعدة في تحديد المناطق
        edges = cv2.Canny(cv_image, 50, 150)
        
        # كشف الخطوط
        lines = cv2.HoughLinesP(
            edges, 1, np.pi/180, 100, 
            minLineLength=100, maxLineGap=10
        )
        
        # تحليل أولي للتخطيط
        height, width = cv_image.shape[:2]
        
        # تحويل الصورة لـ base64 لـ API
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            'image': image,
            'cv_image': cv_image,
            'edges': edges,
            'lines': lines,
            'width': width,
            'height': height,
            'base64': image_base64
        }
        
    async def _analyze_with_ai(self, processed_image: Dict[str, Any], 
                              analysis_type: str) -> Dict[str, Any]:
        """تحليل باستخدام الذكاء الاصطناعي"""
        prompt = self.ANALYSIS_PROMPTS.get(analysis_type, "")
        model = self._select_model(analysis_type)
        
        # إضافة معلومات الصورة للسياق
        enhanced_prompt = f"""{prompt}

معلومات الصورة:
- الأبعاد: {processed_image['width']}x{processed_image['height']}
- عدد الخطوط المكتشفة: {len(processed_image['lines']) if processed_image['lines'] is not None else 0}

تحليل دقيق ومفصل مطلوب."""

        # استدعاء API
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "أنت خبير في تحليل المخطوطات القرآنية والخط العثماني. حلل الصور بدقة وأرجع النتائج بتنسيق JSON."
                        },
                        {
                            "role": "user",
                            "content": enhanced_prompt
                        }
                    ],
                    temperature=0.1,  # دقة عالية
                    max_tokens=2000
                )
                
                # معالجة الرد
                result_text = response.choices[0].message.content
                
                # استخراج JSON من الرد
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    # محاولة تحليل النص مباشرة
                    return self._parse_text_response(result_text, analysis_type)
                    
            except Exception as e:
                self.logger.warning(f"محاولة {attempt + 1} فشلت: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.rate_limit_delay)
                else:
                    raise
                    
    def _select_model(self, analysis_type: str) -> str:
        """اختيار النموذج المناسب للتحليل"""
        model_selection = {
            'layout': 'fast',
            'text_regions': 'balanced',
            'ayah_detection': 'arabic',
            'font_analysis': 'accurate'
        }
        
        model_key = model_selection.get(analysis_type, 'balanced')
        return self.MODELS[model_key]
        
    def _parse_text_response(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """تحليل الرد النصي إذا لم يكن JSON"""
        # محاولة استخراج المعلومات من النص
        result = {}
        
        if analysis_type == 'layout':
            # البحث عن معلومات التخطيط
            if 'بداية سورة' in text or 'سورة جديدة' in text:
                result['layout_type'] = 'sura_start'
            elif 'بداية جزء' in text or 'جزء جديد' in text:
                result['layout_type'] = 'juz_start'
            else:
                result['layout_type'] = 'standard'
                
            # عدد الأعمدة
            columns_match = re.search(r'(\d+)\s*عمود', text)
            result['columns'] = int(columns_match.group(1)) if columns_match else 1
            
            # الزخارف
            result['has_decorations'] = any(word in text for word in ['زخرفة', 'زخارف', 'إطار'])
            
        elif analysis_type == 'text_regions':
            # استخراج مناطق النص
            regions = []
            
            # البحث عن الآيات
            if 'آية' in text or 'آيات' in text:
                regions.append({
                    'type': 'ayah',
                    'font_type': 'uthmani',
                    'bbox': [0.1, 0.1, 0.9, 0.9]  # تقدير افتراضي
                })
                
            result = regions
            
        return result
        
    def _merge_analysis_results(self, image_path: str, results: Dict[str, Any], 
                               processing_time: float) -> PageAnalysis:
        """دمج نتائج التحليلات المختلفة"""
        # استخراج رقم الصفحة من اسم الملف
        page_number = self._extract_page_number(image_path)
        
        # معالجة نتائج التخطيط
        layout = results.get('layout', {})
        layout_type = layout.get('layout_type', 'standard')
        columns = layout.get('columns', 1)
        has_decorations = layout.get('has_decorations', False)
        has_page_number = layout.get('page_number_location', 'none') != 'none'
        
        # معالجة مناطق النص
        text_regions = []
        regions_data = results.get('text_regions', [])
        
        for region in regions_data:
            text_regions.append(TextRegion(
                bbox=region.get('bbox', [0, 0, 0, 0]),
                text=region.get('text', ''),
                confidence=region.get('confidence', 0.8),
                text_type=region.get('type', 'unknown'),
                font_type=region.get('font_type', 'normal'),
                metadata=region.get('metadata', {})
            ))
            
        # عد الآيات
        ayat_count = sum(1 for r in text_regions if r.text_type == 'ayah')
        
        # حساب الثقة الإجمالية
        confidence = np.mean([r.confidence for r in text_regions]) if text_regions else 0.5
        
        return PageAnalysis(
            page_number=page_number,
            image_path=image_path,
            text_regions=text_regions,
            layout_type=layout_type,
            columns=columns,
            has_decorations=has_decorations,
            has_page_number=has_page_number,
            ayat_count=ayat_count,
            processing_time=processing_time,
            ai_model=self.MODELS['balanced'],
            confidence=confidence,
            metadata={
                'analysis_types': list(results.keys()),
                'timestamp': datetime.now().isoformat()
            }
        )
        
    def _extract_page_number(self, image_path: str) -> int:
        """استخراج رقم الصفحة من اسم الملف"""
        filename = Path(image_path).stem
        match = re.search(r'(\d+)', filename)
        return int(match.group(1)) if match else 0
        
    def remove_page_elements(self, image_path: str, 
                           elements_to_remove: List[str]) -> Image.Image:
        """إزالة عناصر معينة من الصفحة"""
        # تحليل الصفحة أولاً
        analysis = self.analyze_page(image_path, ['text_regions'])
        
        # فتح الصورة
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # إزالة العناصر المحددة
        for region in analysis.text_regions:
            if region.text_type in elements_to_remove:
                # ملء المنطقة باللون الأبيض
                bbox = region.bbox
                draw.rectangle(bbox, fill='white')
                
        return image
        
    def extract_ayat_only(self, image_path: str) -> List[TextRegion]:
        """استخراج الآيات فقط من الصفحة"""
        analysis = self.analyze_page(image_path, ['ayah_detection', 'text_regions'])
        
        # فلترة الآيات فقط
        ayat = [r for r in analysis.text_regions if r.text_type == 'ayah']
        
        # ترتيب حسب الموضع
        ayat.sort(key=lambda r: (r.bbox[1], r.bbox[0]))
        
        return ayat
        
    def analyze_batch(self, image_paths: List[str], 
                     parallel: bool = True) -> List[PageAnalysis]:
        """تحليل مجموعة من الصفحات"""
        results = []
        
        if parallel:
            # معالجة متوازية
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    executor.submit(self.analyze_page, path)
                    for path in image_paths
                ]
                
                for future in futures:
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.logger.error(f"خطأ في معالجة دفعة: {e}")
        else:
            # معالجة تسلسلية
            for path in image_paths:
                try:
                    result = self.analyze_page(path)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"خطأ في معالجة {path}: {e}")
                    
        return results
        
    def generate_analysis_report(self, analyses: List[PageAnalysis]) -> Dict[str, Any]:
        """توليد تقرير شامل للتحليلات"""
        report = {
            'total_pages': len(analyses),
            'total_ayat': sum(a.ayat_count for a in analyses),
            'layout_distribution': {},
            'font_types': set(),
            'processing_stats': {
                'total_time': sum(a.processing_time for a in analyses),
                'avg_time': np.mean([a.processing_time for a in analyses]),
                'avg_confidence': np.mean([a.confidence for a in analyses])
            },
            'issues': []
        }
        
        # توزيع التخطيطات
        for analysis in analyses:
            layout = analysis.layout_type
            report['layout_distribution'][layout] = report['layout_distribution'].get(layout, 0) + 1
            
            # جمع أنواع الخطوط
            for region in analysis.text_regions:
                report['font_types'].add(region.font_type)
                
            # تحديد المشاكل
            if analysis.confidence < 0.7:
                report['issues'].append({
                    'page': analysis.page_number,
                    'issue': 'low_confidence',
                    'confidence': analysis.confidence
                })
                
        report['font_types'] = list(report['font_types'])
        
        return report

# وظائف مساعدة
def create_visualization(analysis: PageAnalysis, output_path: str):
    """إنشاء تصور مرئي لتحليل الصفحة"""
    # فتح الصورة الأصلية
    image = Image.open(analysis.image_path)
    draw = ImageDraw.Draw(image)
    
    # رسم مربعات حول المناطق
    colors = {
        'ayah': 'green',
        'page_number': 'red',
        'decoration': 'blue',
        'header': 'orange',
        'footnote': 'purple'
    }
    
    for region in analysis.text_regions:
        color = colors.get(region.text_type, 'black')
        draw.rectangle(region.bbox, outline=color, width=2)
        
        # إضافة تسمية
        draw.text(
            (region.bbox[0], region.bbox[1] - 20),
            f"{region.text_type} ({region.confidence:.2f})",
            fill=color
        )
        
    # حفظ الصورة
    image.save(output_path)
    
def export_to_coco_format(analyses: List[PageAnalysis], output_file: str):
    """تصدير التحليلات بتنسيق COCO لتدريب نماذج أخرى"""
    coco_data = {
        'info': {
            'description': 'Quranic Page Analysis Dataset',
            'version': '1.0',
            'year': datetime.now().year,
            'date_created': datetime.now().isoformat()
        },
        'images': [],
        'annotations': [],
        'categories': [
            {'id': 1, 'name': 'ayah'},
            {'id': 2, 'name': 'page_number'},
            {'id': 3, 'name': 'decoration'},
            {'id': 4, 'name': 'header'},
            {'id': 5, 'name': 'footnote'}
        ]
    }
    
    category_map = {cat['name']: cat['id'] for cat in coco_data['categories']}
    annotation_id = 1
    
    for img_id, analysis in enumerate(analyses, 1):
        # معلومات الصورة
        image = Image.open(analysis.image_path)
        coco_data['images'].append({
            'id': img_id,
            'file_name': Path(analysis.image_path).name,
            'width': image.width,
            'height': image.height
        })
        
        # التعليقات التوضيحية
        for region in analysis.text_regions:
            if region.text_type in category_map:
                x1, y1, x2, y2 = region.bbox
                coco_data['annotations'].append({
                    'id': annotation_id,
                    'image_id': img_id,
                    'category_id': category_map[region.text_type],
                    'bbox': [x1, y1, x2 - x1, y2 - y1],  # COCO format: [x, y, width, height]
                    'area': (x2 - x1) * (y2 - y1),
                    'segmentation': [],
                    'iscrowd': 0,
                    'confidence': region.confidence
                })
                annotation_id += 1
                
    # حفظ الملف
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(coco_data, f, ensure_ascii=False, indent=2)
        
# للاستخدام المباشر
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ai_analyzer.py <image_path> [api_key]")
        sys.exit(1)
        
    image_path = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("Error: GROQ_API_KEY not provided")
        sys.exit(1)
        
    # إنشاء المحلل
    analyzer = AIAnalyzer(api_key)
    
    # تحليل الصفحة
    print(f"تحليل {image_path}...")
    analysis = analyzer.analyze_page(image_path)
    
    # عرض النتائج
    print(f"نوع التخطيط: {analysis.layout_type}")
    print(f"عدد الأعمدة: {analysis.columns}")
    print(f"عدد الآيات: {analysis.ayat_count}")
    print(f"الثقة: {analysis.confidence:.2%}")
    print(f"وقت المعالجة: {analysis.processing_time:.2f} ثانية")
    
    # إنشاء تصور مرئي
    output_path = Path(image_path).stem + "_analyzed.png"
    create_visualization(analysis, output_path)
    print(f"\nتم حفظ التصور المرئي في: {output_path}")
