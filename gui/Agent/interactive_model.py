#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
واجهة تفاعلية للتعامل مع النموذج
تسمح بتشغيل واختبار جميع مكونات النظام

المميزات:
- واجهة سطر أوامر تفاعلية
- اختبار المكونات المختلفة
- عرض حالة النظام
- تشغيل المهام المختلفة
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import subprocess

# تحميل متغيرات البيئة من ملف .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ تم تحميل متغيرات البيئة من .env")
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
            print("✅ تم تحميل متغيرات البيئة يدوياً من .env")
        else:
            print("⚠️ ملف .env غير موجود")
    load_env_file()


# إضافة جذر مجلد gui إلى sys.path ليعمل الاستيراد من Agent بشكل صحيح
sys.path.insert(0, str(Path(__file__).parent.parent))

# استيراد المكونات من Agent
try:
    from Agent.font_manager import AdvancedFontManager
    from Agent.text_processor import AdvancedTextProcessor
    from Agent.search_engine import TavilySearchEngine
    print("✅ تم تحميل جميع المكونات بنجاح")
except ImportError as e:
    print(f"❌ خطأ في تحميل المكونات: {e}")
    sys.exit(1)

class InteractiveModel:
    """واجهة تفاعلية للنموذج"""
    
    def __init__(self):
        """تهيئة الواجهة التفاعلية"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # تحميل المكونات
        self.font_manager = None
        self.text_processor = None
        self.search_engine = None
        
        self.load_components()
        
    def setup_logging(self):
        """إعداد نظام التسجيل"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('interactive_model.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
    def load_components(self):
        """تحميل مكونات النظام"""
        try:
            # تحميل مدير الخط
            font_file = "font/uthmanic_hafs_v20.ttf"
            if os.path.exists(font_file):
                self.font_manager = AdvancedFontManager(font_file, logger=self.logger)
                print("✅ تم تحميل مدير الخط")
            else:
                print(f"⚠️ ملف الخط غير موجود: {font_file}")
                
            # تحميل معالج النصوص
            self.text_processor = AdvancedTextProcessor(
                font_manager=self.font_manager, 
                logger=self.logger
            )
            print("✅ تم تحميل معالج النصوص")
            
            # تحميل محرك البحث
            try:
                # التحقق من وجود المفتاح
                tavily_key = os.getenv('TAVILY_API_KEY')
                if tavily_key:
                    print(f"🔑 تم العثور على مفتاح Tavily: {tavily_key[:10]}...")
                    self.search_engine = TavilySearchEngine(api_key=tavily_key, logger=self.logger)
                    print("✅ تم تحميل محرك البحث")
                else:
                    print("❌ مفتاح TAVILY_API_KEY غير موجود في متغيرات البيئة")
                    self.search_engine = None
            except ValueError as e:
                print(f"⚠️ محرك البحث غير متاح: {e}")
                self.search_engine = None
            except Exception as e:
                print(f"❌ خطأ في تحميل محرك البحث: {e}")
                self.search_engine = None
                
        except Exception as e:
            self.logger.error(f"خطأ في تحميل المكونات: {e}")
            
    def show_status(self):
        """عرض حالة النظام"""
        print("\n" + "="*60)
        print("🔍 حالة النظام")
        print("="*60)
        
        # حالة مدير الخط
        if self.font_manager:
            print(f"✅ مدير الخط: متاح ({len(self.font_manager.character_map)} حرف)")
        else:
            print("❌ مدير الخط: غير متاح")
            
        # حالة معالج النصوص
        if self.text_processor:
            print("✅ معالج النصوص: متاح")
        else:
            print("❌ معالج النصوص: غير متاح")
            
        # حالة محرك البحث
        if self.search_engine:
            print("✅ محرك البحث: متاح")
        else:
            print("❌ محرك البحث: غير متاح")
            
        # حالة الملفات
        files_status = {
            "ملف الخط": "font/uthmanic_hafs_v20.ttf",
            "بيانات حفص": "data/hafsData_v2-0.csv",
            "مجلد الصفحات": "pages_svgs",
            "مجلد التقارير": "reports"
        }

        print("\n📁 حالة الملفات:")
        for name, path in files_status.items():
            if os.path.exists(path):
                print(f"  ✅ {name}: موجود")
            else:
                print(f"  ❌ {name}: غير موجود")

        # حالة متغيرات البيئة
        print("\n🔑 متغيرات البيئة:")
        env_vars = ['TAVILY_API_KEY', 'GROQ_API_KEY']
        for var in env_vars:
            value = os.getenv(var)
            if value:
                print(f"  ✅ {var}: {value[:10]}...")
            else:
                print(f"  ❌ {var}: غير موجود")
                
    def test_font_manager(self):
        """اختبار مدير الخط"""
        if not self.font_manager:
            print("❌ مدير الخط غير متاح")
            return
            
        print("\n🔤 اختبار مدير الخط:")
        
        # اختبار نص عربي
        test_text = "بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ"
        analysis = self.font_manager.analyze_text_composition(test_text)
        
        print(f"  📝 النص: {test_text}")
        print(f"  📊 إجمالي الأحرف: {analysis['total_chars']}")
        print(f"  🔤 أحرف عربية: {analysis['arabic_chars']}")
        print(f"  🕌 رموز عثمانية: {analysis['uthmani_symbols']}")
        print(f"  ✨ تشكيل: {analysis['diacritics']}")
        
    def test_text_processor(self):
        """اختبار معالج النصوص"""
        if not self.text_processor:
            print("❌ معالج النصوص غير متاح")
            return
            
        print("\n📝 اختبار معالج النصوص:")
        
        # نصوص للاختبار
        text1 = "بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ ١"
        text2 = "بسم الله الرحمن الرحيم ١"
        
        # تطبيع النصوص
        normalized1 = self.text_processor.normalize_text(text1)
        normalized2 = self.text_processor.normalize_text(text2)
        
        # حساب التشابه
        similarity = self.text_processor.text_similarity(text1, text2)
        
        print(f"  📝 النص الأول: {text1}")
        print(f"  📝 النص الثاني: {text2}")
        print(f"  🔄 مطبع 1: {normalized1}")
        print(f"  🔄 مطبع 2: {normalized2}")
        print(f"  📊 التشابه: {similarity:.3f}")
        
        # استخراج أرقام الآيات
        verses = self.text_processor.extract_verse_numbers(text1)
        if verses:
            print(f"  🔢 أرقام الآيات: {[v['value'] for v in verses]}")
            
    def test_search_engine(self):
        """اختبار محرك البحث"""
        if not self.search_engine:
            print("❌ محرك البحث غير متاح")
            return
            
        print("\n🔍 اختبار محرك البحث:")
        
        try:
            # بحث تجريبي
            query = "القرآن الكريم تفسير"
            print(f"  🔍 البحث عن: {query}")
            
            results = self.search_engine.search(query, max_results=3)
            
            print(f"  📊 عدد النتائج: {results.total_results}")
            print(f"  ⏱️ وقت البحث: {results.search_time:.2f}s")
            
            if results.summary:
                print(f"  📝 الملخص: {results.summary[:100]}...")
                
            for i, result in enumerate(results.results[:2], 1):
                print(f"  {i}. {result.title[:50]}...")
                print(f"     🔗 {result.url}")
                
        except Exception as e:
            print(f"  ❌ خطأ في البحث: {e}")
            
    def run_main_extractor(self, pages_range="1 3"):
        """تشغيل المستخرج الرئيسي"""
        print(f"\n🚀 تشغيل المستخرج الرئيسي للصفحات {pages_range}:")
        
        try:
            pages = pages_range.split()
            cmd = [
                sys.executable,
                "ayat_extractor_main.py",
                "--pages", pages[0], pages[1],
                "--verbose",
                "--output", f"reports/test_interactive_{pages[0]}_{pages[1]}.json"
            ]
            
            print(f"  🔧 الأمر: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("  ✅ تم التشغيل بنجاح!")
                print(f"  📄 الإخراج: {result.stdout[:200]}...")
            else:
                print("  ❌ فشل في التشغيل!")
                print(f"  📄 الخطأ: {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            print("  ⏰ انتهت مهلة التشغيل")
        except Exception as e:
            print(f"  ❌ خطأ: {e}")
            
    def interactive_menu(self):
        """القائمة التفاعلية"""
        while True:
            print("\n" + "="*60)
            print("🤖 واجهة النموذج التفاعلية")
            print("="*60)
            print("1. عرض حالة النظام")
            print("2. اختبار مدير الخط")
            print("3. اختبار معالج النصوص")
            print("4. اختبار محرك البحث")
            print("5. تشغيل المستخرج الرئيسي")
            print("6. تشغيل اختبار شامل")
            print("0. خروج")
            print("-" * 60)
            
            try:
                choice = input("اختر رقم الخيار: ").strip()
                
                if choice == "0":
                    print("👋 وداعاً!")
                    break
                elif choice == "1":
                    self.show_status()
                elif choice == "2":
                    self.test_font_manager()
                elif choice == "3":
                    self.test_text_processor()
                elif choice == "4":
                    self.test_search_engine()
                elif choice == "5":
                    pages = input("أدخل نطاق الصفحات (مثال: 1 3): ").strip() or "1 3"
                    self.run_main_extractor(pages)
                elif choice == "6":
                    self.run_comprehensive_test()
                else:
                    print("❌ خيار غير صحيح!")
                    
            except KeyboardInterrupt:
                print("\n👋 تم الإنهاء بواسطة المستخدم")
                break
            except Exception as e:
                print(f"❌ خطأ: {e}")
                
    def run_comprehensive_test(self):
        """تشغيل اختبار شامل"""
        print("\n🧪 تشغيل اختبار شامل:")
        
        self.show_status()
        self.test_font_manager()
        self.test_text_processor()
        self.test_search_engine()
        
        print("\n✅ انتهى الاختبار الشامل!")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تشغيل الواجهة التفاعلية...")
    
    try:
        model = InteractiveModel()
        model.interactive_menu()
    except Exception as e:
        print(f"❌ خطأ في تشغيل الواجهة: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
