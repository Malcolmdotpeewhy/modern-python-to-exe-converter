# User Guide: Modern Python to EXE Converter v4.0

## Table of Contents
1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Converting Python Scripts](#converting-python-scripts)
4. [Creating Custom Icons](#creating-custom-icons)
5. [Customizing Themes](#customizing-themes)
6. [Advanced Settings](#advanced-settings)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### First Launch
When you first run the Modern Python to EXE Converter, you'll see a welcome screen with four main tabs:
- **Info**: Application information and quick start guide
- **Converter**: Main conversion functionality
- **Icon Manager**: Create and manage custom icons
- **Settings**: Customize appearance and behavior

### Quick Conversion
1. Go to the **Converter** tab
2. Click **"Add Files"** to select your Python scripts
3. Choose your output directory (defaults to Desktop/EXE)
4. Click **"Convert to EXE"**

## Interface Overview

### Info Tab
- Application version and build information
- Quick start instructions
- Feature highlights
- System requirements

### Converter Tab
- **File Selection**: Add single or multiple Python files
- **Output Directory**: Choose where to save your executables
- **Conversion Options**:
  - Single file (creates one executable)
  - No console window (for GUI applications)
  - Debug mode (for troubleshooting)
- **Icon Selection**: Choose or create custom icons
- **Progress Tracking**: Real-time conversion progress
- **Detailed Logging**: Color-coded status messages

### Icon Manager Tab
- **Source Image**: Browse for any image file (PNG, JPG, BMP, etc.)
- **Shape Selection**: Choose from 6 different shapes
- **Preview**: See your icon before creating it
- **Icon Browser**: Search and preview existing icon files
- **Batch Creation**: Create multiple icons at once

### Settings Tab
- **Theme Selection**: 5 built-in themes + custom themes
- **Appearance**: Window transparency, colors, fonts
- **Behavior**: Auto-select icons, notifications
- **Directories**: Default paths for output and icons

## Converting Python Scripts

### Basic Conversion
1. **Select Files**: Click "Add Files" and choose your .py files
2. **Output Location**: Select where to save the executable
3. **Options**: Configure conversion settings
4. **Convert**: Click "Convert to EXE" and wait for completion

### Conversion Options

#### Single File
- **Enabled**: Creates one standalone .exe file (recommended)
- **Disabled**: Creates an executable with supporting files

#### No Console Window
- **Enabled**: Hides the console window (for GUI applications)
- **Disabled**: Shows console window (useful for debugging)

#### Debug Mode
- **Enabled**: Includes debugging information and symbols
- **Disabled**: Optimized executable (smaller size)

### Best Practices
- Test your Python script before conversion
- Use virtual environments for complex projects
- Include all required files and dependencies
- Choose appropriate options based on your application type

## Creating Custom Icons

### Supported Image Formats
- PNG (recommended for transparency)
- JPG/JPEG
- BMP
- GIF
- TIFF

### Icon Shapes
1. **Square (Rounded)**: Traditional square icon with rounded corners
2. **Circle**: Perfect circular icon
3. **Triangle**: Modern triangular design
4. **Hexagon**: Professional hexagonal shape
5. **Star**: Eye-catching star shape
6. **Diamond**: Elegant diamond design

### Creating Icons
1. **Browse Image**: Select your source image
2. **Choose Shape**: Pick from 6 available shapes
3. **Preview**: See the result in real-time
4. **Create**: Click "Create Icon" to generate the ICO file
5. **Auto-Select**: The new icon is automatically selected for conversion

### Icon Tips
- Use high-resolution source images (512x512 or larger)
- PNG files with transparency work best
- Simple, bold designs work better at small sizes
- Icons are generated with multiple sizes (16x16 to 256x256)

## Customizing Themes

### Built-in Themes
1. **Dark** (Default): Professional dark theme
2. **Light**: Clean light theme
3. **Ocean Blue**: Calming blue tones
4. **Forest Green**: Natural green colors
5. **Royal Purple**: Elegant purple scheme

### Custom Themes
1. Go to the **Settings** tab
2. Click **"Create Custom Theme"**
3. Choose your colors:
   - Background color
   - Text color
   - Accent color
   - Button colors
4. Preview your changes in real-time
5. Save your custom theme

### Transparency
- Adjust window transparency from 70% to 100%
- Lower values create a more transparent window
- 100% is completely opaque (default)

## Advanced Settings

### Default Directories
- **EXE Output**: Where converted executables are saved
- **Icon Output**: Where created icons are saved
- Both default to Desktop subfolders for easy access

### Behavior Settings
- **Auto-select icons**: Automatically select newly created icons
- **Show notifications**: Display system notifications for completion
- **Validate before conversion**: Check files before starting conversion

### Performance Settings
- **Threading**: Background processing keeps UI responsive
- **Memory usage**: Optimized for low memory usage
- **Progress updates**: Real-time status information

## Troubleshooting

### Common Issues

#### "Python not found" Error
- Ensure Python is installed and in your system PATH
- Or use the standalone executable (no Python required)

#### Conversion Fails
- Check that your Python script runs correctly first
- Ensure all required modules are installed
- Try enabling Debug mode for more information

#### Large Executable Size
- This is normal - includes all dependencies
- Use "Single file" option for distribution
- Consider using virtual environments for smaller builds

#### Windows SmartScreen Warning
- Click "More info" then "Run anyway"
- This is normal for new/unsigned applications

#### Icon Creation Fails
- Ensure source image is accessible
- Try different image formats
- Check available disk space

### Getting Help
- Use the **Help** menu for embedded documentation
- Check the application logs for detailed error messages
- Visit our GitHub repository for community support
- Report bugs through GitHub Issues

### Performance Tips
- Close other applications during conversion
- Use SSD storage for faster processing
- Ensure adequate disk space (at least 100MB free)
- Keep source files on local drives (not network)

---

**For more help, visit our GitHub repository or check the embedded Help documentation.**
