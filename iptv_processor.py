import urllib.request

# 这是一个持续维护的直播源发布页（如果它变了，你只需要改这一行链接）
SOURCE_URL = "https://raw.githubusercontent.com/你的源提供者/最新列表.m3u" 
OUTPUT_FILE = "hebei_iptv.m3u"
EPG_URL = "https://epg.zsdc.eu.org/t.xml.gz"

def process():
    try:
        # 1. 自动从源地址抓取最新列表
        req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
        
        # 2. 自动格式化和分类
        m3u = f'#EXTM3U x-tvg-url="{EPG_URL}"\n'
        for line in data.splitlines():
            if "," in line and "http" in line:
                name, url = line.split(',', 1)
                # 分类逻辑
                group = "央视频道" if "CCTV" in name else ("卫视频道" if "卫视" in name else "河北地方")
                m3u += f'#EXTINF:-1 group-title="{group}",{name}\n{url.strip()}\n'
        
        # 3. 自动覆盖更新到你的仓库
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(m3u)
    except Exception as e:
        print(f"更新失败: {e}")

if __name__ == "__main__":
    process()
