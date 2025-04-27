import requests
from bs4 import BeautifulSoup
import re
import os
from ipaddress import ip_address

def is_valid_ip(ip):
    """检查IP地址是否有效（支持IPv4和IPv6）"""
    try:
        ip_address(ip.split('[')[-1].split(']')[0])  # 处理带方括号的IPv6（如[2001:db8::1]）
        return True
    except ValueError:
        return False

def fetch_ips_from_url(url, tag):
    """从指定URL提取IP地址和端口号（格式为 IP:Port）"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all(tag)
        ip_ports = set()

        # 匹配 IPv4:Port 或 [IPv6]:Port 的正则表达式
        ip_port_pattern = re.compile(
            r'(?:\[?([A-Fa-f0-9:]+)\]?|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})):(\d{1,5})'  # 匹配 IP:Port
        )

        for element in elements:
            matches = ip_port_pattern.finditer(element.get_text())
            for match in matches:
                ip = match.group(1) if match.group(1) else match.group(2)  # 提取IPv6或IPv4
                port = match.group(3)
                if ip and port and is_valid_ip(ip):
                    if ':' in ip and not ip.startswith('['):  # 为IPv6添加方括号（如2001:db8::1:80 → [2001:db8::1]:80）
                        ip_port = f"[{ip}]:{port}"
                    else:
                        ip_port = f"{ip}:{port}"
                    ip_ports.add(ip_port)
        return ip_ports
    except requests.RequestException as e:
        print(f"请求失败: {url}, 错误: {e}")
        return set()
    except Exception as e:
        print(f"解析错误: {url}, 错误: {e}")
        return set()

def save_ips_to_file(ip_ports, filename):
    """将IP:Port保存到文件"""
    with open(filename, 'w') as file:
        for ip_port in sorted(ip_ports):  # 按字母顺序排序
            file.write(ip_port + '\n')

def main():
    # 目标URL及其对应的HTML标签
    urls = {
        'https://monitor.gacjie.cn/page/cloudflare/ipv4.html': 'tr',
        'https://ip.164746.xyz': 'tr',
        'https://www.wetest.vip/page/cloudfront/address_v6.html': 'tr',  # 抓取IPv6:Port
    }

    unique_ip_ports = set()

    # 从每个URL提取IP:Port
    for url, tag in urls.items():
        print(f"正在处理: {url}")
        ip_ports = fetch_ips_from_url(url, tag)
        unique_ip_ports.update(ip_ports)
        print(f"已找到 {len(ip_ports)} 个IP:Port组合")

    # 保存到文件
    output_file = 'chuan.txt'
    if os.path.exists(output_file):
        os.remove(output_file)
    
    save_ips_to_file(unique_ip_ports, output_file)
    print(f"共保存 {len(unique_ip_ports)} 个唯一IP:Port组合到 {output_file}")

if __name__ == "__main__":
    main()
