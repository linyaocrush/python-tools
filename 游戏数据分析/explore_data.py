import sys
sys.dont_write_bytecode = True

import requests
import json

# 这个脚本用于探索Steam API返回的数据结构

def explore_steam_data(api_key, steam_id):
    """探索Steam API返回的数据结构"""
    base_url = "http://api.steampowered.com"
    url = f"{base_url}/IPlayerService/GetOwnedGames/v1/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'include_appinfo': 1,
        'include_played_free_games': 1,
        'format': 'json'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'response' in data and 'games' in data['response']:
            games = data['response']['games']
            print("游戏数据结构示例（前3个游戏）：")
            for i, game in enumerate(games[:3]):
                print(f"\n游戏 {i+1}:")
                for key, value in game.items():
                    print(f"  {key}: {value}")
            
            print(f"\n\n总共获取到 {len(games)} 款游戏的数据")
            
            # 检查是否有额外的有用字段
            print("\n可用字段：")
            if games:
                for key in games[0].keys():
                    print(f"  - {key}")
            
            # 统计信息
            total_playtime = sum(game['playtime_forever'] for game in games)
            played_games = [game for game in games if game['playtime_forever'] > 0]
            
            print(f"\n统计信息：")
            print(f"  总游戏数: {len(games)}")
            print(f"  有游玩记录的游戏数: {len(played_games)}")
            print(f"  总游玩时长: {total_playtime // 60}小时{total_playtime % 60}分钟")
            
            return games
        else:
            print("未找到游戏数据")
            return []
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return []

if __name__ == "__main__":
    # 注意：需要替换为实际的API密钥和Steam ID
    API_KEY = "YOUR_API_KEY_HERE"  # 替换为你的实际API密钥
    STEAM_ID = "YOUR_STEAM_ID_HERE"  # 替换为你的实际Steam ID
    
    explore_steam_data(API_KEY, STEAM_ID)