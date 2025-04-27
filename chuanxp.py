import requests
from bs4 import BeautifulSoup
import re
import os
from ipaddress import ip_address, ip_network

def is_valid_ip(ip):
    """检查IP地址是否有效（支持IPv4和IPv6）"""
    try:
        ip_address(ip)
        return True
    except ValueError:
        return False

def fetch_ips_from_url(url, tag):
    """从指定URL提取IP地址（支持IPv4和IPv6）"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all(tag)
        ips = set()
        
        # 匹配IPv4和IPv6的正则表达式
        ip_pattern = re.compile(
            r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|'  # IPv4
            r'(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}|'  # IPv6完整格式
            r'(?:[A-Fa-f0-9]{1,4}:){1,7}:|'               # IPv6缩写格式（::）
            r'(?:[A-Fa-f0-9]{1,4}:){1,6}:[A-Fa-f0-9]{1,4}'  # IPv6混合格式
        )

        for element in elements:
            ip_matches = ip_pattern.findall(element.get_text())
            for ip in ip_matches:
                if is_valid_ip(ip):
                    ips.add(ip)
        return ips
    except requests.RequestException as e:
        print(f"请求失败: {url}, 错误: {e}")
        return set()
    except Exception as e:
        print(f"解析错误: {url}, 错误: {e}")
        return set()

def save_ips_to_file(ips, filename):
    """将IP地址保存到文件"""
    with open(filename, 'w') as file:
        for ip in sorted(ips):  # 按字母顺序排序
            file.write(ip + '\n')

def main():
    # 目标URL及其对应的HTML标签
    urls = {
        'https://monitor.gacjie.cn/page/cloudflare/ipv4.html': 'tr',
        'https://ip.164746.xyz': 'tr',
        'https://www.wetest.vip/page/cloudfront/address_v6.html': 'tr',  # 新增IPv6地址抓取
    }

    unique_ips = set()

    # 从每个URL提取IP地址
    for url, tag in urls.items():
        print(f"正在处理: {url}")
        ips = fetch_ips_from_url(url, tag)
        unique_ips.update(ips)
        print(f"已找到 {len(ips)} 个IP地址")

    # 保存到文件
    output_file = 'chuan.txt'
    if os.path.exists(output_file):
        os.remove(output_file)
    
    save_ips_to_file(unique_ips, output_file)
    print(f"共保存 {len(unique_ips)} 个唯一IP地址到 {output_file}")

if __name__ == "__main__":
    main()
