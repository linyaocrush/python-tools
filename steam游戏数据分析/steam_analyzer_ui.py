import sys
sys.dont_write_bytecode = True

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from steam_game_analyzer import SteamGameAnalyzer
import pandas as pd
import json
import os

# 设置样式
try:
    from tkinter import font
    import tkinter.ttk as ttk
except ImportError:
    pass

class SteamAnalyzerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Steam游戏分析器")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面元素
        self.create_widgets()
        
        # 加载保存的配置
        self.load_config()
        
    def setup_styles(self):
        """设置UI样式"""
        # 配置样式
        style = ttk.Style()
        
        # 设置主题（如果可用）
        try:
            style.theme_use('clam')
        except tk.TclError:
            try:
                style.theme_use('alt')
            except tk.TclError:
                pass  # 使用默认主题
        
        # 配置按钮样式
        style.configure('Accent.TButton', foreground='white', background='#3498db', font=('微软雅黑', 11, 'bold'))
        style.map('Accent.TButton', background=[('active', '#2980b9')])
        
        # 配置标签样式
        style.configure('Title.TLabel', font=('微软雅黑', 18, 'bold'), foreground='#2c3e50')
        style.configure('Section.TLabel', font=('微软雅黑', 12, 'bold'), foreground='#34495e')
        
        # 配置框架样式
        style.configure('Card.TFrame', background='#ffffff', relief='solid', borderwidth=1)
        style.configure('Result.TFrame', background='#ffffff', relief='solid', borderwidth=1)
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="Steam游戏分析器", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 25))
        
        # 输入区域框架
        input_frame = ttk.Frame(main_frame, padding="20", style='Card.TFrame')
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 25))
        input_frame.columnconfigure(1, weight=1)
        
        # API密钥输入
        api_label = ttk.Label(input_frame, text="Steam API密钥:", style='Section.TLabel')
        api_label.grid(row=0, column=0, sticky="w", padx=(0, 15), pady=10)
        self.api_key_entry = ttk.Entry(input_frame, width=50, show="*", font=('微软雅黑', 10))
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=10)
        
        # Steam ID输入
        steam_label = ttk.Label(input_frame, text="Steam ID:", style='Section.TLabel')
        steam_label.grid(row=1, column=0, sticky="w", padx=(0, 15), pady=10)
        self.steam_id_entry = ttk.Entry(input_frame, width=50, font=('微软雅黑', 10))
        self.steam_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 25))
        
        # 获取数据按钮
        self.fetch_button = ttk.Button(button_frame, text="获取游戏数据", command=self.fetch_data, style='Accent.TButton')
        self.fetch_button.pack(side="left", padx=10)
        
        # 生成图表按钮
        self.chart_button = ttk.Button(button_frame, text="生成分析图表", command=self.generate_charts, state="disabled", style='Accent.TButton')
        self.chart_button.pack(side="left", padx=10)
        
        # 保存配置按钮
        self.save_config_button = ttk.Button(button_frame, text="保存配置", command=self.save_config, style='Accent.TButton')
        self.save_config_button.pack(side="left", padx=10)
        
        # 结果显示区域
        result_label = ttk.Label(main_frame, text="游戏数据:", style='Section.TLabel')
        result_label.grid(row=3, column=0, sticky="w", pady=(0, 12))
        
        # 创建带滚动条的文本框
        text_frame = ttk.Frame(main_frame, style='Result.TFrame')
        text_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 12))
        main_frame.rowconfigure(4, weight=1)
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(text_frame, width=90, height=20, wrap=tk.WORD, font=('微软雅黑', 10), bg='#ffffff', fg='#2c3e50', padx=10, pady=10)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2, pady=2)
        
        # 添加垂直滚动条
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(0, 2), pady=2)
        self.result_text.configure(yscrollcommand=v_scrollbar.set)
        
        # 数据存储
        self.games_data = None
        self.df = None
        
    def save_config(self):
        """保存API密钥和Steam ID到配置文件"""
        api_key = self.api_key_entry.get().strip()
        steam_id = self.steam_id_entry.get().strip()
        
        # 如果输入为空，不保存
        if not api_key or not steam_id:
            messagebox.showerror("错误", "请填写API密钥和Steam ID后再保存配置")
            return
        
        config = {
            "api_key": api_key,
            "steam_id": steam_id
        }
        
        try:
            # 配置文件保存在项目根目录
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置时发生错误: {str(e)}")
            
    def load_config(self):
        """从配置文件加载API密钥和Steam ID"""
        try:
            # 配置文件保存在项目根目录
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # 填充输入框
                if "api_key" in config:
                    self.api_key_entry.insert(0, config["api_key"])
                if "steam_id" in config:
                    self.steam_id_entry.insert(0, config["steam_id"])
        except Exception as e:
            # 如果加载配置失败，不影响程序正常运行
            print(f"加载配置时发生错误: {str(e)}")
        
    def fetch_data(self):
        """获取游戏数据"""
        api_key = self.api_key_entry.get().strip()
        steam_id = self.steam_id_entry.get().strip()
        
        if not api_key or not steam_id:
            messagebox.showerror("错误", "请填写API密钥和Steam ID")
            return
        
        # 禁用按钮并显示加载状态
        self.fetch_button.config(state="disabled", text="获取中...")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "正在获取游戏数据，请稍候...\n")
        
        # 在新线程中执行数据获取
        threading.Thread(target=self._fetch_data_thread, args=(api_key, steam_id), daemon=True).start()
        
    def _fetch_data_thread(self, api_key, steam_id):
        """在后台线程中获取数据"""
        try:
            analyzer = SteamGameAnalyzer(api_key, steam_id)
            games = analyzer.get_owned_games()
            
            # 在主线程中更新UI
            self.root.after(0, self._update_ui_after_fetch, games)
        except Exception as e:
            self.root.after(0, self._handle_fetch_error, str(e))
            
    def _update_ui_after_fetch(self, games):
        """获取数据后的UI更新"""
        self.fetch_button.config(state="normal", text="获取游戏数据")
        
        if not games:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "未能获取到游戏数据，请检查API密钥和Steam ID是否正确。\n")
            return
            
        self.games_data = games
        # 传递API密钥和Steam ID以确保功能完整
        api_key = self.api_key_entry.get().strip()
        steam_id = self.steam_id_entry.get().strip()
        analyzer = SteamGameAnalyzer(api_key, steam_id)
        self.df = analyzer.display_games_table(games)
        
        # 显示结果
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"成功获取到 {len(games)} 款游戏的数据\n\n")
        
        # 显示表格数据
        if self.df is not None and not self.df.empty:
            for index, row in self.df.iterrows():
                self.result_text.insert(tk.END, f"{row['游戏名称']} - {row['游玩时长']}\n")
            
            # 启用生成图表按钮
            self.chart_button.config(state="normal")
        else:
            self.result_text.insert(tk.END, "没有游戏数据可显示\n")
            
    def _handle_fetch_error(self, error_message):
        """处理获取数据时的错误"""
        self.fetch_button.config(state="normal", text="获取游戏数据")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"获取数据时发生错误: {error_message}\n")
        
    def generate_charts(self):
        """生成分析图表"""
        if self.df is None or self.df.empty:
            messagebox.showerror("错误", "没有数据可生成图表")
            return
            
        try:
            # 禁用按钮并显示加载状态
            self.chart_button.config(state="disabled", text="生成中...")
            
            # 在新线程中生成图表
            threading.Thread(target=self._generate_charts_thread, daemon=True).start()
        except Exception as e:
            self.chart_button.config(state="normal", text="生成分析图表")
            messagebox.showerror("错误", f"生成图表时发生错误: {str(e)}")
            
    def _generate_charts_thread(self):
        """在后台线程中生成图表"""
        try:
            # 传递API密钥和Steam ID以确保功能完整
            api_key = self.api_key_entry.get().strip()
            steam_id = self.steam_id_entry.get().strip()
            analyzer = SteamGameAnalyzer(api_key, steam_id)
            analyzer.generate_charts(self.df)
            
            # 在主线程中更新UI
            self.root.after(0, self._update_ui_after_charts)
        except Exception as e:
            self.root.after(0, self._handle_chart_error, str(e))
            
    def _update_ui_after_charts(self):
        """生成图表后的UI更新"""
        self.chart_button.config(state="normal", text="生成分析图表")
        messagebox.showinfo("完成", "图表已生成并保存到文件中")
        
    def _handle_chart_error(self, error_message):
        """处理生成图表时的错误"""
        self.chart_button.config(state="normal", text="生成分析图表")
        messagebox.showerror("错误", f"生成图表时发生错误: {error_message}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteamAnalyzerUI(root)
    root.mainloop()