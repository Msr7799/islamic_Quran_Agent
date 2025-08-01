#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مكتبة دعم الذكاء الاصطناعي لصفحات المصحف
يوفر وظائف متقدمة لمعالجة وتحليل صفحات SVG/الصور

المميزات:
- تحميل وإدارة الصفحات
- معالجة دفعية بالذكاء الاصطناعي
- تحليل التخطيط والخطوط
- استخراج الآيات الذكي
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import xml.etree.ElementTree as ET
from tqdm import tqdm

class PageManager:
    """مدير صفحات المصحف مع دعم الذكاء الاصطناعي"""
    
    def __init__(self, pages_dir: str = None, logger=None):
        """
        تهيئة مدير الصفحات
        
        Args:
            pages_dir: مسار مجلد الصفحات
            logger: كائن التسجيل
        """
        self.pages_dir = Path(pages_dir or os.path.dirname(__file__))
        self.logger = logger or logging.getLogger(__name__)
        
        # فهرس الصفحات
        self.pages_index = self._build_pages_index()
        
        # معلومات المصحف
        self.quran_info = self._load_quran_info()
        
    def _build_pages_index(self) -> Dict[int, Dict[str, Any]]:
        """بناء فهرس الصفحات المتاحة"""
        index = {}
        
        # البحث عن ملفات SVG
        svg_files = list(self.pages_dir.glob("page_*.svg"))
        for svg_file in svg_files:
            page_num = self._extract_page_number(svg_file.name)
            if page_num:
                index[page_num] = {
                    'svg_path': str(svg_file),
                    'type': 'svg',
                    'size': svg_file.stat().st_size,
                    'modified': svg_file.stat().st_mtime
                }
                
        # البحث عن ملفات الصور
        for ext in ['png', 'jpg', 'jpeg']:
            image_files = list(self.pages_dir.glob(f"page_*.{ext}"))
            for img_file in image_files:
                page_num = self._extract_page_number(img_file.name)
                if page_num:
                    if page_num in index:
                        index[page_num]['image_path'] = str(img_file)
                    else:
                        index[page_num] = {
                            'image_path': str(img_file),
                            'type': 'image',
                            'size': img_file.stat().st_size,
                            'modified': img_file.stat().st_mtime
                        }
                        
        self.logger.info(f"✅ تم فهرسة {len(index)} صفحة")
        return index
        
    def _extract_page_number(self, filename: str) -> Optional[int]:
        """استخراج رقم الصفحة من اسم الملف"""
        import re
        match = re.search(r'page[_-]?(\d+)', filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
        
    def _load_quran_info(self) -> Dict[str, Any]:
        """تحميل معلومات المصحف"""
        info_file = self.pages_dir.parent / "quran_metadata.json"
        
        if info_file.exists():
            with open(info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # معلومات افتراضية
            return {
                'total_pages': 604,
                'total_suras': 114,
                'total_juz': 30,
                'page_mapping': self._generate_default_mapping()
            }
            
    def _generate_default_mapping(self) -> Dict[str, Any]:
        """توليد خريطة افتراضية للصفحات"""
        # معلومات أساسية عن توزيع السور والأجزاء
        return {
            'sura_starts': {
                1: 1,    # الفاتحة
                2: 2,    # البقرة
                # ... يمكن إضافة المزيد
            },
            'juz_starts': {
                1: 1,
                2: 22,
                # ... يمكن إضافة المزيد
            }
        }
        
    def get_page(self, page_number: int) -> Optional[Dict[str, Any]]:
        """الحصول على معلومات صفحة"""
        return self.pages_index.get(page_number)
        
    def get_page_range(self, start: int, end: int) -> List[Dict[str, Any]]:
        """الحصول على نطاق من الصفحات"""
        pages = []
        for page_num in range(start, end + 1):
            if page_num in self.pages_index:
                page_info = self.pages_index[page_num].copy()
                page_info['page_number'] = page_num
                pages.append(page_info)
        return pages
        
    def load_svg_content(self, page_number: int) -> Optional[ET.Element]:
        """تحميل محتوى SVG"""
        page_info = self.get_page(page_number)
        if page_info and 'svg_path' in page_info:
            try:
                tree = ET.parse(page_info['svg_path'])
                return tree.getroot()
            except Exception as e:
                self.logger.error(f"خطأ في تحميل SVG للصفحة {page_number}: {e}")
        return None
        
    def load_image(self, page_number: int) -> Optional[Image.Image]:
        """تحميل صورة الصفحة"""
        page_info = self.get_page(page_number)
        
        # محاولة تحميل الصورة إن وجدت
        if page_info and 'image_path' in page_info:
            try:
                return Image.open(page_info['image_path'])
            except Exception as e:
                self.logger.error(f"خطأ في تحميل صورة الصفحة {page_number}: {e}")
                
        # محاولة تحويل SVG إلى صورة
        if page_info and 'svg_path' in page_info:
            return self._convert_svg_to_image(page_info['svg_path'])
            
        return None
        
    def _convert_svg_to_image(self, svg_path: str) -> Optional[Image.Image]:
        """تحويل SVG إلى صورة"""
        try:
            # استخدام cairosvg إن كان متاحاً
            import cairosvg
            import io
            
            png_data = cairosvg.svg2png(url=svg_path)
            return Image.open(io.BytesIO(png_data))
        except ImportError:
            self.logger.warning("cairosvg غير مثبت، لا يمكن تحويل SVG")
        except Exception as e:
            self.logger.error(f"خطأ في تحويل SVG: {e}")
            
        return None
        
    def prepare_for_ai_analysis(self, page_numbers: List[int], 
                               output_dir: str = None) -> List[str]:
        """تحضير الصفحات لتحليل الذكاء الاصطناعي"""
        if output_dir is None:
            output_dir = self.pages_dir / "ai_ready"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        prepared_files = []
        
        for page_num in tqdm(page_numbers, desc="تحضير الصفحات"):
            image = self.load_image(page_num)
            
            if image:
                # تحسين الصورة للذكاء الاصطناعي
                enhanced = self._enhance_image_for_ai(image)
                
                # حفظ الصورة
                output_path = output_dir / f"page_{page_num:03d}_enhanced.png"
                enhanced.save(output_path)
                prepared_files.append(str(output_path))
                
        self.logger.info(f"✅ تم تحضير {len(prepared_files)} صفحة للتحليل")
        return prepared_files
        
    def _enhance_image_for_ai(self, image: Image.Image) -> Image.Image:
        """تحسين الصورة لتحليل الذكاء الاصطناعي"""
        # تحويل إلى numpy array
        img_array = np.array(image)
        
        # تحويل إلى grayscale إذا كانت ملونة
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
            
        # تحسين التباين
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # إزالة الضوضاء
        denoised = cv2.fastNlMeansDenoising(enhanced)
        
        # تحديد الحواف لتحسين النص
        edges = cv2.Canny(denoised, 50, 150)
        
        # دمج الحواف مع الصورة الأصلية
        result = cv2.addWeighted(denoised, 0.8, edges, 0.2, 0)
        
        # تحويل مرة أخرى إلى PIL Image
        return Image.fromarray(result)
        
    def analyze_page_structure(self, page_number: int) -> Dict[str, Any]:
        """تحليل بنية الصفحة"""
        svg_root = self.load_svg_content(page_number)
        if not svg_root:
            return {}
            
        structure = {
            'page_number': page_number,
            'elements': {
                'text_elements': 0,
                'use_elements': 0,
                'path_elements': 0,
                'group_elements': 0
            },
            'text_regions': [],
            'decorative_elements': [],
            'estimated_layout': None
        }
        
        # عد العناصر
        for elem in svg_root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if tag == 'text':
                structure['elements']['text_elements'] += 1
            elif tag == 'use':
                structure['elements']['use_elements'] += 1
            elif tag == 'path':
                structure['elements']['path_elements'] += 1
            elif tag == 'g':
                structure['elements']['group_elements'] += 1
                
        # تحليل التخطيط
        structure['estimated_layout'] = self._estimate_layout(svg_root)
        
        return structure
        
    def _estimate_layout(self, svg_root: ET.Element) -> str:
        """تقدير نوع تخطيط الصفحة"""
        # البحث عن مؤشرات تخطيط خاصة
        decorative_count = 0
        text_count = 0
        
        for elem in svg_root.iter():
            if 'class' in elem.attrib:
                if 'decorative' in elem.attrib['class'].lower():
                    decorative_count += 1
                elif 'text' in elem.attrib['class'].lower():
                    text_count += 1
                    
        # تقدير نوع الصفحة
        if decorative_count > 10:
            return 'sura_start'  # بداية سورة
        elif decorative_count > 5:
            return 'juz_start'   # بداية جزء
        else:
            return 'standard'    # صفحة عادية
            
    def get_page_statistics(self) -> Dict[str, Any]:
        """إحصائيات الصفحات"""
        stats = {
            'total_pages': len(self.pages_index),
            'svg_pages': 0,
            'image_pages': 0,
            'both_formats': 0,
            'total_size_mb': 0,
            'page_types': {}
        }
        
        for page_info in self.pages_index.values():
            has_svg = 'svg_path' in page_info
            has_image = 'image_path' in page_info
            
            if has_svg:
                stats['svg_pages'] += 1
            if has_image:
                stats['image_pages'] += 1
            if has_svg and has_image:
                stats['both_formats'] += 1
                
            stats['total_size_mb'] += page_info['size'] / (1024 * 1024)
            
            page_type = page_info.get('type', 'unknown')
            stats['page_types'][page_type] = stats['page_types'].get(page_type, 0) + 1
            
        return stats
        
    def export_page_index(self, output_file: str):
        """تصدير فهرس الصفحات"""
        export_data = {
            'metadata': {
                'total_pages': len(self.pages_index),
                'generated_at': datetime.now().isoformat(),
                'pages_dir': str(self.pages_dir)
            },
            'pages': self.pages_index,
            'statistics': self.get_page_statistics()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"✅ تم تصدير الفهرس إلى: {output_file}")

# وظائف مساعدة للاستخدام المباشر
def process_pages_with_ai(pages_dir: str, ai_analyzer, 
                         page_range: Optional[Tuple[int, int]] = None,
                         batch_size: int = 10) -> List[Any]:
    """معالجة الصفحات باستخدام الذكاء الاصطناعي"""
    manager = PageManager(pages_dir)
    
    # تحديد الصفحات للمعالجة
    if page_range:
        pages = manager.get_page_range(page_range[0], page_range[1])
    else:
        pages = [{'page_number': p, **info} for p, info in manager.pages_index.items()]
        
    # تحضير الصفحات
    page_numbers = [p['page_number'] for p in pages]
    prepared_files = manager.prepare_for_ai_analysis(page_numbers)
    
    # معالجة دفعية
    results = []
    for i in range(0, len(prepared_files), batch_size):
        batch = prepared_files[i:i + batch_size]
        batch_results = ai_analyzer.analyze_batch(batch)
        results.extend(batch_results)
        
    return results

def create_training_dataset(pages_dir: str, output_dir: str, 
                          sample_size: Optional[int] = None):
    """إنشاء مجموعة بيانات للتدريب"""
    manager = PageManager(pages_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # اختيار عينة عشوائية
    import random
    all_pages = list(manager.pages_index.keys())
    
    if sample_size and sample_size < len(all_pages):
        selected_pages = random.sample(all_pages, sample_size)
    else:
        selected_pages = all_pages
        
    # تنظيم البيانات
    train_dir = output_dir / "train"
    val_dir = output_dir / "val"
    test_dir = output_dir / "test"
    
    for dir_path in [train_dir, val_dir, test_dir]:
        dir_path.mkdir(exist_ok=True)
        
    # تقسيم البيانات (70% train, 20% val, 10% test)
    random.shuffle(selected_pages)
    
    train_size = int(0.7 * len(selected_pages))
    val_size = int(0.2 * len(selected_pages))
    
    train_pages = selected_pages[:train_size]
    val_pages = selected_pages[train_size:train_size + val_size]
    test_pages = selected_pages[train_size + val_size:]
    
    # نسخ الملفات
    dataset_info = {
        'train': {'pages': train_pages, 'dir': train_dir},
        'val': {'pages': val_pages, 'dir': val_dir},
        'test': {'pages': test_pages, 'dir': test_dir}
    }
    
    for split_name, split_info in dataset_info.items():
        for page_num in tqdm(split_info['pages'], desc=f"إعداد {split_name}"):
            # تحضير الصفحة
            image = manager.load_image(page_num)
            if image:
                output_path = split_info['dir'] / f"page_{page_num:03d}.png"
                image.save(output_path)
                
    # حفظ معلومات المجموعة
    dataset_metadata = {
        'total_pages': len(selected_pages),
        'splits': {
            'train': len(train_pages),
            'val': len(val_pages),
            'test': len(test_pages)
        },
        'created_at': datetime.now().isoformat()
    }
    
    with open(output_dir / "dataset_info.json", 'w') as f:
        json.dump(dataset_metadata, f, indent=2)
        
    return dataset_metadata

# تصدير الواجهات الرئيسية
__all__ = [
    'PageManager',
    'process_pages_with_ai',
    'create_training_dataset'
]
