import sys
sys.dont_write_bytecode = True

import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Steam API配置
class SteamGameAnalyzer:
    def __init__(self, api_key, steam_id):
        self.api_key = api_key
        self.steam_id = steam_id
        self.base_url = "http://api.steampowered.com"
    
    def get_owned_games(self):
        """获取用户拥有的游戏列表及游玩时间"""
        url = f"{self.base_url}/IPlayerService/GetOwnedGames/v1/"
        params = {
            'key': self.api_key,
            'steamid': self.steam_id,
            'include_appinfo': 1,
            'include_played_free_games': 1,
            'format': 'json'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'response' in data and 'games' in data['response']:
                return data['response']['games']
            else:
                print("未找到游戏数据")
                return []
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return []
    
    def get_player_summary(self):
        """获取玩家摘要信息，包括用户名"""
        # 检查API密钥是否为空
        if not self.api_key:
            print("错误: API密钥为空，请检查配置")
            return None
            
        url = f"{self.base_url}/ISteamUser/GetPlayerSummaries/v2/"
        params = {
            'key': self.api_key,
            'steamids': self.steam_id,
            'format': 'json'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'response' in data and 'players' in data['response'] and data['response']['players']:
                return data['response']['players'][0]
            else:
                print("未找到玩家信息")
                return None
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
    
    def format_playtime(self, minutes):
        """将分钟转换为小时格式，保留一位小数"""
        hours = minutes / 60
        return f"{hours:.1f}小时"
    
    def display_games_table(self, games):
        """以表格形式显示游戏信息"""
        if not games:
            print("没有游戏数据可显示")
            return
        
        # 创建DataFrame
        df = pd.DataFrame(games)
        
        # 选择需要的列
        df = df[['name', 'playtime_forever']]
        
        # 重命名列
        df.columns = ['游戏名称', '游玩时长(分钟)']
        
        # 添加以小时为单位的游玩时长列
        df['游玩时长(小时)'] = df['游玩时长(分钟)'] / 60
        df['游玩时长'] = df['游玩时长(分钟)'].apply(self.format_playtime)
        
        # 添加是否游玩过的标记
        df['是否游玩'] = df['游玩时长(分钟)'] > 0
        
        # 按游玩时长排序
        df = df.sort_values('游玩时长(小时)', ascending=False)
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        # 显示表格
        print("\n用户游戏库及游玩时长:")
        print(df.to_string(index=False))
        
        return df
    
    def generate_charts(self, df):
        """生成分析图表"""
        if df.empty:
            print("没有数据可生成图表")
            return
        
        # 获取玩家信息
        player_summary = self.get_player_summary()
        username = player_summary.get('personaname', '未知用户') if player_summary else '未知用户'
        
        # 设置中文字体和样式，使用多种字体确保兼容性
        plt.rcParams['axes.unicode_minus'] = False
        sns.set_style("whitegrid")
        
        # 检测系统并设置合适的字体
        import platform
        import matplotlib.font_manager as fm
        
        system = platform.system()
        if system == "Windows":
            chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'FangSong']
        elif system == "Darwin":  # macOS
            chinese_fonts = ['Arial Unicode MS', 'Heiti SC']
        else:  # Linux and others
            chinese_fonts = ['WenQuanYi Micro Hei', 'DejaVu Sans', 'Bitstream Vera Sans']
        
        # 检查可用字体并设置
        available_fonts = set(f.name for f in fm.fontManager.ttflist)
        chinese_font = None
        
        for font in chinese_fonts:
            if font in available_fonts:
                chinese_font = font
                break
        
        # 如果找到了中文字体，则设置
        if chinese_font:
            plt.rcParams['font.sans-serif'] = [chinese_font]
        else:
            # 如果没有找到中文字体，尝试使用系统中的任何字体
            plt.rcParams['font.sans-serif'] = ['sans-serif']
        
        # 使用更现代的颜色调色板
        colors = sns.color_palette("viridis", 15)
        
        # 创建图表
        fig, axes = plt.subplots(3, 3, figsize=(24, 22))
        fig.suptitle(f'{username}的Steam游戏数据分析', fontsize=22, fontweight='bold', y=0.98)
        
        # 1. 游戏时长分布直方图
        # 使用动态bins
        max_hours = df['游玩时长(小时)'].max()
        if max_hours <= 10:
            # 对于较小的时长，使用更细的区间
            bins = [0, 1, 2, 5, 10]
        elif max_hours <= 20:
            # 中等时长范围
            bins = [0, 1, 5, 10, 15, 20]
        elif max_hours <= 50:
            # 中等时长范围
            bins = [0, 5, 10, 20, 30, 40, 50]
        elif max_hours <= 100:
            # 较大时长范围
            bins = [0, 10, 20, 30, 50, 75, 100]
        elif max_hours <= 300:
            # 更大的时长范围
            bins = [0, 20, 50, 100, 150, 200, 250, 300]
        else:
            # 很大的时长范围
            bins = [0, 50, 100, 200, 300, 500, 800, 1200]
        
        n, bins, patches = axes[0, 0].hist(df['游玩时长(小时)'], bins=bins, color=colors[0], edgecolor='white', linewidth=1.2, alpha=0.8)
        axes[0, 0].set_title('游戏时长分布', fontsize=16, fontweight='bold', pad=15)
        axes[0, 0].set_xlabel('游玩时长(小时)', fontsize=13)
        axes[0, 0].set_ylabel('游戏数量', fontsize=13)
        axes[0, 0].grid(True, alpha=0.4)
        
        # 添加统计信息
        mean_hours = df['游玩时长(小时)'].mean()
        median_hours = df['游玩时长(小时)'].median()
        std_hours = df['游玩时长(小时)'].std()
        axes[0, 0].axvline(mean_hours, color='#e74c3c', linestyle='--', linewidth=2, label=f'平均值: {mean_hours:.1f}小时')
        axes[0, 0].axvline(median_hours, color='#3498db', linestyle='-.', linewidth=2, label=f'中位数: {median_hours:.1f}小时')
        axes[0, 0].legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
        
        # 添加更多统计信息
        axes[0, 0].text(0.03, 0.97, f'标准差: {std_hours:.1f}小时', 
                       transform=axes[0, 0].transAxes, fontsize=11,
                       verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', alpha=0.9),
                       fontweight='bold')
        
        # 2. 游戏时长前10名条形图
        top_10 = df.head(10)
        bars = axes[0, 1].barh(top_10['游戏名称'], top_10['游玩时长(小时)'], color=colors[1], edgecolor='white', linewidth=0.7, alpha=0.9)
        axes[0, 1].set_title('游玩时长前10名游戏', fontsize=16, fontweight='bold', pad=15)
        axes[0, 1].set_xlabel('游玩时长(小时)', fontsize=13)
        axes[0, 1].grid(True, axis='x', alpha=0.4)
        
        # 在条形图上添加数值标签
        total_hours = df['游玩时长(小时)'].sum()
        total_games = len(df)
        for i, (bar, hours) in enumerate(zip(bars, top_10['游玩时长(小时)'])):
            percentage = (hours / total_hours) * 100
            axes[0, 1].text(bar.get_width() + max(top_10['游玩时长(小时)']) * 0.01, 
                           bar.get_y() + bar.get_height()/2, 
                           f'{hours:.1f}小时 ({percentage:.1f}%)', 
                           va='center', ha='left', fontsize=11, fontweight='bold', color='#2c3e50')
        
        # 添加总游戏数信息
        axes[0, 1].text(0.97, 0.97, f'总游戏数: {total_games}', 
                       transform=axes[0, 1].transAxes, fontsize=11,
                       verticalalignment='top', horizontalalignment='right',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', alpha=0.9),
                       fontweight='bold')
        
        # 3. 游戏时长饼图(前10名和其他)
        top_10_pie = df.head(10)
        others_time = df.iloc[10:]['游玩时长(小时)'].sum()
        
        pie_data = list(top_10_pie['游玩时长(小时)'])
        pie_labels = list(top_10_pie['游戏名称'])
        
        if others_time > 0:
            pie_data.append(others_time)
            pie_labels.append('其他游戏')
        
        wedges, texts, autotexts = axes[1, 0].pie(pie_data, labels=pie_labels, autopct='%1.1f%%', startangle=90, 
                      colors=colors[2:2+len(pie_data)], shadow=True, explode=[0.08]*len(pie_data),
                      textprops={'fontsize': 11, 'fontweight': 'bold'},
                      wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
        
        # 设置百分比标签样式
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        axes[1, 0].set_title('游戏时长占比(前10名及其它)', fontsize=16, fontweight='bold', pad=20)
        
        # 4. 累计游戏时长图
        df_sorted = df.sort_values('游玩时长(小时)', ascending=False).reset_index(drop=True)
        df_sorted['累计时长'] = df_sorted['游玩时长(小时)'].cumsum()
        
        axes[1, 1].plot(df_sorted.index, df_sorted['累计时长'], marker='o', markersize=5, 
                       linewidth=2.5, color=colors[3], markerfacecolor='#e74c3c', markeredgecolor='darkred',
                       alpha=0.8)
        axes[1, 1].set_title('累计游戏时长', fontsize=16, fontweight='bold', pad=20)
        axes[1, 1].set_xlabel('游戏排序', fontsize=13)
        axes[1, 1].set_ylabel('累计时长(小时)', fontsize=13)
        axes[1, 1].grid(True, alpha=0.4)
        
        # 添加统计信息
        total_hours = df['游玩时长(小时)'].sum()
        axes[1, 1].text(0.03, 0.97, f'总时长: {total_hours:.1f}小时', 
                       transform=axes[1, 1].transAxes, fontsize=11,
                       verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', alpha=0.9),
                       fontweight='bold')
        
        # 5. 未玩游戏与已玩游戏对比
        not_played = df[df['游玩时长(小时)'] == 0]
        played = df[df['游玩时长(小时)'] > 0]
        
        categories = ['未玩游戏', '已玩游戏']
        counts = [len(not_played), len(played)]
        bars = axes[1, 2].bar(categories, counts, color=[colors[4], colors[5]], edgecolor='white', linewidth=1.2, alpha=0.9)
        axes[1, 2].set_title('未玩游戏与已玩游戏对比', fontsize=16, fontweight='bold', pad=20)
        axes[1, 2].set_ylabel('游戏数量', fontsize=13)
        axes[1, 2].grid(True, axis='y', alpha=0.4)
        
        # 在条形图上添加数值标签
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            axes[1, 2].text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                           f'{count}', ha='center', va='bottom', fontsize=13, fontweight='bold', color='#2c3e50')
        
        # 添加百分比信息
        total_games = len(df)
        if total_games > 0:
            played_percentage = (len(played) / total_games) * 100
            axes[1, 2].text(0.97, 0.97, f'游玩率: {played_percentage:.1f}%', 
                           transform=axes[1, 2].transAxes, fontsize=11,
                           verticalalignment='top', horizontalalignment='right',
                           bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', alpha=0.9),
                           fontweight='bold')
        
        # 6. 游戏时长分组柱状图
        # 定义游戏时长分组
        def categorize_playtime(hours):
            if hours == 0:
                return '未游玩'
            elif hours < 10:
                return '1-10小时'
            elif hours < 50:
                return '10-50小时'
            elif hours < 100:
                return '50-100小时'
            elif hours < 500:
                return '100-500小时'
            else:
                return '500小时以上'
        
        df['时长分组'] = df['游玩时长(小时)'].apply(categorize_playtime)
        playtime_groups = df['时长分组'].value_counts()
        
        bars = axes[2, 0].bar(playtime_groups.index, playtime_groups.values, 
                             color=colors[6], edgecolor='white', linewidth=1.2, alpha=0.9)
        axes[2, 0].set_title('游戏时长分组', fontsize=16, fontweight='bold', pad=20)
        axes[2, 0].set_ylabel('游戏数量', fontsize=13)
        axes[2, 0].tick_params(axis='x', rotation=45)
        axes[2, 0].grid(True, axis='y', alpha=0.4)
        
        # 在条形图上添加数值标签
        for bar, count in zip(bars, playtime_groups.values):
            height = bar.get_height()
            axes[2, 0].text(bar.get_x() + bar.get_width()/2., height + max(playtime_groups.values)*0.01,
                           f'{count}', ha='center', va='bottom', fontsize=11, fontweight='bold', color='#2c3e50')
        
        # 添加统计信息
        axes[2, 0].text(0.97, 0.97, f'总游戏数: {total_games}', 
                       transform=axes[2, 0].transAxes, fontsize=11,
                       verticalalignment='top', horizontalalignment='right',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', alpha=0.9),
                       fontweight='bold')
        
        # 7. 游戏时长与排名关系图
        df_sorted_by_hours = df.sort_values('游玩时长(小时)', ascending=False).head(20).reset_index(drop=True)
        scatter = axes[2, 1].scatter(range(1, len(df_sorted_by_hours)+1), df_sorted_by_hours['游玩时长(小时)'], 
                          color=colors[7], s=120, alpha=0.8, edgecolors='white', linewidth=1.5)
        axes[2, 1].set_title('游戏时长与排名关系', fontsize=16, fontweight='bold', pad=20)
        axes[2, 1].set_xlabel('排名', fontsize=13)
        axes[2, 1].set_ylabel('游玩时长(小时)', fontsize=13)
        axes[2, 1].grid(True, alpha=0.4)
        
        # 添加趋势线
        x = range(1, len(df_sorted_by_hours)+1)
        y = df_sorted_by_hours['游玩时长(小时)']
        if len(x) > 1:
            import numpy as np
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            axes[2, 1].plot(x, p(x), "--", color='#e74c3c', linewidth=2.5, alpha=0.9)
        
        # 添加统计信息
        total_games = len(df)
        avg_hours = df['游玩时长(小时)'].mean()
        std_hours = df['游玩时长(小时)'].std()
        axes[2, 1].text(0.03, 0.97, f'总游戏数: {total_games}\n平均时长: {avg_hours:.1f}小时\n标准差: {std_hours:.1f}小时', 
                       transform=axes[2, 1].transAxes, fontsize=11,
                       verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', alpha=0.9),
                       fontweight='bold')
        
        # 8. 游戏发布年份分布图(模拟数据)
        # 注意：实际API不提供发布年份，这里使用模拟数据展示图表功能
        import random
        years = [random.randint(1990, 2024) for _ in range(len(df))]
        year_counts = {}
        for year in years:
            year_counts[year] = year_counts.get(year, 0) + 1
        
        sorted_years = sorted(year_counts.keys())
        counts = [year_counts[year] for year in sorted_years]
        
        bars = axes[2, 2].bar(sorted_years, counts, color=colors[8], edgecolor='white', linewidth=1.2, alpha=0.9)
        axes[2, 2].set_title('游戏发布年份分布(模拟)', fontsize=16, fontweight='bold', pad=20)
        axes[2, 2].set_xlabel('发布年份', fontsize=13)
        axes[2, 2].set_ylabel('游戏数量', fontsize=13)
        axes[2, 2].tick_params(axis='x', rotation=45)
        axes[2, 2].grid(True, axis='y', alpha=0.4)
        
        # 在条形图上添加数值标签
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            axes[2, 2].text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                           f'{count}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#2c3e50')
        
        # 添加统计信息
        axes[2, 2].text(0.97, 0.97, f'游戏总数: {len(df)}', 
                       transform=axes[2, 2].transAxes, fontsize=11,
                       verticalalignment='top', horizontalalignment='right',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', alpha=0.9),
                       fontweight='bold')
        
        # 9. 游戏时长与游玩状态关系图
        # 定义游玩状态
        def categorize_status(hours):
            if hours == 0:
                return '未开始'
            elif hours < 5:
                return '浅尝辄止'
            elif hours < 20:
                return '适度游玩'
            elif hours < 100:
                return '深度体验'
            else:
                return '核心玩家'
        
        df['游玩状态'] = df['游玩时长(小时)'].apply(categorize_status)
        status_counts = df['游玩状态'].value_counts()
        
        # 使用饼图展示
        wedges, texts, autotexts = axes[0, 2].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', 
                      startangle=90, colors=colors[9:9+len(status_counts)], 
                      shadow=True, explode=[0.08]*len(status_counts),
                      textprops={'fontsize': 11, 'fontweight': 'bold'},
                      wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
        
        # 设置百分比标签样式
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        axes[0, 2].set_title('游戏游玩分类占比', fontsize=16, fontweight='bold', pad=20)
        
        # 添加统计信息
        total_games = len(df)
        axes[0, 2].text(0, -1.3, f'总游戏数: {total_games}', 
                       ha='center', fontsize=12,
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='#ecf0f1', alpha=0.9),
                       fontweight='bold')
        
        # 调整布局
        plt.tight_layout(pad=2.5)
        fig.subplots_adjust(top=0.90, hspace=0.45, wspace=0.35, bottom=0.08)
        
        # 保存图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"steam_analysis_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"\n图表已保存为: {filename}")
        
        # 显示图表
        plt.show()
        
        # 关闭图表以释放资源
        plt.close(fig)
    
    def run_analysis(self):
        """运行完整分析"""
        print("正在获取Steam游戏数据...")
        games = self.get_owned_games()
        
        if not games:
            print("未能获取到游戏数据，请检查API密钥和Steam ID是否正确。")
            return
        
        print(f"成功获取到 {len(games)} 款游戏的数据")
        
        # 显示表格
        df = self.display_games_table(games)
        
        # 生成图表
        print("\n正在生成分析图表...")
        self.generate_charts(df)
        
        print("\n分析完成!")

if __name__ == "__main__":
    # 配置你的API密钥和Steam ID
    API_KEY = "YOUR_API_KEY_HERE"  # 替换为你的实际API密钥
    STEAM_ID = "YOUR_STEAM_ID_HERE"  # 替换为你的实际Steam ID
    
    # 创建分析器实例并运行分析
    analyzer = SteamGameAnalyzer(API_KEY, STEAM_ID)
    analyzer.run_analysis()