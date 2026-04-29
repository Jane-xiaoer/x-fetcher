#!/usr/bin/env python3
"""
微信公众号文章抓取工具
基于 wechat-fetcher v1 升级:用 Python requests 替代 curl,跨平台 SSL 稳。

用法:
    python fetch_wechat.py <wechat_url>

输出:标题 + 作者 + 字数 + 正文(纯文本)
"""

import sys
import re
import requests

# 微信内置浏览器 UA(伪装成微信内打开,无需 Cookie/登录)
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
      "MicroMessenger/8.0.34(0x16082222) NetType/WIFI Language/zh_CN")


def fetch_html(url: str) -> str:
    """用 UA 伪装抓取微信文章 HTML。跨平台 SSL,先严格验证,失败回退跳过验证。"""
    headers = {"User-Agent": UA}
    try:
        r = requests.get(url, headers=headers, timeout=30, verify=True)
    except requests.exceptions.SSLError:
        # macOS 默认 curl 风格 SSL 失败,回退跳过验证(等同 curl -k)
        r = requests.get(url, headers=headers, timeout=30, verify=False)
    r.encoding = "utf-8"
    return r.text


def parse_article(html: str) -> dict:
    """从微信公众号 HTML 提取标题/作者/正文。"""
    # 标题
    title = ""
    m = re.search(r'<h1[^>]*class="rich_media_title"[^>]*>\s*(.*?)\s*</h1>', html, re.S)
    if m:
        title = re.sub(r'<[^>]+>', '', m.group(1)).strip()

    # 作者(优先从 nickname meta,备选从 var nickname)
    author = ""
    m = re.search(r'<span class="rich_media_meta rich_media_meta_nickname"[^>]*>\s*(.*?)\s*</span>', html, re.S)
    if m:
        author = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    if not author:
        m = re.search(r'var\s+nickname\s*=\s*"([^"]+)"', html)
        if m:
            author = m.group(1)

    # 正文(从 #js_content)
    body = ""
    m = re.search(r'id="js_content"[^>]*>(.*?)</div>', html, re.S)
    if m:
        raw = m.group(1)
        # 去掉 script/style
        raw = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.S)
        raw = re.sub(r'<style[^>]*>.*?</style>', '', raw, flags=re.S)
        # <br> 转换行
        raw = re.sub(r'<br\s*/?>', '\n', raw, flags=re.I)
        # </p> 转换行
        raw = re.sub(r'</p>', '\n', raw, flags=re.I)
        # 剥光剩余标签
        raw = re.sub(r'<[^>]+>', '', raw)
        # 解码 HTML 实体
        raw = (raw.replace('&nbsp;', ' ')
                  .replace('&amp;', '&')
                  .replace('&lt;', '<')
                  .replace('&gt;', '>')
                  .replace('&quot;', '"'))
        # 清空白
        lines = [l.strip() for l in raw.split('\n')]
        lines = [l for l in lines if l]
        body = '\n'.join(lines)

    return {"title": title, "author": author, "body": body, "html_length": len(html)}


def main():
    if len(sys.argv) < 2:
        print("用法: python fetch_wechat.py <wechat_url>", file=sys.stderr)
        sys.exit(2)

    url = sys.argv[1]
    if "mp.weixin.qq.com" not in url:
        print(f"❌ 这不像微信公众号链接: {url}", file=sys.stderr)
        sys.exit(2)

    html = fetch_html(url)
    article = parse_article(html)

    if not article["title"] and not article["body"]:
        print(f"❌ 抓取失败:可能是需要登录的私密文章,或链接已失效。页面长度: {article['html_length']} 字符")
        sys.exit(1)

    print(f"【标题】{article['title']}")
    if article["author"]:
        print(f"【作者】{article['author']}")
    print(f"【字数】{len(article['body'])} 字")
    print("【正文】")
    print(article["body"])


if __name__ == "__main__":
    main()
