import re
from urllib.request import Request, urlopen

# 聚合源地址
SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u"
]
OUTPUT_FILE = "hebei_iptv.m3u"
EPG_URL = "https://epg.zsdc.eu.org/t.xml.gz"

def process():
    m3u = f'#EXTM3U x-tvg-url="{EPG_URL}"\n'
    seen_urls = set()
    
    # 关键词策略：保定、河北、央视、卫视
    keywords = ["保定", "河北", "CCTV", "卫视"]
    
    for url in SOURCES:
        try:
            content = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=10).read().decode('utf-8')
            lines = content.splitlines()
            for i in range(len(lines) - 1):
                if "#EXTINF" in lines[i] and any(k in lines[i] for k in keywords):
                    name = lines[i].split(',')[-1]
                    url_line = lines[i+1].strip()
                    if url_line not in seen_urls:
                        # 简单的分类逻辑
                        group = "河北地方" if "保定" in name or "河北" in name else ("央视频道" if "CCTV" in name else "卫视频道")
                        m3u += f'#EXTINF:-1 group-title="{group}",{name}\n{url_line}\n'
                        seen_urls.add(url_line)
        except: continue
        
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u)

if __name__ == "__main__":
    process()
