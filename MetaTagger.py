import customtkinter as ctk
from tkinter import filedialog, messagebox
import mutagen
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC, TRCK, APIC
from mutagen.mp4 import MP4, MP4Cover
import os
from pathlib import Path
from PIL import Image, ImageTk
import io
import shutil
import tempfile
import sys
import json

# 设置主题和外观模式
ctk.set_appearance_mode("dark")  # 可选: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # 可选主题: "blue", "green", "dark-blue"

def resource_path(relative_path):
    """获取资源文件的正确路径（支持开发和打包后）"""
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 语言文本定义
TEXTS = {
    "zh": {
        # 主窗口
        "window_title": "音乐元数据编辑器",
        "no_file": "未选择文件",
        "ready": "● 就绪",
        "loaded": "● 已加载",
        "load_failed": "● 加载失败",
        "save_success": "● 保存成功",
        "save_failed": "● 保存失败",
        
        # 封面区域
        "cover_hint": "📷\n点击或拖拽\n更换封面",
        "select_image": "选择图片",
        "clear_cover": "清除封面",
        "image_support": "支持 JPG、PNG 格式",
        "no_cover": "📷\n无封面",
        
        # 标签字段
        "title": "🎵 标题",
        "artist": "🎤 艺术家",
        "album": "💿 专辑",
        "genre": "🎸 流派",
        "date": "📅 年份",
        "track": "🔢 音轨号",
        
        # 按钮
        "browse": "浏览",
        "load_tags": "加载标签",
        "save": "保存修改",
        "save_as": "另存为",
        
        # 文件选择
        "select_audio": "选择音频文件",
        "audio_files": "音频文件",
        "mp3_files": "MP3文件",
        "flac_files": "FLAC文件",
        "m4a_files": "M4A文件",
        "all_files": "所有文件",
        "placeholder_audio": "选择音频文件...",
        
        # 图片选择
        "select_cover": "选择封面图片",
        "image_files": "图片文件",
        
        # 错误和提示
        "error": "错误",
        "load_tag_error": "加载标签失败: {}",
        "no_valid_file": "请先选择一个有效的音频文件",
        "cannot_read_format": "无法读取文件格式: {}",
        "no_file_open": "没有打开的文件",
        "cannot_load_image": "无法加载图片: {}",
        "save_success_msg": "标签已保存",
        "save_failed_msg": "保存失败: {}",
        "info": "提示",
        
        # 语言设置
        "language": "语言",
        "chinese": "中文",
        "english": "English"
    },
    "en": {
        # Main window
        "window_title": "MetaTagger - Music Metadata Editor",
        "no_file": "No file selected",
        "ready": "● Ready",
        "loaded": "● Loaded",
        "load_failed": "● Load Failed",
        "save_success": "● Saved",
        "save_failed": "● Save Failed",
        
        # Cover section
        "cover_hint": "📷\nClick or Drag\nto Change Cover",
        "select_image": "Select Image",
        "clear_cover": "Clear Cover",
        "image_support": "Supports JPG, PNG",
        "no_cover": "📷\nNo Cover",
        
        # Tag fields
        "title": "🎵 Title",
        "artist": "🎤 Artist",
        "album": "💿 Album",
        "genre": "🎸 Genre",
        "date": "📅 Date",
        "track": "🔢 Track",
        
        # Buttons
        "browse": "Browse",
        "load_tags": "Load Tags",
        "save": "Save",
        "save_as": "Save As",
        
        # File selection
        "select_audio": "Select Audio File",
        "audio_files": "Audio Files",
        "mp3_files": "MP3 Files",
        "flac_files": "FLAC Files",
        "m4a_files": "M4A Files",
        "all_files": "All Files",
        "placeholder_audio": "Select audio file...",
        
        # Image selection
        "select_cover": "Select Cover Image",
        "image_files": "Image Files",
        
        # Errors and messages
        "error": "Error",
        "load_tag_error": "Failed to load tags: {}",
        "no_valid_file": "Please select a valid audio file first",
        "cannot_read_format": "Cannot read file format: {}",
        "no_file_open": "No file opened",
        "cannot_load_image": "Cannot load image: {}",
        "save_success_msg": "Tags saved successfully",
        "save_failed_msg": "Save failed: {}",
        "info": "Information",
        
        # Language settings
        "language": "Language",
        "chinese": "中文",
        "english": "English"
    }
}

class ModernMusicTagEditor:
    def __init__(self):
        # 创建主窗口
        self.root = ctk.CTk()
        
        # 设置语言（默认英文）
        self.current_language = "en"
        
        self.root.title(TEXTS[self.current_language]["window_title"])
        self.root.geometry("1200x800")
        self.root.minsize(1200, 750)
        
        # 设置窗口图标（如果存在图标文件则设置）
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except:
                pass  # 如果图标设置失败，继续运行
        
        self.current_file = None
        self.cover_image_data = None
        self.has_existing_cover = False
        
        # 创建现代化界面
        self.create_modern_ui()
        
        # 绑定拖放文件（可选）
        self.setup_drag_drop()
        
        # 应用初始语言
        self.update_ui_language()
        
    def get_text(self, key):
        """获取当前语言的文本"""
        return TEXTS[self.current_language].get(key, key)
        
    def create_modern_ui(self):
        """创建Win11风格的现代化界面"""
        
        # 主容器
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ========== 顶部标题栏 ==========
        title_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        # 标题和语言选择在同一行
        left_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        left_frame.pack(side="left")
        
        self.title_label = ctk.CTkLabel(
            left_frame, 
            text="",  # 稍后设置
            font=ctk.CTkFont(family="Microsoft YaHei", size=24, weight="bold")
        )
        self.title_label.pack(side="left")
        
        # 语言切换按钮
        self.language_btn = ctk.CTkButton(
            title_frame,
            text="",
            command=self.toggle_language,
            width=100,
            height=30,
            corner_radius=8,
            font=ctk.CTkFont(family="Microsoft YaHei", size=12)
        )
        self.language_btn.pack(side="right", padx=10)
        
        # 文件信息标签
        self.file_info_label = ctk.CTkLabel(
            title_frame, 
            text="", 
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            text_color="gray70"
        )
        self.file_info_label.pack(side="right", padx=10)
        
        # ========== 主要内容区域 ==========
        content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # 左侧 - 封面图区域
        self.create_cover_section(content_frame)
        
        # 右侧 - 标签编辑区域
        self.create_tags_section(content_frame)
        
        # ========== 底部按钮栏 ==========
        self.create_bottom_bar()
        
    def create_cover_section(self, parent):
        """创建左侧封面图区域（类似Win11设置侧边栏）"""
        left_frame = ctk.CTkFrame(
            parent, 
            width=280,
            corner_radius=12,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        )
        left_frame.pack(side="left", fill="both", padx=(0, 20))
        left_frame.pack_propagate(False)
        
        # 封面图容器
        cover_container = ctk.CTkFrame(left_frame, fg_color="transparent")
        cover_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 封面预览
        self.cover_label = ctk.CTkLabel(
            cover_container,
            text="",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14),
            fg_color="gray25",
            corner_radius=12,
            width=240,
            height=240
        )
        self.cover_label.pack(pady=(0, 15))
        self.cover_label.bind("<Button-1>", lambda e: self.browse_cover())
        
        # 封面操作按钮
        cover_btn_frame = ctk.CTkFrame(cover_container, fg_color="transparent")
        cover_btn_frame.pack(fill="x")
        
        self.change_cover_btn = ctk.CTkButton(
            cover_btn_frame,
            text="",
            command=self.browse_cover,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13)
        )
        self.change_cover_btn.pack(side="left", padx=(0, 10), expand=True, fill="x")
        
        self.remove_cover_btn = ctk.CTkButton(
            cover_btn_frame,
            text="",
            command=self.clear_cover,
            height=35,
            corner_radius=8,
            fg_color="gray35",
            hover_color="gray45",
            font=ctk.CTkFont(family="Microsoft YaHei", size=13)
        )
        self.remove_cover_btn.pack(side="right", expand=True, fill="x")
        
        # 提示文字
        self.tip_label = ctk.CTkLabel(
            cover_container,
            text="",
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            text_color="gray60"
        )
        self.tip_label.pack(pady=(10, 0))
        
    def create_tags_section(self, parent):
        """创建右侧标签编辑区域（类似Win11设置详情页）"""
        right_frame = ctk.CTkFrame(
            parent,
            corner_radius=12,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        )
        right_frame.pack(side="right", fill="both", expand=True)
        
        # 滚动区域（标签较多时）
        scroll_frame = ctk.CTkScrollableFrame(right_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 文件选择卡片
        file_card = self.create_card(scroll_frame)
        file_card.pack(fill="x", pady=(0, 15))
        
        file_row = ctk.CTkFrame(file_card, fg_color="transparent")
        file_row.pack(fill="x", pady=10, padx=15)
        
        self.file_path_var = ctk.StringVar()
        self.file_entry = ctk.CTkEntry(
            file_row,
            textvariable=self.file_path_var,
            placeholder_text="",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(family="Microsoft YaHei", size=14)
        )
        self.file_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        self.browse_file_btn = ctk.CTkButton(
            file_row,
            text="",
            command=self.browse_file,
            width=80,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13)
        )
        self.browse_file_btn.pack(side="right")
        
        # 标签字段
        self.fields = [
            ("title", "title"),
            ("artist", "artist"),
            ("album", "album"),
            ("genre", "genre"),
            ("date", "date"),
            ("track", "track"),
        ]
        
        self.entries = {}
        self.field_labels = {}
        self.field_cards = []
        
        for field_key, entry_key in self.fields:
            card = self.create_card(scroll_frame)
            card.pack(fill="x", pady=(0, 12))
            self.field_cards.append((card, field_key, entry_key))
            
            label = ctk.CTkLabel(
                card,
                text="",
                font=ctk.CTkFont(family="Microsoft YaHei", size=13, weight="bold"),
                anchor="w"
            )
            label.pack(pady=(12, 8), padx=15)
            self.field_labels[field_key] = label
            
            entry = ctk.CTkEntry(
                card,
                height=40,
                corner_radius=8,
                font=ctk.CTkFont(family="Microsoft YaHei", size=14)
            )
            entry.pack(pady=(0, 12), padx=15, fill="x")
            self.entries[entry_key] = entry
        
        # 加载按钮
        load_card = self.create_card(scroll_frame)
        load_card.pack(fill="x", pady=(0, 0))
        
        self.load_btn = ctk.CTkButton(
            load_card,
            text="",
            command=self.load_tags,
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold")
        )
        self.load_btn.pack(pady=15, padx=15, fill="x")
        
    def create_card(self, parent):
        """创建带阴影效果的卡片容器"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=12,
            border_width=0,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        )
        # 添加微妙的边框效果
        card.configure(border_width=1, border_color="gray25")
        return card
    
    def create_bottom_bar(self):
        """创建底部操作栏（类似Win11应用栏）"""
        bottom_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(20, 0))
        
        # 分割线
        separator = ctk.CTkFrame(bottom_frame, height=1, fg_color="gray30")
        separator.pack(fill="x", pady=(0, 15))
        
        # 按钮容器
        btn_container = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        btn_container.pack(fill="x")
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            btn_container,
            text="",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            text_color="#107C10"
        )
        self.status_label.pack(side="left")
        
        # 右侧按钮组
        right_btns = ctk.CTkFrame(btn_container, fg_color="transparent")
        right_btns.pack(side="right")
        
        self.save_btn = ctk.CTkButton(
            right_btns,
            text="",
            command=self.save_tags,
            width=120,
            height=40,
            corner_radius=8,
            state="disabled",
            font=ctk.CTkFont(family="Microsoft YaHei", size=13, weight="bold")
        )
        self.save_btn.pack(side="left", padx=(0, 10))
        
        self.save_as_btn = ctk.CTkButton(
            right_btns,
            text="",
            command=self.save_as,
            width=100,
            height=40,
            corner_radius=8,
            state="disabled",
            fg_color="gray35",
            hover_color="gray45",
            font=ctk.CTkFont(family="Microsoft YaHei", size=13)
        )
        self.save_as_btn.pack(side="left")
        
    def update_ui_language(self):
        """更新整个界面的语言"""
        # 更新窗口标题
        self.root.title(self.get_text("window_title"))
        
        # 更新标题
        self.title_label.configure(text=self.get_text("window_title"))
        
        # 更新语言按钮文本
        if self.current_language == "zh":
            self.language_btn.configure(text="English")
        else:
            self.language_btn.configure(text="中文")
        
        # 更新文件信息
        self.file_info_label.configure(text=self.get_text("no_file"))
        
        # 更新封面区域
        if self.cover_image_data or self.has_existing_cover:
            # 如果有封面，保持图片，但更新提示文字
            pass
        else:
            self.cover_label.configure(text=self.get_text("cover_hint"))
        self.change_cover_btn.configure(text=self.get_text("select_image"))
        self.remove_cover_btn.configure(text=self.get_text("clear_cover"))
        self.tip_label.configure(text=self.get_text("image_support"))
        
        # 更新文件选择区域
        self.file_entry.configure(placeholder_text=self.get_text("placeholder_audio"))
        self.browse_file_btn.configure(text=self.get_text("browse"))
        
        # 更新标签字段
        field_texts = {
            "title": self.get_text("title"),
            "artist": self.get_text("artist"),
            "album": self.get_text("album"),
            "genre": self.get_text("genre"),
            "date": self.get_text("date"),
            "track": self.get_text("track")
        }
        for field_key, label in self.field_labels.items():
            label.configure(text=field_texts.get(field_key, field_key))
        
        # 更新加载按钮
        self.load_btn.configure(text=self.get_text("load_tags"))
        
        # 更新底部按钮
        self.save_btn.configure(text=self.get_text("save"))
        self.save_as_btn.configure(text=self.get_text("save_as"))
        
        # 更新状态栏
        current_status = self.status_label.cget("text")
        if "● 就绪" in current_status or "● Ready" in current_status:
            self.status_label.configure(text=self.get_text("ready"))
        elif "● 已加载" in current_status or "● Loaded" in current_status:
            self.status_label.configure(text=self.get_text("loaded"))
        elif "● 加载失败" in current_status or "● Load Failed" in current_status:
            self.status_label.configure(text=self.get_text("load_failed"))
        elif "● 保存成功" in current_status or "● Saved" in current_status:
            self.status_label.configure(text=self.get_text("save_success"))
        elif "● 保存失败" in current_status or "● Save Failed" in current_status:
            self.status_label.configure(text=self.get_text("save_failed"))
        
    def toggle_language(self):
        """切换语言"""
        if self.current_language == "zh":
            self.current_language = "en"
        else:
            self.current_language = "zh"
        self.update_ui_language()
        
    def setup_drag_drop(self):
        """设置拖放功能（需要额外库，这里提供框架）"""
        # 可以使用 tkinterdnd2 实现完整拖放
        pass
    
    def browse_file(self):
        """浏览并选择音频文件"""
        filetypes = [
            (self.get_text("audio_files"), "*.mp3 *.flac *.m4a *.ogg"),
            (self.get_text("mp3_files"), "*.mp3"),
            (self.get_text("flac_files"), "*.flac"),
            (self.get_text("m4a_files"), "*.m4a"),
            (self.get_text("all_files"), "*.*")
        ]
        filename = filedialog.askopenfilename(title=self.get_text("select_audio"), filetypes=filetypes)
        if filename:
            self.file_path_var.set(filename)
            self.current_file = filename
            self.update_file_info()
            self.load_tags()
    
    def update_file_info(self):
        """更新文件信息显示"""
        if self.current_file:
            name = Path(self.current_file).name
            size = os.path.getsize(self.current_file)
            if size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            self.file_info_label.configure(text=f"{name} • {size_str}")
    
    def browse_cover(self):
        """选择封面图片"""
        filetypes = [
            (self.get_text("image_files"), "*.jpg *.jpeg *.png"),
            (self.get_text("all_files"), "*.*")
        ]
        filename = filedialog.askopenfilename(title=self.get_text("select_cover"), filetypes=filetypes)
        if filename:
            self.load_cover_preview(filename)
    
    def load_cover_preview(self, image_path):
        """加载并显示封面预览"""
        try:
            # 使用PIL处理图片
            img = Image.open(image_path)
            # 调整图片大小适应预览区域
            img.thumbnail((240, 240), Image.Resampling.LANCZOS)
            
            # 转换为CTkImage
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(240, 240))
            self.cover_label.configure(image=ctk_img, text="")
            self.cover_image_data = image_path
            self.has_existing_cover = False
        except Exception as e:
            messagebox.showerror(self.get_text("error"), self.get_text("cannot_load_image").format(str(e)))
    
    def clear_cover(self):
        """清除封面"""
        self.cover_label.configure(image="", text=self.get_text("no_cover"))
        self.cover_image_data = None
        self.has_existing_cover = False
    
    def load_tags(self):
        """加载音频文件的标签"""
        file_path = self.file_path_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror(self.get_text("error"), self.get_text("no_valid_file"))
            return
        
        try:
            ext = Path(file_path).suffix.lower()
            audio = None
            
            # 根据格式加载
            if ext == '.mp3':
                try:
                    audio = EasyID3(file_path)
                except mutagen.id3.ID3NoHeaderError:
                    audio = MP3(file_path)
                    audio.add_tags()
            elif ext == '.flac':
                audio = FLAC(file_path)
            elif ext == '.m4a':
                audio = MP4(file_path)
            else:
                audio = mutagen.File(file_path, easy=True)
            
            if audio is None:
                messagebox.showerror(self.get_text("error"), self.get_text("cannot_read_format").format(ext))
                return
            
            # 填充标签字段
            tag_mapping = {
                'title': 'title', 'artist': 'artist', 'album': 'album',
                'genre': 'genre', 'date': 'date', 'tracknumber': 'track'
            }
            
            for tag_key, field_key in tag_mapping.items():
                if hasattr(audio, 'get') and tag_key in audio:
                    value = audio[tag_key][0] if isinstance(audio[tag_key], list) else audio[tag_key]
                    self.entries[field_key].delete(0, 'end')
                    self.entries[field_key].insert(0, str(value))
                else:
                    self.entries[field_key].delete(0, 'end')
            
            # 加载封面预览
            self.load_existing_cover(file_path, ext)
            
            # 启用保存按钮
            self.save_btn.configure(state="normal")
            self.save_as_btn.configure(state="normal")
            self.status_label.configure(text=self.get_text("loaded"), text_color="#107C10")
            
        except Exception as e:
            messagebox.showerror(self.get_text("error"), self.get_text("load_tag_error").format(str(e)))
            self.status_label.configure(text=self.get_text("load_failed"), text_color="#D83B01")
    
    def load_existing_cover(self, file_path, ext):
        """加载已有的封面图显示"""
        try:
            if ext == '.mp3':
                audio = ID3(file_path)
                for tag in audio.getall('APIC'):
                    img_data = tag.data
                    img = Image.open(io.BytesIO(img_data))
                    img.thumbnail((240, 240), Image.Resampling.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(240, 240))
                    self.cover_label.configure(image=ctk_img, text="")
                    self.has_existing_cover = True
                    return
            elif ext == '.flac':
                audio = FLAC(file_path)
                if audio.pictures:
                    pic = audio.pictures[0]
                    img = Image.open(io.BytesIO(pic.data))
                    img.thumbnail((240, 240), Image.Resampling.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(240, 240))
                    self.cover_label.configure(image=ctk_img, text="")
                    self.has_existing_cover = True
                    return
            elif ext == '.m4a':
                audio = MP4(file_path)
                if 'covr' in audio:
                    cover_data = audio['covr'][0]
                    img = Image.open(io.BytesIO(cover_data))
                    img.thumbnail((240, 240), Image.Resampling.LANCZOS)
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(240, 240))
                    self.cover_label.configure(image=ctk_img, text="")
                    self.has_existing_cover = True
                    return
            
            self.cover_label.configure(image="", text=self.get_text("no_cover"))
            self.has_existing_cover = False
        except:
            self.cover_label.configure(image="", text=self.get_text("no_cover"))
            self.has_existing_cover = False
    
    def save_tags(self):
        """保存标签到文件"""
        if not self.current_file:
            messagebox.showerror(self.get_text("error"), self.get_text("no_file_open"))
            return
        
        try:
            file_path = self.current_file
            ext = Path(file_path).suffix.lower()
            
            # 收集标签数据
            tags = {key: entry.get().strip() for key, entry in self.entries.items()}
            
            if ext == '.mp3':
                self.save_mp3_tags(file_path, tags)
            elif ext == '.flac':
                self.save_flac_tags(file_path, tags)
            elif ext == '.m4a':
                self.save_m4a_tags(file_path, tags)
            else:
                self.save_generic_tags(file_path, tags)
            
            self.status_label.configure(text=self.get_text("save_success"), text_color="#107C10")
            messagebox.showinfo(self.get_text("info"), self.get_text("save_success_msg"))
            
        except Exception as e:
            messagebox.showerror(self.get_text("error"), self.get_text("save_failed_msg").format(str(e)))
            self.status_label.configure(text=self.get_text("save_failed"), text_color="#D83B01")
    
    def save_mp3_tags(self, file_path, tags):
        """保存MP3标签"""
        try:
            audio = EasyID3(file_path)
        except:
            audio = MP3(file_path)
            audio.add_tags()
            audio = EasyID3(file_path)
        
        tag_mapping = {
            'title': 'title', 'artist': 'artist', 'album': 'album',
            'genre': 'genre', 'date': 'date', 'track': 'tracknumber'
        }
        
        for our_key, easy_key in tag_mapping.items():
            value = tags.get(our_key, "")
            if value:
                audio[easy_key] = value
            elif easy_key in audio:
                del audio[easy_key]
        
        audio.save()
        
        # 处理封面
        if self.cover_image_data:
            self.save_mp3_cover(file_path, self.cover_image_data)
        elif not self.has_existing_cover and self.cover_image_data is None:
            self.remove_mp3_cover(file_path)
    
    def save_mp3_cover(self, file_path, cover_path):
        """保存封面到MP3"""
        audio = ID3(file_path)
        audio.delall('APIC')
        
        with open(cover_path, 'rb') as f:
            cover_data = f.read()
        
        ext = Path(cover_path).suffix.lower()
        mime = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
        
        apic = APIC(encoding=3, mime=mime, type=3, desc='Cover', data=cover_data)
        audio.add(apic)
        audio.save()
    
    def remove_mp3_cover(self, file_path):
        """移除MP3封面"""
        audio = ID3(file_path)
        audio.delall('APIC')
        audio.save()
    
    def save_flac_tags(self, file_path, tags):
        """保存FLAC标签"""
        audio = FLAC(file_path)
        
        tag_mapping = {
            'title': 'title', 'artist': 'artist', 'album': 'album',
            'genre': 'genre', 'date': 'date', 'track': 'tracknumber'
        }
        
        for our_key, flac_key in tag_mapping.items():
            value = tags.get(our_key, "")
            if value:
                audio[flac_key] = value
            elif flac_key in audio:
                del audio[flac_key]
        
        # 处理封面
        if self.cover_image_data:
            from mutagen.flac import Picture
            pic = Picture()
            with open(self.cover_image_data, 'rb') as f:
                pic.data = f.read()
            ext = Path(self.cover_image_data).suffix.lower()
            pic.mime = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
            pic.type = 3
            audio.clear_pictures()
            audio.add_picture(pic)
        elif not self.has_existing_cover and self.cover_image_data is None:
            audio.clear_pictures()
        
        audio.save()
    
    def save_m4a_tags(self, file_path, tags):
        """保存M4A标签"""
        audio = MP4(file_path)
        
        tag_mapping = {
            'title': '\xa9nam', 'artist': '\xa9ART', 'album': '\xa9alb',
            'genre': '\xa9gen', 'date': '\xa9day', 'track': 'trkn'
        }
        
        for our_key, mp4_key in tag_mapping.items():
            value = tags.get(our_key, "")
            if value:
                if mp4_key == 'trkn':
                    audio[mp4_key] = [(int(value.split('/')[0]) if '/' in value else int(value), 0)]
                else:
                    audio[mp4_key] = value
            elif mp4_key in audio:
                del audio[mp4_key]
        
        # 处理封面
        if self.cover_image_data:
            with open(self.cover_image_data, 'rb') as f:
                cover_data = f.read()
            ext = Path(self.cover_image_data).suffix.lower()
            cover_format = MP4Cover.FORMAT_JPEG if ext in ['.jpg', '.jpeg'] else MP4Cover.FORMAT_PNG
            audio['covr'] = [MP4Cover(cover_data, cover_format)]
        elif not self.has_existing_cover and self.cover_image_data is None:
            if 'covr' in audio:
                del audio['covr']
        
        audio.save()
    
    def save_generic_tags(self, file_path, tags):
        """保存其他格式标签"""
        audio = mutagen.File(file_path, easy=True)
        if audio is None:
            raise ValueError("不支持的文件格式")
        
        tag_mapping = {
            'title': 'title', 'artist': 'artist', 'album': 'album',
            'genre': 'genre', 'date': 'date', 'track': 'tracknumber'
        }
        
        for our_key, easy_key in tag_mapping.items():
            value = tags.get(our_key, "")
            if value:
                audio[easy_key] = value
            elif easy_key in audio:
                del audio[easy_key]
        
        audio.save()
    
    def save_as(self):
        """另存为功能"""
        if not self.current_file:
            messagebox.showerror(self.get_text("error"), self.get_text("no_file_open"))
            return
        
        ext = Path(self.current_file).suffix
        save_path = filedialog.asksaveasfilename(
            title=self.get_text("save_as"),
            defaultextension=ext,
            filetypes=[(self.get_text("audio_files"), f"*{ext}"), (self.get_text("all_files"), "*.*")],
            initialfile=f"edited_{Path(self.current_file).name}"
        )
        
        if save_path:
            shutil.copy2(self.current_file, save_path)
            self.current_file = save_path
            self.file_path_var.set(save_path)
            self.update_file_info()
            self.save_tags()
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()


def main():
    app = ModernMusicTagEditor()
    app.run()


if __name__ == "__main__":
    main()