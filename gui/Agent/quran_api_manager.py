import aiohttp
import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from urllib.parse import quote
import logging
from bs4 import BeautifulSoup

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuranComplexAPI:
    """API مجمع الملك فهد للطباعة"""
    
    def __init__(self):
        self.base_url = "https://qurancomplex.gov.sa/techquran/dev"
        self.session = None
        
    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
            # Ensure the session is properly initialized
            await asyncio.sleep(0)
            
    async def close_session(self):
        if self.session:
            await self.session.close()
            
    async def search_ayah(self, query: str, mushaf_id: int = 2) -> Dict:
        """البحث عن آية
        
        Args:
            query: نص البحث
            mushaf_id: رقم المصحف (2 = مصحف المدينة النبوية)
        """
        await self.init_session()
        
        try:
            # تنظيف وترميز الاستعلام
            clean_query = quote(query)
            
            # نقاط النهاية المختلفة للبحث
            endpoints = [
                f"/api/v1/search/ayah?query={clean_query}&mushaf={mushaf_id}",
                f"/api/v1/ayah/search?q={clean_query}",
                f"/api/v1/mushaf/{mushaf_id}/search?q={clean_query}"
            ]
            
            results = []
            for endpoint in endpoints:
                url = self.base_url + endpoint
                logger.info(f"Searching: {url}")
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('data') or data.get('results'):
                            results.extend(data.get('data', data.get('results', [])))
                            
            return {
                "status": "success",
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error in search_ayah: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def get_page_data(self, page_number: int, mushaf_id: int = 2) -> Dict:
        """الحصول على بيانات صفحة معينة"""
        await self.init_session()
        
        try:
            url = f"{self.base_url}/api/v1/mushaf/{mushaf_id}/page/{page_number}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error in get_page_data: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def get_surah_info(self, surah_number: int) -> Dict:
        """الحصول على معلومات السورة"""
        await self.init_session()
        
        try:
            url = f"{self.base_url}/api/v1/surah/{surah_number}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error in get_surah_info: {str(e)}")
            return {"status": "error", "message": str(e)}

class AlQuranCloudAPI:
    """Al-Quran Cloud API"""
    
    def __init__(self):
        self.base_url = "https://alquran.cloud/api"
        self.session = None
        
    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
            # Ensure the session is properly initialized
            await asyncio.sleep(0)
            
    async def close_session(self):
        if self.session:
            await self.session.close()
            
    async def search(self, keyword: str, surah: Optional[int] = None, 
                    edition: str = "quran-uthmani") -> Dict:
        """البحث في القرآن"""
        await self.init_session()
        
        try:
            # تحديد نطاق البحث
            search_scope = "all" if not surah else str(surah)
            url = f"{self.base_url}/search/{quote(keyword)}/{search_scope}/{edition}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def get_ayah(self, reference: str, editions: List[str] = None) -> Dict:
        """الحصول على آية محددة
        
        Args:
            reference: مرجع الآية (مثال: "2:255" للبقرة 255)
            editions: قائمة بالإصدارات المطلوبة
        """
        await self.init_session()
        
        if not editions:
            editions = ["quran-uthmani", "ar.alafasy", "en.sahih"]
            
        try:
            editions_str = ",".join(editions)
            url = f"{self.base_url}/ayah/{reference}/editions/{editions_str}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error in get_ayah: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def get_surah(self, surah_number: int, edition: str = "quran-uthmani") -> Dict:
        """الحصول على سورة كاملة"""
        await self.init_session()
        
        try:
            url = f"{self.base_url}/surah/{surah_number}/{edition}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error in get_surah: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def get_juz(self, juz_number: int, edition: str = "quran-uthmani") -> Dict:
        """الحصول على جزء كامل"""
        await self.init_session()
        
        try:
            url = f"{self.base_url}/juz/{juz_number}/{edition}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error in get_juz: {str(e)}")
            return {"status": "error", "message": str(e)}

class AyahByAyahAPI:
    """API موقع آية بآية"""
    
    def __init__(self):
        self.base_url = "https://verse.quran.com/api"  # يحتاج تحديث للURL الصحيح
        self.session = None
        
    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
            # Ensure the session is properly initialized
            await asyncio.sleep(0)
            
    async def close_session(self):
        if self.session:
            await self.session.close()
            
    async def get_verse_details(self, verse_key: str) -> Dict:
        """الحصول على تفاصيل آية"""
        await self.init_session()
        
        try:
            # verse_key format: "chapter:verse" e.g., "2:255"
            url = f"{self.base_url}/verses/{verse_key}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error in get_verse_details: {str(e)}")
            return {"status": "error", "message": str(e)}

class WebSearchAPI:
    """بحث الويب العام"""
    
    def __init__(self):
        self.session = None
        
    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
            
    async def close_session(self):
        if self.session:
            await self.session.close()
            
    async def search_duckduckgo(self, query: str) -> List[Dict]:
        """البحث باستخدام DuckDuckGo"""
        await self.init_session()
        
        try:
            # استخدام DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    
                    # معالجة النتائج
                    if data.get('AbstractText'):
                        results.append({
                            'title': data.get('Heading', 'نتيجة'),
                            'snippet': data['AbstractText'],
                            'url': data.get('AbstractURL', '')
                        })
                        
                    # النتائج ذات الصلة
                    for related in data.get('RelatedTopics', []):
                        if isinstance(related, dict) and related.get('Text'):
                            results.append({
                                'title': related.get('Text', '').split(' - ')[0],
                                'snippet': related.get('Text', ''),
                                'url': related.get('FirstURL', '')
                            })
                            
                    return results[:10]  # أول 10 نتائج
                    
        except Exception as e:
            logger.error(f"Error in search_duckduckgo: {str(e)}")
            return []
            
    async def search_searx(self, query: str, instance: str = "https://searx.be") -> List[Dict]:
        """البحث باستخدام SearX (محرك بحث مفتوح المصدر)"""
        await self.init_session()
        
        try:
            url = f"{instance}/search"
            params = {
                'q': query,
                'format': 'json',
                'categories': 'general',
                'language': 'ar'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('results', [])
                    
        except Exception as e:
            logger.error(f"Error in search_searx: {str(e)}")
            return []

class UnifiedQuranAPI:
    """واجهة موحدة لجميع APIs القرآن"""
    
    def __init__(self):
        self.quran_complex = QuranComplexAPI()
        self.alquran_cloud = AlQuranCloudAPI()
        self.ayah_by_ayah = AyahByAyahAPI()
        self.web_search = WebSearchAPI()
        
    async def close_all_sessions(self):
        """إغلاق جميع الجلسات"""
        await self.quran_complex.close_session()
        await self.alquran_cloud.close_session()
        await self.ayah_by_ayah.close_session()
        await self.web_search.close_session()
        
    async def search_all_sources(self, query: str) -> Dict[str, Any]:
        """البحث في جميع المصادر"""
        results = {
            "query": query,
            "sources": {}
        }
        
        # البحث في مجمع الملك فهد
        try:
            quran_complex_results = await self.quran_complex.search_ayah(query)
            results["sources"]["quran_complex"] = quran_complex_results
        except Exception as e:
            results["sources"]["quran_complex"] = {"error": str(e)}
            
        # البحث في Al-Quran Cloud
        try:
            alquran_results = await self.alquran_cloud.search(query)
            results["sources"]["alquran_cloud"] = alquran_results
        except Exception as e:
            results["sources"]["alquran_cloud"] = {"error": str(e)}
            
        # البحث في الويب
        try:
            web_results = await self.web_search.search_duckduckgo(f"القرآن الكريم {query}")
            results["sources"]["web_search"] = {"results": web_results}
        except Exception as e:
            results["sources"]["web_search"] = {"error": str(e)}
            
        return results
        
    async def get_ayah_with_tafsir(self, surah: int, ayah: int) -> Dict:
        """الحصول على آية مع التفسير من مصادر متعددة"""
        results = {
            "reference": f"{surah}:{ayah}",
            "data": {}
        }
        
        # من Al-Quran Cloud - نص الآية بإصدارات مختلفة
        try:
            editions = [
                "quran-uthmani",      # النص العثماني
                "ar.alafasy",         # تلاوة العفاسي
                "ar.jalalayn",        # تفسير الجلالين
                "ar.muyassar",        # التفسير الميسر
                "en.sahih"            # ترجمة صحيح انترناشيونال
            ]
            
            ayah_data = await self.alquran_cloud.get_ayah(f"{surah}:{ayah}", editions)
            results["data"]["alquran_cloud"] = ayah_data
            
        except Exception as e:
            results["data"]["alquran_cloud"] = {"error": str(e)}
            
        # من مجمع الملك فهد
        try:
            # الحصول على معلومات السورة أولاً
            surah_info = await self.quran_complex.get_surah_info(surah)
            results["data"]["surah_info"] = surah_info
            
        except Exception as e:
            results["data"]["quran_complex"] = {"error": str(e)}
            
        return results
        
    async def download_mushaf_page(self, page_number: int, 
                                  mushaf_type: str = "hafs") -> Optional[bytes]:
        """تحميل صفحة من المصحف"""
        await self.quran_complex.init_session()
        
        mushaf_urls = {
            "hafs": f"https://qurancomplex.gov.sa/data/mushaf/1/{page_number:03d}.png",
            "warsh": f"https://qurancomplex.gov.sa/data/mushaf/2/{page_number:03d}.png",
            "qaloon": f"https://qurancomplex.gov.sa/data/mushaf/3/{page_number:03d}.png"
        }
        
        url = mushaf_urls.get(mushaf_type)
        if not url:
            return None
            
        try:
            async with self.quran_complex.session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                    
        except Exception as e:
            logger.error(f"Error downloading page: {str(e)}")
            
        return None

# وظائف مساعدة
def parse_ayah_reference(reference: str) -> tuple:
    """تحليل مرجع الآية
    
    Args:
        reference: مرجع الآية مثل "2:255" أو "البقرة:255"
        
    Returns:
        tuple: (رقم السورة، رقم الآية)
    """
    # قاموس أسماء السور
    surah_names = {
        "الفاتحة": 1, "البقرة": 2, "آل عمران": 3, "النساء": 4,
        "المائدة": 5, "الأنعام": 6, "الأعراف": 7, "الأنفال": 8,
        "التوبة": 9, "يونس": 10, "هود": 11, "يوسف": 12,
        "الرعد": 13, "إبراهيم": 14, "الحجر": 15, "النحل": 16,
        "الإسراء": 17, "الكهف": 18, "مريم": 19, "طه": 20,
        # ... يمكن إكمال باقي السور
    }
    
    # محاولة تحليل بالأرقام
    match = re.match(r"(\d+):(\d+)", reference)
    if match:
        return int(match.group(1)), int(match.group(2))
        
    # محاولة تحليل بالأسماء
    for name, number in surah_names.items():
        if name in reference:
            ayah_match = re.search(r":(\d+)", reference)
            if ayah_match:
                return number, int(ayah_match.group(1))
                
    return None, None

async def example_usage():
    """مثال على الاستخدام"""
    api = UnifiedQuranAPI()
    
    try:
        # البحث في جميع المصادر
        print("البحث عن 'الرحمن الرحيم'...")
        results = await api.search_all_sources("الرحمن الرحيم")
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
        # الحصول على آية مع التفسير
        print("\nالحصول على آية الكرسي مع التفسير...")
        ayah_data = await api.get_ayah_with_tafsir(2, 255)
        print(json.dumps(ayah_data, ensure_ascii=False, indent=2))
        
        # تحميل صفحة من المصحف
        print("\nتحميل الصفحة الأولى من المصحف...")
        page_data = await api.download_mushaf_page(1)
        if page_data:
            with open("mushaf_page_001.png", "wb") as f:
                f.write(page_data)
            print("تم حفظ الصفحة!")
            
    finally:
        await api.close_all_sessions()

if __name__ == "__main__":
    # تشغيل المثال
    asyncio.run(example_usage())
