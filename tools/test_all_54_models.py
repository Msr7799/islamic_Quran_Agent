#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل لجميع نماذج OpenRouter الـ54
تحديد النماذج العاملة والمعطلة
"""

import sys
import os
import time
import json
from datetime import datetime

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model(manager, model_id, model_info):
    """اختبار نموذج واحد"""
    print(f"🧪 {model_id:<40} ", end='', flush=True)
    
    try:
        # تغيير النموذج
        manager.set_model(model_id)
        
        # إرسال رسالة بسيطة
        start_time = time.time()
        response = manager.get_response("مرحبا")
        response_time = time.time() - start_time
        
        if response and len(response.strip()) > 5:
            print(f"✅ يعمل ({response_time:.1f}s)")
            return {
                'status': 'working', 
                'model_id': model_id,
                'name': model_info['name'],
                'context': model_info['context'],
                'response_time': response_time,
                'response_preview': response.strip()[:50]
            }
        else:
            print("❌ لا يعطي رد")
            return {
                'status': 'no_response',
                'model_id': model_id, 
                'name': model_info['name'],
                'context': model_info['context']
            }
            
    except Exception as e:
        error_msg = str(e).lower()
        if "404" in error_msg or "not found" in error_msg:
            print("❌ غير متوفر")
            status = "not_available"
        elif "rate limit" in error_msg or "too many" in error_msg:
            print("⏱️ حد المعدل")
            status = "rate_limited"
        elif "timeout" in error_msg:
            print("⏰ انتهت المهلة")
            status = "timeout"
        else:
            print(f"💥 خطأ")
            status = "error"
            
        return {
            'status': status,
            'model_id': model_id,
            'name': model_info['name'], 
            'context': model_info['context'],
            'error': str(e)[:100]
        }

def main():
    """اختبار جميع النماذج"""
    print("🧪 اختبار شامل لجميع نماذج OpenRouter الـ54")
    print("=" * 80)
    
    try:
        from gui.Agent.openrouter_chat_manager import OpenRouterChatManager
        
        # إنشاء المدير
        manager = OpenRouterChatManager()
        models = manager.get_available_models()
        
        print(f"📋 سيتم اختبار {len(models)} نموذج")
        print(f"⏰ الوقت المتوقع: {len(models) * 5 / 60:.1f} دقيقة")
        print("-" * 80)
        
        results = []
        start_time = time.time()
        
        # اختبار كل نموذج
        for i, (model_id, model_info) in enumerate(models.items(), 1):
            print(f"[{i:2d}/{len(models)}] ", end='')
            
            result = test_model(manager, model_id, model_info)
            results.append(result)
            
            # تأخير قصير لتجنب حدود المعدل
            time.sleep(2)
            
            # إحصائيات مؤقتة كل 15 نموذج
            if i % 15 == 0:
                working = len([r for r in results if r['status'] == 'working'])
                print(f"\n📊 التقدم: {i}/{len(models)} | ✅ يعمل: {working} | 📈 معدل النجاح: {working/i*100:.1f}%")
                print("-" * 50)
        
        total_time = time.time() - start_time
        
        # تحليل النتائج
        working = [r for r in results if r['status'] == 'working']
        no_response = [r for r in results if r['status'] == 'no_response']
        not_available = [r for r in results if r['status'] == 'not_available']
        rate_limited = [r for r in results if r['status'] == 'rate_limited']
        timeouts = [r for r in results if r['status'] == 'timeout']
        errors = [r for r in results if r['status'] == 'error']
        
        # النتائج النهائية
        print("\n" + "=" * 80)
        print("📈 النتائج النهائية")
        print("=" * 80)
        
        print(f"⏰ إجمالي الوقت: {total_time/60:.1f} دقيقة")
        print(f"📊 إجمالي النماذج: {len(models)}")
        print(f"✅ النماذج العاملة: {len(working)} ({len(working)/len(models)*100:.1f}%)")
        print(f"❌ لا يعطي رد: {len(no_response)}")
        print(f"🚫 غير متوفر: {len(not_available)}")
        print(f"⏱️ حد المعدل: {len(rate_limited)}")
        print(f"⏰ انتهت المهلة: {len(timeouts)}")
        print(f"💥 أخطاء أخرى: {len(errors)}")
        
        # النماذج العاملة
        if working:
            print(f"\n🏆 النماذج العاملة ({len(working)}):")
            # ترتيب حسب سرعة الاستجابة
            working_sorted = sorted(working, key=lambda x: x['response_time'])
            
            for i, model in enumerate(working_sorted, 1):
                print(f"{i:2d}. {model['model_id']}")
                print(f"    📝 الاسم: {model['name']}")
                print(f"    🔢 السياق: {model['context']:,} tokens")
                print(f"    ⚡ السرعة: {model['response_time']:.1f} ثانية")
                print(f"    💬 مثال الرد: {model['response_preview']}...")
                print()
        
        # أفضل النماذج للاستخدام
        if working:
            print("💡 أفضل النماذج المقترحة:")
            best_models = working_sorted[:5]  # أسرع 5 نماذج
            for i, model in enumerate(best_models, 1):
                print(f"  {i}. {model['model_id']} ({model['response_time']:.1f}s)")
        
        # النماذج غير العاملة
        if not_available:
            print(f"\n🚫 النماذج غير المتوفرة ({len(not_available)}):")
            for model in not_available[:10]:  # أول 10 فقط
                print(f"  • {model['model_id']}")
        
        if rate_limited:
            print(f"\n⏱️ النماذج محدودة المعدل ({len(rate_limited)}):")
            for model in rate_limited[:5]:  # أول 5 فقط
                print(f"  • {model['model_id']}")
        
        # حفظ النتائج
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"openrouter_models_test_{timestamp}.json"
        
        final_results = {
            'timestamp': datetime.now().isoformat(),
            'total_time_minutes': round(total_time / 60, 2),
            'total_models': len(models),
            'summary': {
                'working': len(working),
                'no_response': len(no_response),
                'not_available': len(not_available),
                'rate_limited': len(rate_limited),
                'timeouts': len(timeouts),
                'errors': len(errors),
                'success_rate': round(len(working) / len(models) * 100, 2)
            },
            'working_models': working,
            'failed_models': {
                'no_response': no_response,
                'not_available': not_available,
                'rate_limited': rate_limited,
                'timeouts': timeouts,
                'errors': errors
            }
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ النتائج التفصيلية في: {results_file}")
        
        # إنشاء قائمة النماذج العاملة للمطورين
        if working:
            working_list_file = f"working_models_{timestamp}.txt"
            with open(working_list_file, 'w', encoding='utf-8') as f:
                f.write("# النماذج العاملة من OpenRouter\n")
                f.write(f"# تم الاختبار في: {datetime.now()}\n\n")
                for model in working_sorted:
                    f.write(f"{model['model_id']}\n")
            
            print(f"📝 تم حفظ قائمة النماذج العاملة في: {working_list_file}")
        
        print(f"\n🎉 انتهى الاختبار! وُجد {len(working)} نموذج عامل من أصل {len(models)}")
        
        return len(working) > 0
        
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ تم العثور على نماذج عاملة!")
    else:
        print("❌ لم يتم العثور على نماذج عاملة")