#!/usr/bin/env python3
"""
X (Twitter) 帖子内容抓取工具
支持普通推文和 X Article 长文章，可选抓取评论
用法: python fetch_x.py <x_url> [选项]
"""

import sys
import re
import json
import os
from datetime import datetime
import requests
from urllib.parse import urlparse

def extract_tweet_id(url):
    """从 URL 提取 tweet ID"""
    patterns = [
        r'(?:x\.com|twitter\.com)/\w+/status/(\d+)',
        r'(?:x\.com|twitter\.com)/\w+/statuses/(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def extract_username(url):
    """从 URL 提取用户名"""
    match = re.search(r'(?:x\.com|twitter\.com)/(\w+)/status', url)
    return match.group(1) if match else None

def fetch_via_fxtwitter(url):
    """通过 fxtwitter API 获取内容"""
    api_url = re.sub(r'(x\.com|twitter\.com)', 'api.fxtwitter.com', url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    try:
        resp = requests.get(api_url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"  fxtwitter 错误: {e}", file=sys.stderr)
    return None

def fetch_via_syndication(tweet_id):
    """通过 X 的 syndication API 获取内容"""
    url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"  syndication 错误: {e}", file=sys.stderr)
    return None

def fetch_replies_via_syndication(tweet_id):
    """通过 syndication API 获取评论/回复"""
    url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # syndication API 返回的数据中可能包含部分回复
            replies = []
            if "conversation" in data:
                for item in data.get("conversation", []):
                    if item.get("id_str") != tweet_id:
                        replies.append({
                            "id": item.get("id_str", ""),
                            "text": item.get("text", ""),
                            "author": item.get("user", {}).get("name", ""),
                            "username": item.get("user", {}).get("screen_name", ""),
                            "created_at": item.get("created_at", ""),
                            "likes": item.get("favorite_count", 0),
                            "retweets": item.get("retweet_count", 0)
                        })
            return replies
    except Exception as e:
        print(f"  获取评论错误: {e}", file=sys.stderr)
    return []

def fetch_replies_via_fxtwitter(tweet_id, username):
    """通过多种方式尝试获取评论"""
    replies = []
    
    # 方法1: 尝试 syndication conversation
    syndication_replies = fetch_replies_via_syndication(tweet_id)
    if syndication_replies:
        replies.extend(syndication_replies)
    
    # 方法2: 尝试通过搜索 API 获取回复 (使用 nitter 实例)
    nitter_instances = [
        "nitter.poast.org",
        "nitter.privacydev.net",
    ]
    
    for instance in nitter_instances:
        try:
            search_url = f"https://{instance}/{username}/status/{tweet_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            resp = requests.get(search_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                # 简单解析回复（nitter 页面结构）
                html = resp.text
                # 查找回复区域
                reply_pattern = r'class="reply-thread".*?class="tweet-content[^"]*"[^>]*>([^<]+)<'
                reply_matches = re.findall(reply_pattern, html, re.DOTALL)
                for i, text in enumerate(reply_matches[:20]):  # 最多20条
                    text = text.strip()
                    if text and len(text) > 5:
                        replies.append({
                            "id": f"reply_{i}",
                            "text": text,
                            "author": "Unknown",
                            "username": "unknown",
                            "created_at": "",
                            "likes": 0,
                            "retweets": 0
                        })
                if replies:
                    break
        except Exception as e:
            continue
    
    return replies

def extract_article_content(article):
    """从 X Article 中提取完整内容"""
    if not article:
        return None

    content_blocks = article.get("content", {}).get("blocks", [])

    # 拼接所有文本块
    paragraphs = []
    for block in content_blocks:
        text = block.get("text", "").strip()
        block_type = block.get("type", "unstyled")

        if text:
            # 根据类型添加格式
            if block_type == "header-one":
                paragraphs.append(f"# {text}")
            elif block_type == "header-two":
                paragraphs.append(f"## {text}")
            elif block_type == "header-three":
                paragraphs.append(f"### {text}")
            elif block_type == "blockquote":
                paragraphs.append(f"> {text}")
            elif block_type == "unordered-list-item":
                paragraphs.append(f"- {text}")
            elif block_type == "ordered-list-item":
                paragraphs.append(f"1. {text}")
            else:
                paragraphs.append(text)

    return "\n\n".join(paragraphs)

def format_output(data, source):
    """格式化输出"""
    result = {
        "source": source,
        "success": True,
        "type": "tweet",
        "content": {}
    }

    if source == "fxtwitter":
        tweet = data.get("tweet", {})
        article = tweet.get("article")

        if article:
            # X Article 长文章
            result["type"] = "article"
            result["content"] = {
                "title": article.get("title", ""),
                "preview": article.get("preview_text", ""),
                "full_text": extract_article_content(article),
                "cover_image": article.get("cover_media", {}).get("media_info", {}).get("original_img_url"),
                "author": tweet.get("author", {}).get("name", ""),
                "username": tweet.get("author", {}).get("screen_name", ""),
                "created_at": article.get("created_at", ""),
                "modified_at": article.get("modified_at", ""),
                "likes": tweet.get("likes", 0),
                "retweets": tweet.get("retweets", 0),
                "views": tweet.get("views", 0),
                "bookmarks": tweet.get("bookmarks", 0)
            }
        else:
            # 普通推文
            result["content"] = {
                "text": tweet.get("text", ""),
                "author": tweet.get("author", {}).get("name", ""),
                "username": tweet.get("author", {}).get("screen_name", ""),
                "created_at": tweet.get("created_at", ""),
                "likes": tweet.get("likes", 0),
                "retweets": tweet.get("retweets", 0),
                "views": tweet.get("views", 0),
                "media": [m.get("url") for m in tweet.get("media", {}).get("all", []) if m.get("url")],
                "replies": tweet.get("replies", 0)
            }

    elif source == "syndication":
        result["content"] = {
            "text": data.get("text", ""),
            "author": data.get("user", {}).get("name", ""),
            "username": data.get("user", {}).get("screen_name", ""),
            "created_at": data.get("created_at", ""),
            "likes": data.get("favorite_count", 0),
            "retweets": data.get("retweet_count", 0),
            "media": [m.get("media_url_https") for m in data.get("mediaDetails", []) if m.get("media_url_https")]
        }

    return result

def fetch_tweet(url):
    """主函数：尝试多种方式获取帖子内容"""
    tweet_id = extract_tweet_id(url)
    username = extract_username(url)

    if not tweet_id:
        return {"success": False, "error": "无法从 URL 提取 tweet ID"}, tweet_id, username

    print(f"📍 Tweet ID: {tweet_id}", file=sys.stderr)
    print(f"📍 Username: {username}", file=sys.stderr)
    print(f"🔍 正在抓取...", file=sys.stderr)

    # 方法1: fxtwitter API (支持 Article)
    print("  尝试 fxtwitter API...", file=sys.stderr)
    data = fetch_via_fxtwitter(url)
    if data and data.get("tweet"):
        print("  ✅ fxtwitter 成功", file=sys.stderr)
        return format_output(data, "fxtwitter"), tweet_id, username

    # 方法2: syndication API
    print("  尝试 syndication API...", file=sys.stderr)
    data = fetch_via_syndication(tweet_id)
    if data and data.get("text"):
        print("  ✅ syndication 成功", file=sys.stderr)
        return format_output(data, "syndication"), tweet_id, username

    return {"success": False, "error": "所有抓取方式均失败"}, tweet_id, username


def generate_markdown(result, tweet_id, username, url, replies=None, include_replies=False):
    """生成 Markdown 格式内容"""
    content = result.get("content", {})
    content_type = result.get("type", "tweet")
    
    lines = []
    
    if content_type == "article":
        # X Article 长文章
        title = content.get("title", "Untitled")
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"> 作者: **{content.get('author', '')}** (@{content.get('username', '')})")
        lines.append(f"> 发布时间: {content.get('created_at', '')}")
        if content.get('modified_at'):
            lines.append(f"> 修改时间: {content.get('modified_at', '')}")
        lines.append(f"> 原文链接: {url}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 封面图
        if content.get("cover_image"):
            lines.append(f"![封面]({content.get('cover_image')})")
            lines.append("")
        
        # 正文
        if content.get("full_text"):
            lines.append(content.get("full_text"))
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 互动数据")
        lines.append("")
        lines.append(f"- ❤️ 点赞: {content.get('likes', 0):,}")
        lines.append(f"- 🔁 转发: {content.get('retweets', 0):,}")
        lines.append(f"- 👀 浏览: {content.get('views', 0):,}")
        lines.append(f"- 🔖 书签: {content.get('bookmarks', 0):,}")
    else:
        # 普通推文
        lines.append(f"# @{content.get('username', '')} 的推文")
        lines.append("")
        lines.append(f"> 作者: **{content.get('author', '')}** (@{content.get('username', '')})")
        lines.append(f"> 发布时间: {content.get('created_at', '')}")
        lines.append(f"> 原文链接: {url}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(content.get("text", ""))
        lines.append("")
        
        # 媒体
        media = content.get("media", [])
        if media:
            lines.append("## 媒体")
            lines.append("")
            for i, m in enumerate(media, 1):
                lines.append(f"![媒体{i}]({m})")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("## 互动数据")
        lines.append("")
        lines.append(f"- ❤️ 点赞: {content.get('likes', 0):,}")
        lines.append(f"- 🔁 转发: {content.get('retweets', 0):,}")
        lines.append(f"- 👀 浏览: {content.get('views', 0):,}")
        lines.append(f"- 💬 回复: {content.get('replies', 0):,}")
    
    # 添加评论部分
    if include_replies and replies:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 评论/回复")
        lines.append("")
        for i, reply in enumerate(replies, 1):
            lines.append(f"### {i}. @{reply.get('username', 'unknown')}")
            if reply.get('author'):
                lines.append(f"**{reply.get('author')}**")
            lines.append("")
            lines.append(reply.get('text', ''))
            lines.append("")
            if reply.get('likes') or reply.get('retweets'):
                lines.append(f"*❤️ {reply.get('likes', 0)} | 🔁 {reply.get('retweets', 0)}*")
            lines.append("")
    
    return "\n".join(lines)


def save_markdown(markdown_content, tweet_id, username, suffix=""):
    """保存 Markdown 文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if suffix:
        filename = f"{username}_{tweet_id}_{suffix}_{timestamp}.md"
    else:
        filename = f"{username}_{tweet_id}_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    return filename


def interactive_menu(result, tweet_id, username, url):
    """交互式菜单，让用户选择要抓取的内容"""
    content = result.get("content", {})
    content_type = result.get("type", "tweet")
    
    print("\n" + "="*50, file=sys.stderr)
    print("📋 抓取成功！请选择要保存的内容：", file=sys.stderr)
    print("="*50, file=sys.stderr)
    print("", file=sys.stderr)
    print("  [1] 仅保存主贴内容          → 输出 Markdown (.md)", file=sys.stderr)
    print("  [2] 仅保存评论/回复         → 输出 Markdown (.md)", file=sys.stderr)
    print("  [3] 保存主贴 + 评论（完整归档）→ 输出 Markdown (.md)", file=sys.stderr)
    print("  [4] 仅查看数据（不保存文件）  → 输出 JSON", file=sys.stderr)
    print("  [0] 退出", file=sys.stderr)
    print("", file=sys.stderr)
    
    choice = input("请输入选项 (0-4): ").strip()
    
    replies = []
    
    if choice in ['2', '3']:
        print("\n🔍 正在抓取评论...", file=sys.stderr)
        replies = fetch_replies_via_fxtwitter(tweet_id, username)
        if replies:
            print(f"  ✅ 获取到 {len(replies)} 条评论", file=sys.stderr)
        else:
            print("  ⚠️ 未能获取到评论（可能是 API 限制或无评论）", file=sys.stderr)
    
    if choice == '1':
        # 仅主贴
        markdown_content = generate_markdown(result, tweet_id, username, url, replies=None, include_replies=False)
        filename = save_markdown(markdown_content, tweet_id, username, "post")
        print(f"\n✅ 主贴已保存到: {filename}", file=sys.stderr)
        
    elif choice == '2':
        # 仅评论
        if replies:
            lines = [f"# @{username} 推文的评论", ""]
            lines.append(f"> 原文链接: {url}")
            lines.append(f"> 抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
            lines.append("---")
            lines.append("")
            for i, reply in enumerate(replies, 1):
                lines.append(f"## {i}. @{reply.get('username', 'unknown')}")
                if reply.get('author'):
                    lines.append(f"**{reply.get('author')}**")
                lines.append("")
                lines.append(reply.get('text', ''))
                lines.append("")
                if reply.get('likes') or reply.get('retweets'):
                    lines.append(f"*❤️ {reply.get('likes', 0)} | 🔁 {reply.get('retweets', 0)}*")
                lines.append("")
            markdown_content = "\n".join(lines)
            filename = save_markdown(markdown_content, tweet_id, username, "replies")
            print(f"\n✅ 评论已保存到: {filename}", file=sys.stderr)
        else:
            print("\n⚠️ 没有评论可保存", file=sys.stderr)
            
    elif choice == '3':
        # 完整归档
        markdown_content = generate_markdown(result, tweet_id, username, url, replies=replies, include_replies=True)
        filename = save_markdown(markdown_content, tweet_id, username, "full")
        print(f"\n✅ 完整归档已保存到: {filename}", file=sys.stderr)
        
    elif choice == '4':
        # 仅 JSON
        output = {
            "tweet": result,
            "replies": replies if replies else []
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        
    elif choice == '0':
        print("\n👋 已退出", file=sys.stderr)
    else:
        print("\n⚠️ 无效选项", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        print("用法: python fetch_x.py <x_url> [选项]")
        print("")
        print("选项:")
        print("  --save-md        直接保存主贴为 Markdown")
        print("  --with-replies   同时抓取评论")
        print("  --full           保存完整归档（主贴+评论）")
        print("  --json           仅输出 JSON，不保存文件")
        print("")
        print("示例:")
        print("  python fetch_x.py https://x.com/elonmusk/status/123456789")
        print("  python fetch_x.py https://x.com/elonmusk/status/123456789 --full")
        sys.exit(1)

    url = sys.argv[1]
    
    # 解析命令行参数
    save_md = "--save-md" in sys.argv
    with_replies = "--with-replies" in sys.argv
    full_archive = "--full" in sys.argv
    json_only = "--json" in sys.argv
    
    result, tweet_id, username = fetch_tweet(url)

    if not result.get("success"):
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    # 根据参数决定行为
    if json_only:
        # 仅输出 JSON
        replies = []
        if with_replies or full_archive:
            print("🔍 正在抓取评论...", file=sys.stderr)
            replies = fetch_replies_via_fxtwitter(tweet_id, username)
        output = {"tweet": result, "replies": replies}
        print(json.dumps(output, ensure_ascii=False, indent=2))
        
    elif full_archive:
        # 完整归档模式
        print("🔍 正在抓取评论...", file=sys.stderr)
        replies = fetch_replies_via_fxtwitter(tweet_id, username)
        if replies:
            print(f"  ✅ 获取到 {len(replies)} 条评论", file=sys.stderr)
        markdown_content = generate_markdown(result, tweet_id, username, url, replies=replies, include_replies=True)
        filename = save_markdown(markdown_content, tweet_id, username, "full")
        print(f"✅ 完整归档已保存到: {filename}", file=sys.stderr)
        
    elif save_md:
        # 仅保存主贴
        replies = []
        if with_replies:
            print("🔍 正在抓取评论...", file=sys.stderr)
            replies = fetch_replies_via_fxtwitter(tweet_id, username)
        markdown_content = generate_markdown(result, tweet_id, username, url, replies=replies, include_replies=with_replies)
        filename = save_markdown(markdown_content, tweet_id, username)
        print(f"✅ 已保存到: {filename}", file=sys.stderr)
        
    else:
        # 交互模式
        print(json.dumps(result, ensure_ascii=False, indent=2))
        interactive_menu(result, tweet_id, username, url)


if __name__ == "__main__":
    main()
