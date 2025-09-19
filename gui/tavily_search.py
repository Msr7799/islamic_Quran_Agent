#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import json
from typing import Dict, List, Optional

class TavilySearchClient:
    """عميل البحث في الإنترنت باستخدام Tavily API"""
    
    def __init__(self):
        self.api_key = os.getenv('TAVILY_API_KEY')
        self.base_url = "https://api.tavily.com"
        
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY غير موجود في متغيرات البيئة")
    
    def search(self, query: str, max_results: int = 5, include_domains: Optional[List[str]] = None, 
               exclude_domains: Optional[List[str]] = None) -> Dict:
        """البحث في الإنترنت باستخدام Tavily"""
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": False,
            "include_images": False
        }
        
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        
        try:
            response = requests.post(
                f"{self.base_url}/search",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"خطأ في البحث: {e}")
            return {"error": str(e), "results": []}
    
    def get_usage(self) -> Dict:
        """الحصول على معلومات الاستخدام"""
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/usage",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"خطأ في الحصول على الاستخدام: {e}")
            return {"error": str(e)}
    
    def format_search_results(self, results: Dict) -> str:
        """تنسيق نتائج البحث للعرض"""
        if "error" in results:
            return f"❌ خطأ في البحث: {results['error']}"
        
        if not results.get("results"):
            return "❌ لم يتم العثور على نتائج"
        
        formatted = "🌐 **نتائج البحث في الإنترنت:**\n\n"
        
        # إضافة الإجابة المباشرة إن وجدت
        if results.get("answer"):
            formatted += f"💡 **الإجابة المباشرة:**\n{results['answer']}\n\n"
        
        formatted += "📋 **المصادر:**\n"
        
        for i, result in enumerate(results["results"][:5], 1):
            title = result.get("title", "بدون عنوان")
            url = result.get("url", "")
            content = result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", "")
            
            formatted += f"\n**{i}. {title}**\n"
            formatted += f"🔗 {url}\n"
            formatted += f"📄 {content}\n"
            formatted += "─" * 50 + "\n"
        
        return formatted

# اختبار الاتصال
if __name__ == "__main__":
    try:
        client = TavilySearchClient()
        usage = client.get_usage()
        print("✅ تم الاتصال بـ Tavily بنجاح")
        print(f"معلومات الاستخدام: {usage}")
    except Exception as e:
        print(f"❌ خطأ في التهيئة: {e}")
