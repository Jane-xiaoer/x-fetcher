---
name: x-fetcher
description: 抓取 X (Twitter) 帖子 + 微信公众号文章。X 支持普通推文 / X Article 长文章 / 互动数据,微信支持公众号文章正文+作者+字数。触发词:x.com、twitter.com、X 链接、推文、X Article、mp.weixin.qq.com、微信文章、公众号链接、抓取公众号
---

# x-fetcher v2 — 双能力内容抓取器

**装一个 skill,抓两个平台**:X (Twitter) + 微信公众号文章。

## 触发场景

只要用户消息里出现以下任一,自动调用本 skill:

| 平台 | URL 特征 | 用哪个脚本 |
|---|---|---|
| X / Twitter | `x.com/*/status/*` 或 `twitter.com/*/status/*` | `python fetch_x.py <url>` |
| 微信公众号 | `mp.weixin.qq.com/s/*` | `python fetch_wechat.py <url>` |

## 核心命令

### X / Twitter

```bash
python fetch_x.py <x_url> [选项]
```

选项:`--save-md` / `--with-replies` / `--full` / `--json` / **`--save-video`**(🆕 下载推文视频)

详见根目录 README 的"X 抓取"段。

### 微信公众号

```bash
python fetch_wechat.py <wechat_url>
```

输出:标题 + 作者 + 字数 + 正文(纯文本)。

## 执行流程

1. 识别 URL 平台(x.com / twitter.com / mp.weixin.qq.com)
2. 调对应脚本
3. 解析输出
4. 直接交付给用户,或继续下游处理(翻译 / 摘要 / 发布 / 归档)

## 注意

- 仅适用于公开内容(私密账号 / 需登录文章无法抓取)
- 微信链接有效期通常较长,极少数旧文章可能失效
- 依赖 Python `requests` 库(已在 requirements.txt)
- 跨平台 SSL:微信抓取用 Python `requests`(自动处理证书),不需要 macOS 上 curl `-k` 的 hack
