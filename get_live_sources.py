import datetime
import os
import re
from bs4 import BeautifulSoup
import requests

TARGET_URL = "http://nn.7x9d.cn/xzjd2.php?id=%E6%B2%B3%E5%8C%97"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_m3u_sources():
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        response.encoding = response.apparent_encoding

        if response.status_code != 200:
            print(f"无法访问网站，状态码: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        
        # 寻找包含 "运营商：河北-电信" 文本的元素
        target_text_node = soup.find(text=re.compile(r"运营商：\s*河北\s*-\s*电信"))
        if not target_text_node:
            target_text_node = soup.find(text=re.compile(r"河北.*电信"))

        if not target_text_node:
            print("未找到指定的‘运营商：河北-电信’文本标识")
            return

        # 寻找上方的超链接按钮
        download_btn = target_text_node.find_previous("a")
        if not download_btn or not download_btn.get("href"):
            print("未能在目标文本上方找到超链接按钮")
            return

        sub_link = download_btn.get("href")
        if sub_link.startswith("/"):
            sub_link = "http://nn.7x9d.cn" + sub_link
        elif not sub_link.startswith("http"):
            sub_link = "http://nn.7x9d.cn/" + sub_link

        print(f"成功提取下级链接: {sub_link}")

        # 访问下级链接
        sub_response = requests.get(sub_link, headers=HEADERS, timeout=15)
        sub_response.encoding = sub_response.apparent_encoding
        raw_text = sub_response.text

        if not raw_text.strip():
            print("下载的直播源内容为空")
            return

        # 加工 M3U 格式
        m3u_lines = ["#EXTM3U"]
        for line in raw_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = re.split(r"[,，#]", line, maxsplit=1)
            if len(parts) == 2:
                channel_name = parts[0].strip()
                channel_url = parts[1].strip()
                m3u_lines.append(f'#EXTINF:-1 tvg-name="{channel_name}",{channel_name}')
                m3u_lines.append(channel_url)

        # 确保输出到当前工作目录（仓库根目录）
        output_filename = "hebei_telecom.m3u"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))

        print(f"处理完成！M3U 文件已更新。")

    except Exception as e:
        print(f"运行过程中发生错误: {e}")

if __name__ == "__main__":
    fetch_m3u_sources()
