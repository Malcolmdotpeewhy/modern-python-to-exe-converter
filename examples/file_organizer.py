"""
File Organizer Example
A utility script that organizes files in a directory by type.
Demonstrates file operations and user interaction.
"""

import os
import shutil
from pathlib import Path

def organize_files(directory_path):
    """Organize files in a directory by their extensions."""
    
    # Create a Path object
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"❌ Directory '{directory_path}' does not exist!")
        return False
    
    if not directory.is_dir():
        print(f"❌ '{directory_path}' is not a directory!")
        return False
    
    # File type categories
    file_types = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
        'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods', '.numbers'],
        'Presentations': ['.ppt', '.pptx', '.odp', '.key'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        'Video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb'],
        'Executables': ['.exe', '.msi', '.deb', '.dmg', '.app']
    }
    
    # Count organized files
    organized_count = 0
    created_folders = []
    
    print(f"📁 Organizing files in: {directory}")
    print("=" * 50)
    
    # Process each file
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_extension = file_path.suffix.lower()
            file_moved = False
            
            # Find the appropriate category
            for category, extensions in file_types.items():
                if file_extension in extensions:
                    # Create category folder if it doesn't exist
                    category_folder = directory / category
                    if not category_folder.exists():
                        category_folder.mkdir()
                        created_folders.append(category)
                        print(f"📂 Created folder: {category}")
                    
                    # Move the file
                    try:
                        new_path = category_folder / file_path.name
                        # Handle duplicate names
                        counter = 1
                        while new_path.exists():
                            name_parts = file_path.stem, counter, file_path.suffix
                            new_name = f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                            new_path = category_folder / new_name
                            counter += 1
                        
                        shutil.move(str(file_path), str(new_path))
                        print(f"📄 Moved: {file_path.name} → {category}/")
                        organized_count += 1
                        file_moved = True
                        break
                    except Exception as e:
                        print(f"❌ Error moving {file_path.name}: {e}")
            
            # Handle unknown file types
            if not file_moved and file_extension:
                other_folder = directory / "Other"
                if not other_folder.exists():
                    other_folder.mkdir()
                    if "Other" not in created_folders:
                        created_folders.append("Other")
                        print(f"📂 Created folder: Other")
                
                try:
                    new_path = other_folder / file_path.name
                    counter = 1
                    while new_path.exists():
                        name_parts = file_path.stem, counter, file_path.suffix
                        new_name = f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                        new_path = other_folder / new_name
                        counter += 1
                    
                    shutil.move(str(file_path), str(new_path))
                    print(f"📄 Moved: {file_path.name} → Other/")
                    organized_count += 1
                except Exception as e:
                    print(f"❌ Error moving {file_path.name}: {e}")
    
    print("=" * 50)
    print(f"✅ Organization complete!")
    print(f"📊 Files organized: {organized_count}")
    print(f"📂 Folders created: {len(created_folders)}")
    if created_folders:
        print(f"   Categories: {', '.join(created_folders)}")
    
    return True

def main():
    print("🗂️  File Organizer")
    print("Organize files in a directory by type")
    print("=" * 40)
    
    while True:
        # Get directory from user
        directory_path = input("Enter the directory path to organize (or 'quit' to exit): ").strip()
        
        if directory_path.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not directory_path:
            print("❌ Please enter a valid directory path.")
            continue
        
        # Expand user path (handles ~ on Unix systems)
        directory_path = os.path.expanduser(directory_path)
        
        # Confirm before organizing
        print(f"\n⚠️  This will organize all files in: {directory_path}")
        confirm = input("Continue? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            print()
            success = organize_files(directory_path)
            if success:
                print("\n🎉 Files organized successfully!")
            else:
                print("\n❌ Organization failed.")
        else:
            print("❌ Operation cancelled.")
        
        print("\n" + "─" * 40 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
