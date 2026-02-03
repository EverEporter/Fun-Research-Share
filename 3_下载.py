#!/usr/bin/env python
# coding: utf-8

import json
import os
import re
import requests

def _get_requests_proxies():
    """
    requests 代理（可选）：通过环境变量开启
    - DOWNLOAD_PROXY_HTTP: 例如 "http://127.0.0.1:7890"
    - DOWNLOAD_PROXY_HTTPS: 例如 "http://127.0.0.1:7890"

    为空则不设置 proxies（requests 将走系统环境变量或直连，取决于你的环境）。
    """
    http = (os.getenv("DOWNLOAD_PROXY_HTTP") or "").strip()
    https = (os.getenv("DOWNLOAD_PROXY_HTTPS") or "").strip()

    if not http and not https:
        return None

    proxies = {}
    if http:
        proxies["http"] = http
    if https:
        proxies["https"] = https
    return proxies

def sanitize_filename(s):
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/*?:"<>|]', '', s).strip().replace(' ', '_')

def download_pdfs(json_path, save_dir):
    # 创建保存目录（如果不存在）
    os.makedirs(save_dir, exist_ok=True)
    
    # 读取JSON文件
    with open(json_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    
    #读取已存在文件
    existing_files = set(
        f for f in os.listdir(save_dir)
        if f.endswith('.pdf')
    )
    total = len(entries)
    success_count = 0
    fail_count = 0
    
    # 遍历所有条目下载文件
    for idx, entry in enumerate(entries, 1):
        try:
            # 生成安全文件名
            time_str = entry["time"]
            org_name = sanitize_filename(entry["org_name"])
            title = sanitize_filename(entry["title"])
            filename = f"{time_str}_{org_name}_{title}.pdf"
            
            # 构建保存路径
            filepath = os.path.join(save_dir, filename)
            
            if filename in existing_files:
                success_count += 1
                #print(f"文件已存在，跳过：{filename}")
                continue
            
            # 下载文件
            response = requests.get(entry["download"], timeout=10, proxies=_get_requests_proxies())
            response.raise_for_status()  # 检查HTTP错误
            
            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(response.content)
                

            print(f"({idx}/{total}) 成功下载：{filename} ")
            
            #print(f"成功下载：{filename}")
            
        except Exception as e:
            print(f"下载失败【{entry.get('title', '')}】：{str(e)}")

    print("\n" + "="*50)
    print(f"下载任务完成：\n"
          f"✓ 总文件数：{idx}")


if __name__ == "__main__":
    configs = [
        {
            "JSON_FILE": os.path.join(os.path.dirname(__file__), "data/add-links", "基金深度-download-links.json"),
            "SAVE_DIR": os.path.join(os.path.dirname(__file__), "data/reports", "基金深度")
        },
        {
            "JSON_FILE": os.path.join(os.path.dirname(__file__), "data/add-links", "金工深度-download-links.json"),
            "SAVE_DIR": os.path.join(os.path.dirname(__file__), "data/reports", "金工深度")
        },
        {
            "JSON_FILE": os.path.join(os.path.dirname(__file__), "data/add-links", "金工策略-download-links.json"),
            "SAVE_DIR": os.path.join(os.path.dirname(__file__), "data/reports", "金工策略")
        },
        {
            "JSON_FILE": os.path.join(os.path.dirname(__file__), "data/add-links", "金工动态点评-download-links.json"),
            "SAVE_DIR": os.path.join(os.path.dirname(__file__), "data/reports", "金工动态点评")
        },
        {
            "JSON_FILE": os.path.join(os.path.dirname(__file__), "data/add-links", "基金策略-download-links.json"),
            "SAVE_DIR": os.path.join(os.path.dirname(__file__), "data/reports", "基金策略")
        },  
        {
            "JSON_FILE": os.path.join(os.path.dirname(__file__), "data/add-links", "其他-download-links.json"),
            "SAVE_DIR": os.path.join(os.path.dirname(__file__), "data/reports", "其他研究")
        },  
        {
            "JSON_FILE": os.path.join(os.path.dirname(__file__), "data/add-links", "市场策略-download-links.json"),
            "SAVE_DIR": os.path.join(os.path.dirname(__file__), "data/reports", "市场策略")
        },  
    ]
    
    # 遍历执行所有下载任务
    for cfg in configs:
        print(f"\n{'='*30} 开始下载任务：{cfg['SAVE_DIR']} {'='*30}")
        download_pdfs(cfg["JSON_FILE"], cfg["SAVE_DIR"])
