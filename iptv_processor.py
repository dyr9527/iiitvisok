import re
from urllib.request import Request, urlopen

# 依然使用这些仓库，但必须进行更深度的清洗
SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.m3u"
]
OUTPUT_FILE = "hebei_iptv.m3u"
EPG_URL = "https://epg.zsdc.eu.org/t.xml.gz"

def is_public_playable(url):
    # 彻底封杀所有以 '[' 开头的 IPv6 地址 和 运营商专用 IP
    if url.startswith("[") or "PLTV" in url or "chinamobile" in url or "112.25" in url:
        return False
    # 只允许通过域名访问的链接
    if "://" in url and not any(x in url for x in ["192.168.", "10.", "172.16."]):
        return True
    return False

def process():
    m3u = f'#EXTM3U x-tvg-url="{EPG_URL}"\n'
    seen_names = set()
    
    for url in SOURCES:
        try:
            content = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read().decode('utf-8')
            lines = content.splitlines()
            for i in range(len(lines) - 1):
                if "#EXTINF" in lines[i]:
                    name = lines[i].split(',')[-1]
                    url_line = lines[i+1].strip()
                    
                    # 关键词匹配 + 必须是公网可播放地址
                    if any(k in name for k in ["CCTV", "卫视", "河北", "保定"]) and is_public_playable(url_line):
                        if name not in seen_names:
                            m3u += f'#EXTINF:-1,{name}\n{url_line}\n'
                            seen_names.add(name)
        except: continue
        
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)

if __name__ == "__main__":
    process()
