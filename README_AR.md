<div align="center">

<img src="gui/assets/ai_icon.png" alt="Islamic Quran Agent" width="120" height="120">

# كل النماذج المجانية من OpenRouter لديهم القدره للوصول للأنترنت عن طريق TRAVILY MCP ووصول الى قاعدة بيانات وفيره للقران الكريم ووصول الى uthmanic font وأمكانية إضافة MCP Servers
### Islamic Quran Agent

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![AI](https://img.shields.io/badge/AI_Powered-FF6B6B?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)]()
[![Version](https://img.shields.io/badge/Version-2.0.0-blue?style=flat-square)]()
[![Arabic Support](https://img.shields.io/badge/Arabic-100%25-success?style=flat-square)]()
[![GitHub](https://img.shields.io/badge/♥️%20GitHub-000?style=flat-square&logo=github&logoColor=white)](https://github.com/Msr7799/islamic_Quran_Agent)

[![Read in English](https://img.shields.io/badge/English-Read%20in%20English-0078a8?style=for-the-badge&logo=googletranslate&logoColor=white)](README.md)

</div>

---

## 📖 نظرة عامة | Overview

**وكيل القرآن الذكي** هو تطبيق ذكي مصمم خصيصاً لتحليل وفهم النصوص القرآنية باستخدام تقنيات الذكاء الاصطناعي المتقدمة. يوفر التطبيق واجهة مستخدم سهلة الاستخدام باللغة العربية مع دعم كامل للخط العثماني والتشكيل.

**Islamic Quran Agent** is an intelligent application designed specifically for analyzing and understanding Quranic texts using advanced artificial intelligence techniques. The application provides an easy-to-use Arabic interface with full support for Uthmanic script and diacritics.

---

## ✨ الميزات الرئيسية | Key Features

### 🎯 التحليل الذكي
- **تحليل دلالي متقدم** للآيات القرآنية
- **فهم السياق** وربط المعاني
- **استخراج المفاهيم** والموضوعات الرئيسية
- **تحليل إحصائي** شامل للنصوص

### 🖥️ واجهة المستخدم
- **تصميم عربي أصيل** مع دعم الاتجاه من اليمين لليسار
- **خط عثماني** أصلي للنصوص القرآنية  
- **واجهة تفاعلية** سهلة الاستخدام
- **دعم كامل** للتشكيل والرموز العثمانية

### 🤖 الذكاء الاصطناعي
- **تكامل مع نماذج AI** المتقدمة
- **محادثة تفاعلية** حول النصوص القرآنية
- **بحث ذكي** بالمعنى والسياق
- **تحليل متعدد المستويات**

---

## 🛠️ المتطلبات | Requirements

### النظام | System
- **Python 3.8+**
- **نظام التشغيل**: Windows, macOS, Linux
- **الذاكرة**: 4GB RAM (مُوصى بـ 8GB)
- **المساحة**: 2GB مساحة فارغة

### المكتبات الأساسية | Core Libraries
```
PyQt5==5.15.11          # واجهة المستخدم الرسومية
pandas==2.3.1           # تحليل البيانات  
numpy==2.2.6            # العمليات الرياضية
arabic-reshaper==3.0.0  # معالجة النصوص العربية
python-bidi==0.4.2      # دعم الاتجاه العربي
groq==0.30.0            # تكامل الذكاء الاصطناعي
```

---

## 📦 التثبيت | Installation

### 1. استنساخ المشروع | Clone Repository
```bash
git clone https://github.com/Msr7799/islamic_Quran_Agent
cd islamic_Quran_Agent
```

### 2. إنشاء بيئة افتراضية | Create Virtual Environment
```bash
python -m venv quran_agent_env
# Windows
quran_agent_env\Scripts\activate
# macOS/Linux  
source quran_agent_env/bin/activate
```

### 3. تثبيت المتطلبات | Install Requirements
```bash
pip install -r requirements.txt
```

### 4. تشغيل التطبيق | Run Application
```bash
python run.py
```

---

## 🚀 طريقة الاستخدام | Usage Guide

### البدء السريع | Quick Start

1. **تشغيل التطبيق**
   ```bash
   python run.py
   ```

2. **اختيار النموذج**
   - افتح قائمة "إعدادات النموذج"
   - اختر النموذج المناسب من القائمة

3. **بدء التحليل**
   - أدخل النص القرآني في المربع المخصص
   - اضغط على "تحليل" لبدء العملية

4. **استعراض النتائج**
   - اطلع على التحليل المفصل
   - احفظ النتائج للرجوع إليها لاحقاً

### الوظائف المتقدمة | Advanced Features

- **التحليل المتعمق**: استخدم خيارات التحليل المتقدمة
- **المقارنات**: قارن بين آيات مختلفة
- **الإحصائيات**: اطلع على الإحصائيات التفصيلية
- **التصدير**: احفظ النتائج بصيغ مختلفة

---

## 📁 هيكل المشروع | Project Structure

```
islamic_Quran_Agent/
│
├── 📂 gui/                     # واجهة المستخدم الرسومية
│   ├── 📂 Agent/              # وكيل الذكاء الاصطناعي
│   ├── 📂 assets/             # الصور والموارد
│   └── 📄 *.py                # ملفات الواجهة
│
├── 📂 Uthmanic_data/          # البيانات العثمانية
│   ├── 📄 hafs_smart.json     # نص القرآن بالرواية
│   └── 📄 *.csv, *.html       # ملفات البيانات
│
├── 📂 Uthmanic_font/          # الخطوط العثمانية
│   ├── 📄 *.ttf               # ملفات الخط
│   └── 📄 *.json              # إعدادات الخط
│
├── 📂 tools/                  # أدوات التطوير
├── 📂 old-extractors/         # أدوات الاستخراج القديمة
│
├── 📄 requirements.txt        # متطلبات المشروع
├── 📄 run.py                  # ملف التشغيل الرئيسي
└── 📄 README.md              # هذا الملف
```

---

## 🤝 المساهمة | Contributing

نرحب بمساهماتكم لتطوير المشروع! | We welcome your contributions!

### خطوات المساهمة | Contribution Steps

1. **Fork** المشروع
2. إنشاء **branch** جديد للميزة
   ```bash
   git checkout -b feature/new-feature
   ```
3. **Commit** التغييرات
   ```bash
   git commit -m "إضافة ميزة جديدة"
   ```
4. **Push** إلى البرنش
   ```bash
   git push origin feature/new-feature
   ```
5. إنشاء **Pull Request**

### إرشادات الكود | Code Guidelines
- اتبع معايير **PEP 8** للـ Python
- اكتب **تعليقات** واضحة باللغة العربية والإنجليزية
- أضف **اختبارات** للميزات الجديدة
- حافظ على **التوافقية** مع النسخ السابقة

---

## 📞 الدعم والتواصل | Support & Contact

### المشاكل والاقتراحات | Issues & Suggestions
- 🐛 **البلاغات**: [GitHub Issues](https://github.com/Msr7799/islamic_Quran_Agent/issues)
- 💡 **الاقتراحات**: [Feature Requests](https://github.com/Msr7799/islamic_Quran_Agent/issues/new)

### التواصل | Contact
- 📧 **البريد الإلكتروني**: [msr7799@example.com](mailto:msr7799@example.com)
- 💬 **المناقشات**: [GitHub Discussions](https://github.com/Msr7799/islamic_Quran_Agent/discussions)

---

## 📄 الترخيص | License

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 شكر وتقدير | Acknowledgments

- **القرآن الكريم** - المصدر الأساسي للبيانات
- **المجتمع المفتوح المصدر** - للأدوات والمكتبات المذهلة
- **مجتمع المطورين العرب** - للدعم والمساهمات
- **فريق العمل** - للجهود المبذولة في التطوير

---

<div align="center">

**⭐ إذا أعجبك المشروع، لا تنس إعطاؤه نجمة! | If you like this project, don't forget to give it a star!**

</div>