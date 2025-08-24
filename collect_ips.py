import requests
from bs4 import BeautifulSoup
import re
import os
import time

# 目标URL列表
urls = [
    'https://ip.164746.xyz', 
    'https://cf.090227.xyz', 
    'https://stock.hostmonit.com/CloudFlareYes',
    'https://www.wetest.vip/page/cloudflare/address_v4.html'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

# 检查ip.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 使用集合存储IP地址实现自动去重
unique_ips = set()

for url in urls:
    try:
        # 发送HTTP请求获取网页内容
        response = requests.get(url, timeout=5)
        
        # 确保请求成功
        if response.status_code == 200:
            # 获取网页的文本内容
            html_content = response.text
            
            # 使用正则表达式查找IP地址
            ip_matches = re.findall(ip_pattern, html_content, re.IGNORECASE)
            
            # 将找到的IP添加到集合中（自动去重）
            unique_ips.update(ip_matches)
    except requests.exceptions.RequestException as e:
        print(f'请求 {url} 失败: {e}')
        continue

# 查询每个IP的国家信息，并保存格式为 ip:8443#国家
def get_country(ip):
    try:
        url = f'https://ip9.com.cn/get?ip={ip}'
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            # 返回内容形如 {"ip":"104.16.124.254","country":"美国",...}
            data = resp.json()
            return data.get('country', '未知')
        else:
            return '未知'
    except Exception as e:
        print(f"查询IP {ip} 国家失败: {e}")
        return '未知'

if unique_ips:
    # 按IP地址的数字顺序排序（非字符串顺序）
    sorted_ips = sorted(unique_ips, key=lambda ip: [int(part) for part in ip.split('.')])
    results = []
    for ip in sorted_ips:
        country = get_country(ip)
        results.append(f"{ip}:8443#{country}")
        time.sleep(0.5)  # 防止请求过快被封

    with open('ip.txt', 'w', encoding='utf-8') as file:
        for line in results:
            file.write(line + '\n')
    print(f'已保存 {len(results)} 个唯一IP地址及国家到ip.txt文件。')
else:
    print('未找到有效的IP地址。')
