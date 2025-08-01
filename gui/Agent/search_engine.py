#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
محرك البحث المتطور باستخدام Tavily API
يوفر إمكانيات بحث متقدمة في الإنترنت للمساعدة في تحليل النصوص القرآنية

المميزات:
- بحث ذكي في الإنترنت
- تصفية النتائج حسب الموضوع
- دعم البحث باللغة العربية والإنجليزية
- تحليل وتلخيص النتائج
"""

import os
import json
import requests
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re

# تحميل متغيرات البيئة من ملف .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # إذا لم تكن مكتبة python-dotenv مثبتة، نقرأ الملف يدوياً
    def load_env_file():
        env_file = '.env'
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    load_env_file()

@dataclass
class SearchResult:
    """نتيجة بحث واحدة"""
    title: str
    url: str
    content: str
    score: float
    published_date: Optional[str] = None
    domain: Optional[str] = None
    language: Optional[str] = None

@dataclass
class SearchResponse:
    """استجابة البحث الكاملة"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    timestamp: str
    summary: Optional[str] = None

class TavilySearchEngine:
    """محرك البحث باستخدام Tavily API"""
    
    def __init__(self, api_key: str = None, logger=None):
        """
        تهيئة محرك البحث
        
        Args:
            api_key: مفتاح Tavily API
            logger: كائن التسجيل
        """
        self.api_key = api_key or os.getenv('TAVILY_API_KEY')
        self.logger = logger or logging.getLogger(__name__)
        
        if not self.api_key:
            raise ValueError("مفتاح Tavily API مطلوب. ضعه في متغير البيئة TAVILY_API_KEY")
            
        # إعدادات API
        self.base_url = "https://api.tavily.com"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # إعدادات البحث الافتراضية
        self.default_config = {
            "search_depth": "advanced",
            "max_results": 10,
            "include_answer": True,
            "include_raw_content": False,
            "include_domains": [],
            "exclude_domains": [],
            "topic": "general"
        }
        
    def search(self, query: str, **kwargs) -> SearchResponse:
        """
        البحث في الإنترنت
        
        Args:
            query: استعلام البحث
            **kwargs: إعدادات إضافية للبحث
            
        Returns:
            نتائج البحث
        """
        start_time = datetime.now()
        
        # دمج الإعدادات
        config = {**self.default_config, **kwargs}
        
        # إعداد طلب البحث
        search_request = {
            "query": query,
            "search_depth": config["search_depth"],
            "max_results": config["max_results"],
            "include_answer": config["include_answer"],
            "include_raw_content": config["include_raw_content"],
            "topic": config["topic"]
        }
        
        # إضافة المجالات المحددة
        if config["include_domains"]:
            search_request["include_domains"] = config["include_domains"]
        if config["exclude_domains"]:
            search_request["exclude_domains"] = config["exclude_domains"]
            
        try:
            # إرسال الطلب
            response = requests.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json=search_request,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # معالجة النتائج
            results = []
            for item in data.get("results", []):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    score=item.get("score", 0.0),
                    published_date=item.get("published_date"),
                    domain=self._extract_domain(item.get("url", "")),
                    language=self._detect_language(item.get("content", ""))
                )
                results.append(result)
                
            # حساب وقت البحث
            search_time = (datetime.now() - start_time).total_seconds()
            
            # إنشاء الاستجابة
            search_response = SearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                timestamp=datetime.now().isoformat(),
                summary=data.get("answer")
            )
            
            self.logger.info(f"🔍 تم البحث عن: '{query}' - {len(results)} نتيجة في {search_time:.2f}s")
            
            return search_response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ خطأ في البحث: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ خطأ غير متوقع: {e}")
            raise
            
    def search_quran_related(self, query: str, **kwargs) -> SearchResponse:
        """
        بحث متخصص في المواضيع القرآنية
        
        Args:
            query: استعلام البحث
            **kwargs: إعدادات إضافية
            
        Returns:
            نتائج البحث المتخصصة
        """
        # إضافة كلمات مفتاحية قرآنية
        enhanced_query = f"{query} القرآن الكريم تفسير"
        
        # مجالات موثوقة للمحتوى القرآني
        trusted_domains = [
            "islamweb.net",
            "alukah.net",
            "islamqa.info",
            "dorar.net",
            "quran.com",
            "tanzil.net"
        ]
        
        # إعدادات متخصصة
        config = {
            "include_domains": trusted_domains,
            "search_depth": "advanced",
            "max_results": 15,
            **kwargs
        }
        
        return self.search(enhanced_query, **config)
        
    def search_academic(self, query: str, **kwargs) -> SearchResponse:
        """
        بحث أكاديمي متخصص
        
        Args:
            query: استعلام البحث
            **kwargs: إعدادات إضافية
            
        Returns:
            نتائج البحث الأكاديمية
        """
        # إضافة كلمات أكاديمية
        academic_query = f"{query} research paper academic study"
        
        # مجالات أكاديمية
        academic_domains = [
            "scholar.google.com",
            "researchgate.net",
            "academia.edu",
            "jstor.org",
            "springer.com",
            "ieee.org"
        ]
        
        config = {
            "include_domains": academic_domains,
            "search_depth": "advanced",
            "max_results": 20,
            **kwargs
        }
        
        return self.search(academic_query, **config)
        
    def _extract_domain(self, url: str) -> str:
        """استخراج اسم المجال من الرابط"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ""
            
    def _detect_language(self, text: str) -> str:
        """كشف لغة النص (بسيط)"""
        if not text:
            return "unknown"
            
        # عد الأحرف العربية
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        total_chars = len(re.findall(r'[a-zA-Z\u0600-\u06FF]', text))
        
        if total_chars == 0:
            return "unknown"
            
        arabic_ratio = arabic_chars / total_chars
        
        if arabic_ratio > 0.3:
            return "arabic"
        else:
            return "english"
            
    def summarize_results(self, search_response: SearchResponse, max_length: int = 500) -> str:
        """
        تلخيص نتائج البحث
        
        Args:
            search_response: نتائج البحث
            max_length: الحد الأقصى لطول الملخص
            
        Returns:
            ملخص النتائج
        """
        if search_response.summary:
            return search_response.summary[:max_length]
            
        # إنشاء ملخص من النتائج
        all_content = []
        for result in search_response.results[:5]:  # أول 5 نتائج
            if result.content:
                all_content.append(result.content[:200])
                
        combined_content = " ".join(all_content)
        
        # تقصير الملخص
        if len(combined_content) > max_length:
            combined_content = combined_content[:max_length] + "..."
            
        return combined_content
        
    def export_results(self, search_response: SearchResponse, output_file: str):
        """
        تصدير نتائج البحث إلى ملف
        
        Args:
            search_response: نتائج البحث
            output_file: ملف الإخراج
        """
        export_data = {
            "query": search_response.query,
            "timestamp": search_response.timestamp,
            "total_results": search_response.total_results,
            "search_time": search_response.search_time,
            "summary": search_response.summary,
            "results": [
                {
                    "title": result.title,
                    "url": result.url,
                    "content": result.content,
                    "score": result.score,
                    "domain": result.domain,
                    "language": result.language
                }
                for result in search_response.results
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"📄 تم تصدير النتائج إلى: {output_file}")

# للاستخدام المباشر
if __name__ == "__main__":
    import sys
    
    # إعداد التسجيل
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) < 2:
        print("Usage: python search_engine.py <search_query>")
        sys.exit(1)
        
    query = " ".join(sys.argv[1:])
    
    try:
        # إنشاء محرك البحث
        search_engine = TavilySearchEngine()
        
        # البحث
        results = search_engine.search(query)
        
        # عرض النتائج
        print(f"\n🔍 نتائج البحث عن: '{query}'")
        print(f"📊 عدد النتائج: {results.total_results}")
        print(f"⏱️ وقت البحث: {results.search_time:.2f} ثانية")
        
        if results.summary:
            print(f"\n📝 الملخص: {results.summary}")
            
        print("\n📋 النتائج:")
        for i, result in enumerate(results.results[:5], 1):
            print(f"\n{i}. {result.title}")
            print(f"   🔗 {result.url}")
            print(f"   📄 {result.content[:200]}...")
            print(f"   ⭐ النقاط: {result.score:.2f}")
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        sys.exit(1)
