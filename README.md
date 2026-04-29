# 🎵 Music Metadata Editor

A modern, cross-platform music metadata editor with Windows 11-style design, supporting multiple audio formats for tag editing and cover art management.

## ✨ Features

- 🎨 **Modern Interface** - Windows 11-style design with rounded corners and smooth animations
- 🌍 **Multi-language Support** - Supports Chinese and English interfaces with one-click switching
- 📝 **Complete Metadata Editing** - Title, artist, album, genre, date, track number
- 🖼️ **Cover Art Management** - Add, remove, and preview music cover art
- 💾 **Multiple Format Support** - MP3, FLAC, M4A, and other mainstream formats
- 🔧 **File Operations** - Save directly or save as a new file

## 📸 Screenshot

![Main Interface Preview](screenshot.png)

## 🚀 Quick Start

### System Requirements

- Python 3.7 or higher
- Windows / macOS / Linux

### Install Dependencies

```bash
pip install customtkinter mutagen Pillow
```

### Run the Application

```bash
python MetaTagger.py
```

### Package as EXE

Package as a standalone executable using PyInstaller:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="Music Metadata Editor" music_metadata_editor.py
```

## 📖 Usage Guide

1. Select File - Click the "Browse" button to choose an audio file
2. Load Tags - Click "Load Tags" to read existing metadata
3. Edit Information - Modify fields like title, artist, album, etc.
4. Manage Cover - Click the cover area to select an image, or use "Clear Cover" to remove
5. Save Changes - Click "Save" to write to the original file, or "Save As" to create a new file

### Supported File Formats

| Format | Tag Standard | Cover Support |
| --- | --- | --- |
| MP3 | ID3v2 | ✅ |
| FLAC | Vorbis Comments | ✅ |
| M4A | MP4 Metadata | ✅ |
| OGG | Vorbis Comments | ❌ |

## 🛠️ Tech Stack

- GUI Framework - CustomTkinter (Modern Tkinter extension)
- Metadata Processing - Mutagen (Audio metadata parsing library)
- Image Processing - Pillow (Cover image processing)
- Packaging Tool - PyInstaller
