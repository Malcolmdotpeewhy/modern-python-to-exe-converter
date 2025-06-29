# Example Python Scripts

This folder contains example Python scripts that you can use to test the Modern Python to EXE Converter.

## Available Examples

### 1. Hello World (`hello_world.py`)
**Type**: Console Application  
**Description**: A simple script that greets the user and asks for their name.  
**Best Settings**: 
- ✅ Single file
- ❌ No console window (keep console visible)
- ❌ Debug mode (optional)

**Use Case**: Perfect for testing basic conversion functionality.

---

### 2. Simple Calculator (`simple_calculator.py`)
**Type**: GUI Application  
**Description**: A basic calculator with a modern dark theme interface built using tkinter.  
**Best Settings**: 
- ✅ Single file
- ✅ No console window (hide console for GUI apps)
- ❌ Debug mode (optional)

**Features**:
- Basic arithmetic operations (+, -, ×, ÷)
- Clear, percentage, and sign change functions
- Modern dark theme design
- Keyboard-friendly interface

**Use Case**: Great for testing GUI application conversion and custom icons.

---

### 3. File Organizer (`file_organizer.py`)
**Type**: Console Utility  
**Description**: Organizes files in a directory by type (Images, Documents, Audio, Video, etc.).  
**Best Settings**: 
- ✅ Single file
- ❌ No console window (keep console visible)
- ❌ Debug mode (optional)

**Features**:
- Automatically categorizes files by extension
- Creates organized folder structure
- Handles duplicate file names
- Progress reporting with emojis
- Safe file operations with error handling

**Use Case**: Demonstrates file operations and real-world utility conversion.

---

## How to Use These Examples

### Testing Conversion
1. **Open the Converter**: Run the Modern Python to EXE Converter
2. **Add Example**: Click "Add Files" and select an example script
3. **Configure Settings**: Use the recommended settings above
4. **Choose Icon** (Optional): Create a custom icon in the Icon Manager
5. **Convert**: Click "Convert to EXE" and test the result

### Testing Different Scenarios

#### Console Applications
- Use `hello_world.py` or `file_organizer.py`
- Keep console window visible
- Test user input and output

#### GUI Applications  
- Use `simple_calculator.py`
- Hide console window for clean appearance
- Test with custom icons from Icon Manager

#### Batch Conversion
- Select multiple example files at once
- Test batch processing capabilities
- Compare different conversion settings

## Expected Results

### File Sizes (Approximate)
- **hello_world.exe**: ~25-30 MB
- **simple_calculator.exe**: ~25-30 MB  
- **file_organizer.exe**: ~25-30 MB

*Note: Size includes Python interpreter and all dependencies*

### Performance
- **Startup Time**: 1-3 seconds (normal for PyInstaller executables)
- **Memory Usage**: 20-50 MB depending on the application
- **Functionality**: Should match original Python script exactly

## Troubleshooting Examples

### Common Issues

#### Calculator Not Responding
- Ensure tkinter is available in your Python installation
- Try running the Python script first to test functionality

#### File Organizer Errors
- Test with a folder containing various file types
- Ensure write permissions in the target directory

#### Large Executable Size
- This is normal for PyInstaller conversions
- Use "Single file" option for easier distribution

### Testing Tips

1. **Run Python Script First**: Always test the Python version before conversion
2. **Use Test Directories**: Create test folders with sample files for file_organizer.py
3. **Try Different Icons**: Test the calculator with different custom icons
4. **Test on Different Systems**: Converted EXEs should work on similar Windows systems

## Creating Your Own Examples

### Best Practices for Test Scripts
- Include error handling
- Use clear user feedback  
- Test both console and GUI scenarios
- Include file operations if relevant
- Add comments explaining functionality

### Recommended Script Types
- **Simple utilities**: File processors, calculators, converters
- **GUI demos**: tkinter applications with modern interfaces
- **Data processors**: CSV readers, image processors, web scrapers
- **Games**: Simple pygame or tkinter games

---

**Happy Converting!** 🚀

*These examples are designed to showcase different aspects of Python to EXE conversion. Feel free to modify them or use them as templates for your own projects.*
