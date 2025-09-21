<div align="center">

<img src="gui/assets/ai_icon.png" alt="Islamic Quran Agent" width="120" height="120">

# All OpenRouter free AI Agents have internet Access & have access to a big Quran Data & Quran Uthmanic Fonts and you can Add MCP servers to the application to get more data
### AI-Powered Quranic Text Analyzer

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![AI](https://img.shields.io/badge/AI_Powered-FF6B6B?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)]()
[![Version](https://img.shields.io/badge/Version-2.0.0-blue?style=flat-square)]()
[![Arabic Support](https://img.shields.io/badge/Arabic-100%25-success?style=flat-square)]()
[![GitHub](https://img.shields.io/badge/♥️%20GitHub-000?style=flat-square&logo=github&logoColor=white)](https://github.com/Msr7799/islamic_Quran_Agent)

[![Read in Arabic](https://img.shields.io/badge/Arabic-Read%20in%20Arabic-0078a8?style=for-the-badge&logo=googletranslate&logoColor=white)](README_AR.md)

</div>

---

## 📖 Overview

**Islamic Quran Agent** is an intelligent application designed specifically for analyzing and understanding Quranic texts using advanced artificial intelligence techniques. The application provides an easy-to-use Arabic interface with full support for Uthmanic script and diacritics, making it an invaluable tool for researchers, scholars, and anyone interested in deep Quranic analysis.

This powerful tool combines modern AI capabilities with traditional Islamic scholarship, offering comprehensive analysis while maintaining the sanctity and accuracy of the sacred text.

---

## ✨ Key Features

### 🎯 Intelligent Analysis
- **Advanced Semantic Analysis** of Quranic verses
- **Contextual Understanding** and meaning correlation
- **Concept Extraction** and key theme identification  
- **Comprehensive Statistical Analysis** of texts
- **Cross-referencing** between related verses

### 🖥️ User Interface
- **Authentic Arabic Design** with full RTL support
- **Original Uthmanic Script** for Quranic texts
- **Interactive Interface** with intuitive navigation
- **Complete Support** for diacritics and Uthmanic symbols
- **Responsive Layout** adaptable to different screen sizes

### 🤖 Artificial Intelligence
- **Integration with Advanced AI Models** for deep analysis
- **Interactive Conversations** about Quranic texts
- **Smart Search** by meaning and context
- **Multi-level Analysis** capabilities
- **Real-time Processing** and instant results

---

## 🛠️ Requirements

### System Requirements
- **Python 3.8+**
- **Operating System**: Windows, macOS, Linux
- **Memory**: 4GB RAM (8GB recommended)
- **Storage**: 2GB free space
- **Internet Connection**: Required for AI model access

### Core Libraries
```
PyQt5==5.15.11          # GUI Framework
pandas==2.3.1           # Data Analysis  
numpy==2.2.6            # Mathematical Operations
arabic-reshaper==3.0.0  # Arabic Text Processing
python-bidi==0.4.2      # Arabic Direction Support
groq==0.30.0            # AI Integration
```

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/Msr7799/islamic_Quran_Agent
cd islamic_Quran_Agent
```

### 2. Create Virtual Environment
```bash
python -m venv quran_agent_env

# Windows
quran_agent_env\Scripts\activate

# macOS/Linux  
source quran_agent_env/bin/activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
python run.py
```

---

## 🚀 Usage Guide

### Quick Start

1. **Launch the Application**
   ```bash
   python run.py
   ```

2. **Select AI Model**
   - Open "Model Settings" menu
   - Choose appropriate model from the list
   - Configure API settings if required

3. **Start Analysis**
   - Enter Quranic text in the designated input area
   - Click "Analyze" to begin the process
   - Wait for AI processing to complete

4. **Review Results**
   - Examine detailed analysis output
   - Save results for future reference
   - Export findings in various formats

### Advanced Features

- **Deep Analysis**: Use advanced analysis options for comprehensive insights
- **Verse Comparison**: Compare different verses and their meanings
- **Statistical Reports**: Access detailed statistical information
- **Export Options**: Save results in multiple formats (PDF, JSON, CSV)
- **Search History**: Access previously analyzed texts
- **Custom Queries**: Create specific analysis queries

---

## 📁 Project Structure

```
islamic_Quran_Agent/
│
├── 📂 gui/                     # Graphical User Interface
│   ├── 📂 Agent/              # AI Agent Components
│   │   ├── 📂 pages_svgs/     # SVG Resources
│   │   ├── 📄 ai_analyzer.py  # AI Analysis Engine
│   │   └── 📄 *.py            # Agent Modules
│   ├── 📂 assets/             # Images and Resources
│   │   ├── 📄 ai_icon.png     # Application Icon
│   │   └── 📄 *.png, *.svg    # UI Assets
│   └── 📄 *.py                # GUI Components
│
├── 📂 Uthmanic_data/          # Uthmanic Script Data
│   ├── 📄 hafs_smart.json     # Quran Text (Hafs Recitation)
│   ├── 📄 hafs_smart.csv      # Structured Data
│   └── 📄 *.html, *.xml       # Alternative Formats
│
├── 📂 Uthmanic_font/          # Uthmanic Fonts
│   ├── 📄 *.ttf               # Font Files
│   ├── 📄 *.json              # Font Configuration
│   └── 📄 *.pdf, *.docx       # Documentation
│
├── 📂 tools/                  # Development Tools
│   ├── 📄 test_all_54_models.py
│   └── 📄 *.md, *.txt         # Tool Documentation
│
├── 📂 old-extractors/         # Legacy Extraction Tools
│   └── 📄 *.py                # OCR and Text Extractors
│
├── 📄 requirements.txt        # Project Dependencies
├── 📄 run.py                  # Main Application Entry
├── 📄 mcp_servers_config.json # MCP Configuration
└── 📄 README.md              # This File
```

---

## 🤝 Contributing

We welcome contributions to improve the Islamic Quran Agent!

### How to Contribute

1. **Fork** the repository
2. Create a **feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```
3. **Commit** your changes
   ```bash
   git commit -m "Add new feature: description"
   ```
4. **Push** to the branch
   ```bash
   git push origin feature/new-feature
   ```
5. Create a **Pull Request**

### Development Guidelines
- Follow **PEP 8** standards for Python code
- Write **clear comments** and documentation
- Add **tests** for new features
- Maintain **backward compatibility**
- Respect the **Islamic context** of the application
- Ensure **accuracy** when dealing with Quranic text

### Code of Conduct
- Be respectful and considerate
- Focus on constructive feedback
- Maintain the sanctity of religious content
- Follow Islamic principles in development

---

## 📞 Support & Contact

### Issues & Suggestions
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Msr7799/islamic_Quran_Agent/issues)
- 💡 **Feature Requests**: [Feature Requests](https://github.com/Msr7799/islamic_Quran_Agent/issues/new)
- 📋 **Documentation**: [Wiki](https://github.com/Msr7799/islamic_Quran_Agent/wiki)

### Community
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Msr7799/islamic_Quran_Agent/discussions)
- 📧 **Email**: [msr7799@example.com](mailto:msr7799@example.com)
- 🌐 **Website**: [Project Homepage](https://github.com/Msr7799/islamic_Quran_Agent)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The Quranic text and Uthmanic script data used in this application are in the public domain and are used with respect for their sacred nature.

---

## 🙏 Acknowledgments

- **The Holy Quran** - The primary source of all data and inspiration
- **Islamic Scholars** - For their invaluable contributions to Quranic studies
- **Open Source Community** - For the amazing tools and libraries
- **Arabic Developer Community** - For support and contributions
- **AI Research Community** - For advancing natural language processing
- **Development Team** - For their dedication and hard work

### Special Thanks
- **Uthmanic Script Providers** - For preserving the authentic script
- **Recitation Sources** - For maintaining accuracy in pronunciation
- **Beta Testers** - For their valuable feedback and testing
- **Islamic Organizations** - For their guidance and support

---

## 🔄 Changelog

### Version 2.0.0 (Current)
- ✅ Complete GUI redesign with modern interface
- ✅ Advanced AI integration for deeper analysis
- ✅ Enhanced Arabic text processing
- ✅ Multi-model AI support
- ✅ Improved search and analysis capabilities

### Version 1.x
- ✅ Basic text analysis functionality
- ✅ Simple GUI interface
- ✅ Uthmanic script support
- ✅ Initial AI integration

---

## 🎯 Roadmap

### Upcoming Features
- 🔄 **Multi-language Support** - Additional language interfaces
- 🔄 **Mobile Application** - iOS and Android versions
- 🔄 **Cloud Synchronization** - Cross-device data sync
- 🔄 **Advanced Visualizations** - Interactive charts and graphs
- 🔄 **Audio Analysis** - Recitation analysis capabilities
- 🔄 **Collaborative Features** - Shared analysis and discussions

### Long-term Goals
- 🎯 **Educational Platform** - Comprehensive learning modules
- 🎯 **Research Tools** - Advanced academic research features
- 🎯 **API Development** - Public API for developers
- 🎯 **Plugin System** - Extensible architecture

---

<div align="center">

### Made with ❤️ for the Islamic Community
### Built to serve and honor the Holy Quran

**⭐ If you find this project helpful, please give it a star!**

**📚 "And We have made the Quran easy to understand and remember" - Quran 54:17**

</div>