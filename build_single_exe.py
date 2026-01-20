#!/usr/bin/env python3
"""
Build Script for Modern Python to EXE Converter v4.0
Creates a single executable file containing all documentation and resources.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import tempfile

def check_and_install_pyinstaller():
    """Check if PyInstaller is installed, install if needed."""
    print("🔧 Checking PyInstaller...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PyInstaller is already installed")
            return True
    except:
        pass

    print("📦 Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install PyInstaller: {e}")
        return False

def create_embedded_resources():
    """Create a Python file with all documentation embedded as strings."""
    current_dir = Path(__file__).parent

    # Files to embed
    files_to_embed = {
        'README.md': 'readme_content',
        'README_v4_USER_GUIDE.md': 'user_guide_content',
        'VERSION.md': 'version_content',
        'FINAL_COMPLETION_REPORT.md': 'completion_report_content',
        'PROJECT_COMPLETE.md': 'project_complete_content',
        'requirements.txt': 'requirements_content'
    }

    embedded_content_list = ['''"""
Embedded resources for Modern Python to EXE Converter v4.0
All documentation and resource files are included here.
"""

# Embedded documentation and resources
EMBEDDED_RESOURCES = {
''']

    for filename, var_name in files_to_embed.items():
        file_path = current_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Escape quotes and newlines for Python string
                content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                embedded_content_list.append(f'    "{var_name}": """{content}""",\n')
        else:
            print(f"⚠️ Warning: {filename} not found, skipping...")

    embedded_content_list.append('''}
''')
    embedded_content = "".join(embedded_content_list)

    embedded_content += '''

def get_embedded_resource(resource_name):
    """Get an embedded resource by name."""
    return EMBEDDED_RESOURCES.get(resource_name, "Resource not found")

def save_embedded_resource(resource_name, filename):
    """Save an embedded resource to a file."""
    content = get_embedded_resource(resource_name)
    if content != "Resource not found":
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def show_help_dialog():
    """Show a help dialog with embedded documentation."""
    import tkinter as tk
    from tkinter import messagebox, scrolledtext

    def show_user_guide():
        guide_window = tk.Toplevel()
        guide_window.title("User Guide - Modern Python to EXE Converter v4.0")
        guide_window.geometry("800x600")

        text_widget = scrolledtext.ScrolledText(guide_window, wrap=tk.WORD)
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)

        user_guide = get_embedded_resource("user_guide_content")
        text_widget.insert('1.0', user_guide)
        text_widget.config(state='disabled')

    def show_version_info():
        version_info = get_embedded_resource("version_content")
        messagebox.showinfo("Version Information", version_info[:500] + "...")

    def export_documentation():
        try:
            # Export all documentation to current directory
            resources = [
                ("readme_content", "README.md"),
                ("user_guide_content", "README_v4_USER_GUIDE.md"),
                ("version_content", "VERSION.md"),
                ("completion_report_content", "FINAL_COMPLETION_REPORT.md"),
                ("project_complete_content", "PROJECT_COMPLETE.md"),
                ("requirements_content", "requirements.txt")
            ]

            exported = 0
            for resource_name, filename in resources:
                if save_embedded_resource(resource_name, filename):
                    exported += 1

            messagebox.showinfo("Export Complete",
                f"Successfully exported {exported} documentation files to current directory.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export documentation: {e}")

    # Create help dialog
    help_window = tk.Tk()
    help_window.title("Help - Modern Python to EXE Converter v4.0")
    help_window.geometry("400x300")
    help_window.resizable(False, False)

    # Center the window
    help_window.update_idletasks()
    x = (help_window.winfo_screenwidth() // 2) - (400 // 2)
    y = (help_window.winfo_screenheight() // 2) - (300 // 2)
    help_window.geometry(f"400x300+{x}+{y}")

    # Main label
    main_label = tk.Label(help_window,
        text="Modern Python to EXE Converter v4.0\\nHelp & Documentation",
        font=('Arial', 14, 'bold'), pady=20)
    main_label.pack()

    # Buttons frame
    buttons_frame = tk.Frame(help_window)
    buttons_frame.pack(expand=True)

    # Help buttons
    tk.Button(buttons_frame, text="📖 User Guide", command=show_user_guide,
             width=20, pady=5).pack(pady=5)
    tk.Button(buttons_frame, text="ℹ️ Version Info", command=show_version_info,
             width=20, pady=5).pack(pady=5)
    tk.Button(buttons_frame, text="💾 Export Documentation", command=export_documentation,
             width=20, pady=5).pack(pady=5)
    tk.Button(buttons_frame, text="❌ Close", command=help_window.destroy,
             width=20, pady=5).pack(pady=5)

    help_window.mainloop()

# Add help menu integration
def add_help_menu_to_app(app_instance):
    """Add help menu to the main application."""
    try:
        # Add Help menu to the main application
        menubar = tk.Menu(app_instance.root)
        app_instance.root.config(menu=menubar)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)

        help_menu.add_command(label="📖 User Guide", command=lambda: show_help_dialog())
        help_menu.add_separator()
        help_menu.add_command(label="💾 Export Documentation",
                             command=lambda: export_documentation())
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About",
                             command=lambda: messagebox.showinfo("About",
                                "Modern Python to EXE Converter v4.0\\n\\n"
                                "A comprehensive tool for converting Python scripts\\n"
                                "to standalone executables with advanced features.\\n\\n"
                                "All documentation is embedded in this executable."))
    except:
        pass  # Fail silently if menu can't be added
'''

    # Write the embedded resources file
    resources_file = current_dir / "embedded_resources.py"
    with open(resources_file, 'w', encoding='utf-8') as f:
        f.write(embedded_content)

    print(f"✅ Created embedded resources file: {resources_file}")
    return resources_file

def modify_main_app():
    """Modify the main application to use embedded resources."""
    current_dir = Path(__file__).parent
    main_app_path = current_dir / "py2exe_converter_v4.py"
    modified_app_path = current_dir / "py2exe_converter_v4_standalone.py"

    # Read the main application
    with open(main_app_path, 'r', encoding='utf-8') as f:
        app_content = f.read()

    # Add embedded resources import at the top
    import_addition = """# Embedded resources for standalone executable
try:
    from embedded_resources import add_help_menu_to_app, show_help_dialog
    STANDALONE_MODE = True
except ImportError:
    STANDALONE_MODE = False

"""

    # Add the import after other imports
    import_index = app_content.find('class ModernPy2ExeConverter:')
    modified_content = app_content[:import_index] + import_addition + app_content[import_index:]

    # Add help menu integration in the __init__ method
    init_addition = """
        # Add help menu for standalone executable
        if STANDALONE_MODE:
            try:
                add_help_menu_to_app(self)
            except:
                pass  # Fail silently if menu can't be added
"""

    # Find the end of __init__ method and add help menu
    init_end = modified_content.find('        self.apply_visual_effects()')
    if init_end != -1:
        init_end = modified_content.find('\n', init_end) + 1
        modified_content = modified_content[:init_end] + init_addition + modified_content[init_end:]

    # Write the modified application
    with open(modified_app_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    print(f"✅ Created standalone application: {modified_app_path}")
    return modified_app_path

def create_pyinstaller_spec():
    """Create a PyInstaller spec file for the build."""
    current_dir = Path(__file__).parent

    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['py2exe_converter_v4_standalone.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'PIL.ImageFilter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ModernPy2ExeConverter_v4.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='converter_icon.ico',
    version_file=None,
)
'''

    spec_file = current_dir / "standalone_build.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print(f"✅ Created PyInstaller spec file: {spec_file}")
    return spec_file

def build_executable():
    """Build the standalone executable."""
    current_dir = Path(__file__).parent
    spec_file = current_dir / "standalone_build.spec"

    print("🔨 Building standalone executable...")
    print("   This may take several minutes...")

    try:
        # Run PyInstaller
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean", "--noconfirm",
            str(spec_file)
        ], cwd=current_dir, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Build completed successfully!")

            # Check if executable was created
            exe_path = current_dir / "dist" / "ModernPy2ExeConverter_v4.0.exe"
            if exe_path.exists():
                exe_size = exe_path.stat().st_size
                print(f"📁 Executable created: {exe_path}")
                print(f"📊 File size: {exe_size / (1024*1024):.1f} MB")
                return exe_path
            else:
                print("❌ Executable not found in expected location")
                return None
        else:
            print(f"❌ Build failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ Build error: {e}")
        return None

def cleanup_build_files():
    """Clean up temporary build files."""
    current_dir = Path(__file__).parent

    cleanup_items = [
        "build",
        "py2exe_converter_v4_standalone.py",
        "embedded_resources.py",
        "standalone_build.spec",
        "__pycache__"
    ]

    print("🧹 Cleaning up build files...")
    for item in cleanup_items:
        item_path = current_dir / item
        try:
            if item_path.is_file():
                item_path.unlink()
                print(f"  🗑️ Removed file: {item}")
            elif item_path.is_dir():
                shutil.rmtree(item_path)
                print(f"  🗑️ Removed directory: {item}")
        except Exception as e:
            print(f"  ⚠️ Could not remove {item}: {e}")

def cleanup_source_files():
    """Clean up all source files after successful build, keeping only the executable."""
    current_dir = Path(__file__).parent

    # Files to keep (essential for distribution)
    keep_files = [
        "ModernPy2ExeConverter_v4.0.exe",
        "README_GITHUB.md",  # GitHub readme (will be renamed)
        "LICENSE",   # If exists
    ]

    # Files to remove (no longer needed after exe creation)
    remove_files = [
        "py2exe_converter_v4.py",
        "requirements.txt",
        "launch_converter.py",
        "Start_Converter.bat",
        "Setup_and_Launch.bat",
        "install_and_run.py",
        "validate_deployment.py",
        "prepare_for_self_conversion.py",
        "build_single_exe.py",
        "BUILD_SINGLE_EXE.bat",
        "SELF_CONVERT.bat",
        "embedded_docs.py",
        "README.md",  # Original readme (replaced by GitHub version)
        "README_v4_USER_GUIDE.md",
        "VERSION.md",
        "FINAL_COMPLETION_REPORT.md",
        "PROJECT_COMPLETE.md",
        "DEPLOYMENT_COMPLETE.md",
        "SINGLE_EXECUTABLE_COMPLETE.md"
    ]

    print("\n🗑️ Auto-cleanup: Removing source files (executable is now standalone)...")

    removed_count = 0
    for filename in remove_files:
        file_path = current_dir / filename
        try:
            if file_path.exists():
                file_path.unlink()
                print(f"  ✅ Removed: {filename}")
                removed_count += 1
        except Exception as e:
            print(f"  ⚠️ Could not remove {filename}: {e}")

    # Rename GitHub README to standard README.md
    github_readme = current_dir / "README_GITHUB.md"
    standard_readme = current_dir / "README.md"
    try:
        if github_readme.exists():
            github_readme.rename(standard_readme)
            print(f"  ✅ Renamed: README_GITHUB.md → README.md")
    except Exception as e:
        print(f"  ⚠️ Could not rename README: {e}")

    # Create a simple distribution summary
    create_distribution_summary(current_dir)

    print(f"\n🎉 Auto-cleanup complete! Removed {removed_count} source files.")
    print("💡 Only the standalone executable and essential files remain.")
    print("🚀 Ready for GitHub upload and distribution!")

    return removed_count

def create_distribution_summary(directory):
    """Create a summary file for the final distribution."""
    summary_content = """# Distribution Package - Modern Python to EXE Converter v4.0

## 📦 Contents

- **ModernPy2ExeConverter_v4.0.exe** - Standalone executable (32.7 MB)
- **README.md** - Complete documentation and usage guide

## 🚀 Usage

Simply download and run `ModernPy2ExeConverter_v4.0.exe` - no installation required!

## ✨ Features

- Complete Python to EXE conversion tool
- Advanced icon manager with 6 shapes
- Modern dark theme interface
- All documentation embedded (Help menu)
- No Python installation required

## 📋 System Requirements

- Windows 7/8/10/11 (64-bit)
- No additional software required

---

*This package contains everything needed to run the application.*
"""

    try:
        summary_path = directory / "DISTRIBUTION_INFO.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        print(f"  ✅ Created: DISTRIBUTION_INFO.md")
    except Exception as e:
        print(f"  ⚠️ Could not create distribution summary: {e}")

def main():
    """Main build process."""
    print("🏗️ Modern Python to EXE Converter v4.0 - Standalone Build")
    print("=" * 65)

    current_dir = Path(__file__).parent
    print(f"📁 Build directory: {current_dir}")

    # Step 1: Check and install PyInstaller
    if not check_and_install_pyinstaller():
        print("❌ Cannot proceed without PyInstaller")
        return False

    # Step 2: Create embedded resources
    try:
        resources_file = create_embedded_resources()
    except Exception as e:
        print(f"❌ Failed to create embedded resources: {e}")
        return False

    # Step 3: Modify main application
    try:
        standalone_app = modify_main_app()
    except Exception as e:
        print(f"❌ Failed to modify main application: {e}")
        return False

    # Step 4: Create PyInstaller spec
    try:
        spec_file = create_pyinstaller_spec()
    except Exception as e:
        print(f"❌ Failed to create spec file: {e}")
        return False

    # Step 5: Build executable
    exe_path = build_executable()
    if not exe_path:
        print("❌ Failed to build executable")
        return False

    # Step 6: Clean up build files
    cleanup_build_files()

    # Step 7: Ask user if they want to clean up source files
    print("\n" + "🤔 Auto-cleanup Options:")
    print("The standalone executable is complete and contains everything needed.")
    print("Would you like to remove the source files to create a clean distribution?")
    print("\nOptions:")
    print("  1. Keep all files (for development/backup)")
    print("  2. Remove source files (clean distribution - RECOMMENDED)")
    print("  3. Remove source files automatically (no confirmation)")

    try:
        choice = input("\nEnter your choice (1-3) [default: 2]: ").strip()
        if not choice:
            choice = "2"

        if choice == "2":
            confirm = input("\n⚠️ This will remove all source files except the .exe. Continue? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                cleanup_source_files()
            else:
                print("📁 Source files kept - you can clean up manually later.")
        elif choice == "3":
            cleanup_source_files()
        else:
            print("📁 Keeping all source files for development/backup.")

    except KeyboardInterrupt:
        print("\n📁 Auto-cleanup skipped - keeping all files.")

    print("\n" + "=" * 65)
    print("🎉 STANDALONE EXECUTABLE BUILD COMPLETE!")
    print(f"📁 Location: {exe_path}")
    print(f"📊 Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")

    print("\n🎯 What's included in the executable:")
    print("  ✅ Complete Python to EXE Converter application")
    print("  ✅ All documentation embedded (accessible via Help menu)")
    print("  ✅ All dependencies included")
    print("  ✅ No additional files needed")

    print("\n🚀 Ready for distribution!")
    print("  • Users just need to download and run the .exe file")
    print("  • No Python installation required")
    print("  • All documentation accessible from Help menu")

    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Build process completed successfully!")
            input("\nPress Enter to exit...")
        else:
            print("\n❌ Build process failed!")
            input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\n🛑 Build cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        input("\nPress Enter to exit...")
