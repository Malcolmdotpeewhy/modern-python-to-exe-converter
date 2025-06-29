# Modern Python to EXE Converter v4.0

<div align="center">

![App Icon](converter_icon_64.png)

![Version](https://img.shields.io/badge/version-4.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.7+-orange)

**A comprehensive desktop application for converting Python scripts to standalone executables**

[Download Latest Release](../../releases/latest) | [Features](#features) | [Screenshots](#screenshots)

</div>

## 🚀 Quick Start

### Option 1: Download Standalone Executable (Recommended)
1. **Download**: Go to [Releases](../../releases/latest) and download `ModernPy2ExeConverter_v4.0_WithCustomIcon.exe` (32.6MB)
2. **Run**: Double-click the executable
3. **Convert**: Add your Python files and click "Convert to EXE"

**No Python installation required!** ✨

### Option 2: Run from Source
```bash
# Clone repository
git clone https://github.com/yourusername/modern-python-to-exe-converter.git
cd modern-python-to-exe-converter

# Install dependencies
pip install -r requirements.txt

# Run application
python py2exe_converter_v4.py
```

## ✨ Features

<div align="center">

| Feature | Description |
|---------|-------------|
| 🎨 **Modern Interface** | Dark theme with transparency effects and tabbed layout |
| 🔧 **Advanced Conversion** | Batch processing with real-time progress tracking |
| 🎯 **Icon Manager** | Create custom icons with 6 shapes (Circle, Square, Triangle, etc.) |
| ⚙️ **Settings & Themes** | 5 built-in themes + custom theme creation |
| 📊 **Smart Validation** | Automatic dependency detection and error checking |
| 🚀 **Self-Converting** | Application can convert itself to a standalone executable |

</div>

### 🎨 **Modern Interface**
- **Dark theme** with transparency effects
- **Tabbed layout**: Info, Converter, Icon Manager, Settings
- **5 built-in themes** + custom theme creation
- **Responsive design** with scrollable content

### 🔧 **Advanced Conversion**
- **Batch processing** - Convert multiple files at once
- **Real-time progress** tracking with detailed logging
- **Automatic dependency** detection
- **Flexible options** - Single file, no console, debug mode
- **Smart validation** before conversion

### 🎯 **Icon Manager**
- **6 icon shapes**: Square, Circle, Triangle, Hexagon, Star, Diamond
- **Multi-size generation** (16x16 to 256x256)
- **Real-time preview** with rounded corners
- **Icon browser** with visual search
- **Auto-selection** of newly created icons

### ⚙️ **Settings & Customization**
- **Desktop-default** directories for easy access
- **Persistent settings** across sessions
- **Window transparency** control (70%-100%)
- **Behavior customization** options
- **Complete theme system**

## 📖 User Guide

### Converting Python Scripts
1. **Add Files**: Click "Add Files" to select your Python scripts
2. **Set Output**: Choose output directory (defaults to Desktop)
3. **Configure Options**: 
   - ✅ Single file (recommended for distribution)
   - ✅ No console window (for GUI applications)
   - ✅ Debug mode (for troubleshooting)
4. **Select Icon** (optional): Browse existing or create new shaped icons
5. **Convert**: Click "Convert to EXE" and monitor progress

### Creating Custom Icons
1. Go to **Icon Manager** tab
2. **Browse** for source image (PNG, JPG, etc.)
3. **Select shape**: Square, Circle, Triangle, Hexagon, Star, or Diamond
4. **Preview** the result with rounded corners
5. **Create Icon** - automatically generates multi-size ICO file
6. **Auto-selection**: Created icons are automatically selected for conversion

### Customizing Themes
1. Open **Settings** tab
2. Choose from **5 built-in themes**:
   - Dark (default)
   - Light
   - Ocean Blue
   - Forest Green
   - Royal Purple
3. **Create custom theme** with your own colors
4. **Adjust transparency** (70%-100%)

## 🛠️ Building from Source

To create your own standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Run the build script
python build_single_exe.py

# Follow prompts for auto-cleanup
```

The build script will:
- Embed all documentation into the executable
- Add Help menu for accessing embedded docs
- Create a single file with custom icon
- Optionally clean up source files for distribution

## 📋 System Requirements

- **OS**: Windows 7/8/10/11 (64-bit)
- **Python**: 3.7+ (for source version)
- **RAM**: 256MB minimum
- **Disk Space**: 50MB free space

## 🔧 Technical Details

- **Platform**: Windows (64-bit)
- **Dependencies**: tkinter, PyInstaller, Pillow
- **Executable Size**: ~33MB (includes all dependencies)
- **Architecture**: Class-based with modern design patterns
- **GUI Framework**: tkinter with custom styling
- **Icon Processing**: Pillow for image manipulation
- **Conversion Engine**: PyInstaller with custom configurations

## 📝 What's New in v4.0

- ✨ **Complete rewrite** with modern architecture
- 🎨 **Enhanced UI** with dark theme and transparency
- 🔧 **Advanced icon manager** with 6 shapes
- ⚙️ **Comprehensive settings** with theme system
- 📊 **Real-time progress** tracking
- 🚀 **Self-conversion** capability
- 📚 **Embedded documentation** in standalone executable
- 🎯 **Custom application icon** with professional branding

## 📸 Screenshots

*Screenshots will be added soon showing the modern interface and features.*

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyInstaller** for Python to executable conversion
- **Pillow** for image processing and icon creation
- **tkinter** for the GUI framework
- **Python community** for inspiration and support

## 🔗 Links

- [Download Latest Release](../../releases/latest)
- [Report Issues](../../issues)
- [Feature Requests](../../issues/new?template=feature_request.md)

---

<div align="center">

**Made with ❤️ for the Python community**

⭐ Star this repository if you find it helpful!

[⬆ Back to Top](#modern-python-to-exe-converter-v40)

</div>
