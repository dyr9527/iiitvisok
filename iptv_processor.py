import re
from urllib.request import Request, urlopen

# 仅保留公网直连源，避开复杂的运营商私网聚合库
SOURCES = [
    "https://raw.githubusercontent.com/zhimly/iptv/main/tv.m3u",
    "https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.m3u"
]
OUTPUT_FILE = "hebei_iptv.m3u"
EPG_URL = "https://epg.zsdc.eu.org/t.xml.gz"

def is_clean_public_url(url):
    """核心过滤器：只保留没有鉴权参数、没有移动/电信专网特征的公网流"""
    # 过滤掉带有鉴权信息、移动/电信专网特征、IPv6 格式的链接
    forbidden = ["AuthInfo", "PLTV", "chinamobile", "chinaunicom", "chinatelecom", "112.25", "[2409", "192.168"]
    if any(f in url for f in forbidden):
        return False
    # 必须是 http 开头且包含 m3u8 扩展名
    return url.startswith("http") and ".m3u8" in url

def process():
    m3u = f'#EXTM3U x-tvg-url="{EPG_URL}"\n'
    seen_names = set()
    
    # 关键词列表
    keywords = ["CCTV", "卫视", "河北", "保定"]
    
    for url in SOURCES:
        try:
            content = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read().decode('utf-8')
            lines = content.splitlines()
            for i in range(len(lines) - 1):
                if "#EXTINF" in lines[i]:
                    name = lines[i].split(',')[-1]
                    url_line = lines[i+1].strip()
                    
                    # 只有频道命中关键词 且 地址是纯净公网的 才保留
                    if any(k in name for k in keywords) and is_clean_public_url(url_line):
                        if name not in seen_names:
                            group = "河北地方" if any(k in name for k in ["保定", "河北"]) else ("央视频道" if "CCTV" in name else "卫视频道")
                            m3u += f'#EXTINF:-1 group-title="{group}",{name}\n{url_line}\n'
                            seen_names.add(name)
        except: continue
        
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)

if __name__ == "__main__":
    process()
