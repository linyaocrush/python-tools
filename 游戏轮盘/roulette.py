import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import webbrowser
from PIL import Image, ImageTk
import time
import json

class FolderRoulette:
    def __init__(self, root):
        self.root = root
        self.root.title("Steam游戏轮盘")
        self.root.geometry("700x600")
        self.root.configure(bg='#121212')
        
        # 配置文件和缓存文件路径
        self.config_file = "config.json"
        self.cache_file = "game_cache.txt"
        
        # 加载配置
        self.load_config()
        
        # 设置现代化样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 配置按钮样式
        self.style.configure('Modern.TButton', 
                           background='#1e88e5', 
                           foreground='white',
                           borderwidth=0,
                           focusthickness=0,
                           focuscolor='none',
                           font=('Helvetica', 11, 'bold'),
                           padding=10)
        self.style.map('Modern.TButton', 
                      background=[('active', '#1976d2'), ('disabled', '#4a4a4a')],
                      foreground=[('disabled', '#a0a0a0')])
        
        # 配置标签样式
        self.style.configure('Modern.TLabel', 
                           background='#121212', 
                           foreground='#e0e0e0',
                           font=('Helvetica', 11))
        
        # 配置框架样式
        self.style.configure('Modern.TFrame', 
                           background='#1e1e1e')
        
        # 配置标题标签
        self.style.configure('Title.TLabel', 
                           background='#121212', 
                           foreground='#64b5f6',
                           font=('Helvetica', 24, 'bold'))
        
        # 配置结果标签
        self.style.configure('Result.TLabel', 
                           background='#1e1e1e', 
                           foreground='#bb86fc',
                           font=('Helvetica', 18, 'bold'))
        
        self.folder_path = tk.StringVar()
        self.api_key = tk.StringVar()
        self.folders = []
        self.roulette_running = False
        self.selected_game = None
        
        self.create_widgets()
        
        # 设置默认值
        if not self.folder_path.get() and 'folder_path' in self.config:
            self.folder_path.set(self.config['folder_path'])
        if not self.api_key.get() and 'api_key' in self.config:
            self.api_key.set(self.config['api_key'])
    
    def load_config(self):
        """加载配置文件"""
        self.config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        # 初始化配置项
        self.folder_path = tk.StringVar(value=self.config.get('folder_path', ''))
        self.api_key = tk.StringVar(value=self.config.get('api_key', ''))
    
    def save_config(self):
        """保存配置文件"""
        self.config['folder_path'] = self.folder_path.get()
        self.config['api_key'] = self.api_key.get()
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def load_cache(self):
        """加载缓存文件"""
        self.cached_games = {}
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    i = 0
                    while i < len(lines):
                        folder_name = lines[i].strip()
                        if i + 1 < len(lines):
                            chinese_name = lines[i + 1].strip()
                            self.cached_games[folder_name] = chinese_name
                        i += 3  # 跳过空行
            except Exception as e:
                print(f"加载缓存文件失败: {e}")
    
    def save_cache(self):
        """保存缓存文件"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                for folder_name, chinese_name in self.cached_games.items():
                    f.write(f"{folder_name}\n{chinese_name}\n\n")
        except Exception as e:
            print(f"保存缓存文件失败: {e}")
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(main_frame, text="Steam游戏轮盘", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # 文件夹选择部分
        folder_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        folder_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(folder_frame, text="选择Steam游戏文件夹:", style='Modern.TLabel').pack(anchor=tk.W)
        
        folder_select_frame = ttk.Frame(folder_frame, style='Modern.TFrame')
        folder_select_frame.pack(fill=tk.X, pady=5)
        
        folder_entry = ttk.Entry(folder_select_frame, textvariable=self.folder_path, width=50)
        folder_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        browse_button = ttk.Button(folder_select_frame, text="浏览", command=self.browse_folder, style='Modern.TButton')
        browse_button.pack(side=tk.RIGHT)
        
        # API密钥部分
        api_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        api_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(api_frame, text="Steam API密钥:", style='Modern.TLabel').pack(anchor=tk.W)
        
        api_key_frame = ttk.Frame(api_frame, style='Modern.TFrame')
        api_key_frame.pack(fill=tk.X, pady=5)
        
        api_entry = ttk.Entry(api_key_frame, textvariable=self.api_key, width=50, show="*")
        api_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        api_button = ttk.Button(api_key_frame, text="获取API密钥", command=self.open_api_page, style='Modern.TButton')
        api_button.pack(side=tk.RIGHT)
        
        # 扫描按钮
        scan_button = ttk.Button(main_frame, text="扫描游戏", command=self.scan_folders, style='Modern.TButton')
        scan_button.pack(pady=15)
        
        # 游戏数量显示
        self.game_count_label = ttk.Label(main_frame, text="游戏数量: 0", style='Modern.TLabel')
        self.game_count_label.pack(pady=5)
        
        # 轮盘显示区域
        roulette_frame = ttk.Frame(main_frame, style='Modern.TFrame', relief='ridge', borderwidth=2)
        roulette_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self.result_label = ttk.Label(roulette_frame, 
                                    text="请选择文件夹并扫描", 
                                    style='Result.TLabel',
                                    anchor='center')
        self.result_label.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill=tk.X, pady=10)
        
        # 开始轮盘按钮
        self.start_button = ttk.Button(button_frame, text="开始轮盘", command=self.start_roulette, state=tk.DISABLED, style='Modern.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        # 停止轮盘按钮
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_roulette, state=tk.DISABLED, style='Modern.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        # 开始游戏按钮
        self.play_button = ttk.Button(button_frame, text="开始游戏", command=self.play_game, state=tk.DISABLED, style='Modern.TButton')
        self.play_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
    
    def open_api_page(self):
        webbrowser.open("https://steamcommunity.com/dev/apikey")
    
    def get_steam_game_name(self, app_id):
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=schinese"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data[str(app_id)]['success']:
                    name = data[str(app_id)]['data']['name']
                    if name:
                        return name
            else:
                print(f"请求失败，状态码: {response.status_code}")
        except requests.RequestException as e:
            print(f"请求异常: {e}")
        return None
    
    def scan_folders(self):
        path = self.folder_path.get()
        if not path:
            messagebox.showerror("错误", "请选择一个文件夹")
            return
        
        # 保存配置
        self.save_config()
        
        if not os.path.exists(path):
            messagebox.showerror("错误", "选择的文件夹不存在")
            return
        
        # 加载缓存
        self.load_cache()
        
        # 扫描第一层子文件夹并尝试获取Steam游戏名称
        game_folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        self.folders = []
        
        # 创建进度条窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("扫描进度")
        progress_window.geometry("350x120")
        progress_window.configure(bg='#1e1e1e')
        
        progress_label = tk.Label(progress_window, text="正在扫描游戏...", bg='#1e1e1e', fg='#e0e0e0', font=('Helvetica', 12))
        progress_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate')
        progress_bar.pack(pady=10)
        progress_bar['maximum'] = len(game_folders)
        
        for i, f in enumerate(game_folders):
            folder_path = os.path.join(path, f)
            if os.path.isdir(folder_path):
                # 检查缓存中是否有该游戏
                if f in self.cached_games:
                    game_name = self.cached_games[f]
                    self.folders.append(game_name)
                else:
                    appid_file = os.path.join(folder_path, "steam_appid.txt")
                    if os.path.exists(appid_file):
                        try:
                            with open(appid_file, 'r') as file:
                                app_id = file.read().strip()
                                game_name = self.get_steam_game_name(app_id)
                                if game_name:
                                    self.folders.append(game_name)
                                    # 添加到缓存
                                    self.cached_games[f] = game_name
                                else:
                                    self.folders.append(f)
                                    # 添加到缓存
                                    self.cached_games[f] = f
                        except Exception as e:
                            print(f"读取appid文件失败: {e}")
                            self.folders.append(f)
                            # 添加到缓存
                            self.cached_games[f] = f
                    else:
                        self.folders.append(f)
                        # 添加到缓存
                        self.cached_games[f] = f
            
            # 更新进度条
            progress_bar['value'] = i + 1
            progress_window.update()
        
        # 关闭进度条窗口
        progress_window.destroy()
        
        # 保存缓存
        self.save_cache()
        
        if not self.folders:
            messagebox.showwarning("警告", "该文件夹中没有Steam游戏")
            self.start_button.config(state=tk.DISABLED)
            return
        
        self.game_count_label.config(text=f"游戏数量: {len(self.folders)}")
        self.result_label.config(text="扫描完成，点击开始轮盘")
        self.start_button.config(state=tk.NORMAL)
    
    def start_roulette(self):
        if not self.folders or self.roulette_running:
            return
        
        self.roulette_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.roulette_effect()
    
    def stop_roulette(self):
        self.roulette_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.stop_roulette_effect()
    
    def roulette_effect(self):
        if not self.roulette_running:
            return
        
        # 随机选择一个游戏
        selected = random.choice(self.folders)
        
        # 创建科技感的渐变效果
        colors = ['#64b5f6', '#bb86fc', '#03dac6', '#ff7043', '#ffeb3b', '#ab47bc', '#42a5f5', '#26c6da']
        color = random.choice(colors)
        
        # 添加缩放效果
        font_sizes = [16, 17, 18, 19, 20]
        font_size = random.choice(font_sizes)
        
        self.result_label.config(text=selected, foreground=color, font=('Helvetica', font_size, 'bold'))
        
        # 随机延迟
        delay = random.uniform(0.05, 0.15)
        self.root.after(int(delay * 1000), self.roulette_effect)
    
    def stop_roulette_effect(self):
        if not self.folders:
            return
        
        # 最终选择
        selected = random.choice(self.folders)
        self.selected_game = selected
        
        # 显示最终选择的游戏，使用更突出的颜色
        self.result_label.config(text=f"选中的游戏: {selected}", foreground='#00e676', font=('Helvetica', 20, 'bold'))
        
        # 启用开始游戏按钮
        self.play_button.config(state=tk.NORMAL)
    
    def play_game(self):
        if not self.selected_game:
            messagebox.showerror("错误", "没有选中的游戏")
            return
        
        print(f"选中的游戏: {self.selected_game}")
        
        # 获取游戏文件夹路径
        path = self.folder_path.get()
        print(f"游戏文件夹路径: {path}")
        
        if not path:
            messagebox.showerror("错误", "请选择一个文件夹")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("错误", "选择的文件夹不存在")
            return
        
        # 标准化路径
        path = os.path.normpath(path)
        print(f"标准化后的游戏文件夹路径: {path}")
        
        game_folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        print(f"找到的游戏文件夹: {game_folders}")
        
        # 查找选中游戏对应的文件夹
        game_folder = None
        
        # 首先尝试通过Steam API获取的游戏名称匹配
        for folder in game_folders:
            folder_path = os.path.join(path, folder)
            folder_path = os.path.normpath(folder_path)
            appid_file = os.path.join(folder_path, "steam_appid.txt")
            appid_file = os.path.normpath(appid_file)
            
            if os.path.exists(appid_file):
                try:
                    with open(appid_file, 'r') as file:
                        app_id = file.read().strip()
                        print(f"文件夹 '{folder}' 中的appid: {app_id}")
                        
                        if app_id:
                            game_name = self.get_steam_game_name(app_id)
                            print(f"通过API获取的游戏名称: {game_name}")
                            
                            if game_name and game_name == self.selected_game:
                                game_folder = folder
                                print(f"通过API名称匹配成功: {game_folder}")
                                break
                except Exception as e:
                    print(f"读取appid文件失败: {e}")
            
            if not game_folder and folder == self.selected_game:
                game_folder = folder
                print(f"通过文件夹名匹配成功: {game_folder}")
                break
        
        if not game_folder:
            print("通过名称匹配失败，尝试通过文件夹名查找")
            for folder in game_folders:
                if folder == self.selected_game:
                    game_folder = folder
                    print(f"后备方案匹配成功: {game_folder}")
                    break
        
        if not game_folder:
            messagebox.showerror("错误", f"找不到选中游戏的文件夹: {self.selected_game}")
            print("查找游戏文件夹失败")
            return
        
        # 直接通过游戏文件夹路径启动游戏
        try:
            game_path = os.path.join(path, game_folder)
            game_path = os.path.normpath(game_path)
            print(f"尝试启动游戏路径: {game_path}")
            
            # 查找可执行文件
            exe_files = []
            for root, dirs, files in os.walk(game_path):
                for file in files:
                    if file.endswith('.exe') and not file.endswith('redistributable.exe') and not file.endswith('setup.exe'):
                        exe_files.append(os.path.join(root, file))
            
            if exe_files:
                exe_path = exe_files[0]
                print(f"找到可执行文件: {exe_path}")
                os.startfile(exe_path)
                print("游戏启动命令已发送")
            else:
                messagebox.showerror("错误", "找不到游戏的可执行文件")
                print("找不到可执行文件")
        except Exception as e:
            error_msg = f"无法启动游戏: {e}"
            messagebox.showerror("错误", error_msg)
            print(error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderRoulette(root)
    
    # 注册退出时的保存函数
    def on_closing():
        app.save_config()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()