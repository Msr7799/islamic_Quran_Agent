#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🕌 محلل النصوص القرآنية المتقدم - ملف التشغيل البسيط
Advanced Quran Text Analyzer - Simple Launcher
"""

import sys
import subprocess
from pathlib import Path

def main():
    """تشغيل التطبيق مباشرة"""
    print("� محلل النصوص القرآنية المتقدم")
    print("🚀 بدء التشغيل...")
    
    try:
        # تشغيل التطبيق مباشرة
        subprocess.run([sys.executable, "gui/main_runner.py"], check=True)
        
    except subprocess.CalledProcessError:
        print("❌ خطأ في تشغيل التطبيق")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚡ تم إيقاف التطبيق")
        sys.exit(0)

if __name__ == "__main__":
    main()
