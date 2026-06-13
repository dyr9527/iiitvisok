import re
from urllib.request import Request, urlopen

# 优质公网直播源聚合（这些源自带大量央卫视及高清频道，且通常为公网可播放）
SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.m3u"
]
OUTPUT_FILE = "hebei_iptv.m3u"
EPG_URL = "https://epg.zsdc.eu.org/t.xml.gz"

def is_valid_url(url):
    # 排除私网和运营商专用 IP 范围，确保是公网链接
    invalid_prefixes = ("192.168.", "10.", "172.16.", "112.25.", "39.134.", "223.110.")
    return not url.startswith(invalid_prefixes) and url.startswith("http")

def process():
    m3u = f'#EXTM3U x-tvg-url="{EPG_URL}"\n'
    seen_urls = set()
    
    # 你的核心关注频道：保定、河北、央视、卫视
    keywords = ["保定", "河北", "CCTV", "卫视"]
    
    for url in SOURCES:
        try:
            content = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read().decode('utf-8')
            lines = content.splitlines()
            for i in range(len(lines) - 1):
                if "#EXTINF" in lines[i]:
                    name = lines[i].split(',')[-1]
                    url_line = lines[i+1].strip()
                    
                    # 只有频道命中关键词 且 地址是公网的 才保留
                    if any(k in name for k in keywords) and is_valid_url(url_line):
                        if url_line not in seen_urls:
                            group = "河北地方" if any(k in name for k in ["保定", "河北"]) else ("央视频道" if "CCTV" in name else "卫视频道")
                            m3u += f'#EXTINF:-1 group-title="{group}",{name}\n{url_line}\n'
                            seen_urls.add(url_line)
        except: continue
        
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)

if __name__ == "__main__":
    process()
