# x-fetcher v2

**装一个 skill,抓两个平台**:X (Twitter) + 微信公众号文章。

> v2 升级(2026-04-29):合并 wechat-fetcher 能力,新增微信公众号文章抓取。
> Claude Code skill 自动触发(放进 `~/.claude/skills/` 即可,扔链接给 CC 自动识别 + 抓)。

## 安装

### 作为 Claude Code Skill(推荐)

```bash
git clone https://github.com/Jane-xiaoer/x-fetcher.git ~/.claude/skills/x-fetcher
cd ~/.claude/skills/x-fetcher
pip install -r requirements.txt
```

装完后,在 Claude Code 里直接扔链接,CC 自动识别平台 + 调对应脚本:

> 抓一下这个 https://x.com/elonmusk/status/123456789
> 抓这篇微信文章 https://mp.weixin.qq.com/s/abc123

### 作为命令行工具

```bash
git clone https://github.com/Jane-xiaoer/x-fetcher.git
cd x-fetcher
pip install -r requirements.txt
```

---

## 使用

### 一、抓 X (Twitter) 帖子

```bash
python fetch_x.py <x_url> [选项]
```

#### 选项

| 选项 | 说明 |
|------|------|
| `--save-md` | 直接保存主贴为 Markdown |
| `--with-replies` | 同时抓取评论 |
| `--full` | 保存完整归档(主贴+评论) |
| `--json` | 仅输出 JSON,不保存文件 |
| `--save-video` 🆕 | 下载推文里的视频/媒体到当前目录(可与其它选项叠加) |

#### 示例

```bash
# 交互模式(推荐)— 会询问你要保存哪些内容
python fetch_x.py "https://x.com/elonmusk/status/123456789"

# 抓取 X Article 长文章
python fetch_x.py "https://x.com/thedankoe/status/2010751592346030461"

# 直接保存主贴为 Markdown
python fetch_x.py "https://x.com/elonmusk/status/123456789" --save-md

# 保存完整归档(主贴 + 评论)
python fetch_x.py "https://x.com/elonmusk/status/123456789" --full

# 仅输出 JSON
python fetch_x.py "https://x.com/elonmusk/status/123456789" --json --with-replies

# 🆕 下载推文里的视频(以 {username}_{tweet_id}_video_N.mp4 命名)
python fetch_x.py "https://x.com/zeke/status/2049348208489570771" --save-video

# 视频 + 评论 + 完整归档,叠加用
python fetch_x.py "https://x.com/elonmusk/status/123456789" --full --save-video
```

#### 交互模式菜单

```
📋 抓取成功!请选择要保存的内容:
==================================================

  [1] 仅保存主贴内容
  [2] 仅保存评论/回复
  [3] 保存主贴 + 评论(完整归档)
  [4] 仅输出 JSON(不保存文件)
  [0] 退出
```

#### 生成文件命名

`{用户名}_{推文ID}_{类型}_{时间戳}.md`

- `_post_` — 仅主贴
- `_replies_` — 仅评论
- `_full_` — 完整归档

#### X 输出格式

**普通推文**:
```json
{
  "source": "fxtwitter",
  "success": true,
  "type": "tweet",
  "content": {
    "text": "推文内容...",
    "author": "作者名",
    "username": "用户名",
    "created_at": "发布时间",
    "likes": 1234,
    "retweets": 567,
    "views": 89000,
    "media": ["图片/视频URL"],
    "replies": 123
  }
}
```

**X Article 长文章**:
```json
{
  "source": "fxtwitter",
  "success": true,
  "type": "article",
  "content": {
    "title": "文章标题",
    "preview": "文章预览...",
    "full_text": "完整文章内容(Markdown 格式)...",
    "cover_image": "封面图URL",
    "author": "作者名",
    "username": "用户名",
    "created_at": "创建时间",
    "modified_at": "修改时间",
    "likes": 206351,
    "retweets": 28631,
    "views": 115555283,
    "bookmarks": 571495
  }
}
```

---

### 二、抓微信公众号文章 🆕(v2 新增)

```bash
python fetch_wechat.py <wechat_url>
```

#### 示例

```bash
python fetch_wechat.py "https://mp.weixin.qq.com/s/abc123"
```

#### 输出

```
【标题】xxx
【作者】xxx
【字数】xxx 字
【正文】
完整正文(纯文本,段落保留)
```

#### 工作原理

- **UA 伪装法**:用微信内置浏览器 UA 直接 HTTP GET,无需 Cookie / 代理 / 登录
- **跨平台 SSL**:用 Python `requests`(自动处理证书),先严格验证,失败回退跳过验证。**比 curl `-k` 跨平台稳**
- 纯正则解析(从 `#js_content` 提取),无额外依赖

---

## 支持的 URL 格式

### X
- `https://x.com/username/status/123456789`
- `https://twitter.com/username/status/123456789`

### 微信公众号
- `https://mp.weixin.qq.com/s/<id>`
- `https://mp.weixin.qq.com/s?__biz=...&mid=...&idx=...`(扩展格式)

## 限制

- 依赖第三方 API(fxtwitter)抓 X,可能因服务变更而失效
- 私密账号的内容 / 需登录的微信付费文章无法抓取
- 部分媒体内容可能无法获取完整 URL

## License

MIT

---

## 📱 关注作者 / Follow Me

如果这个仓库对你有帮助,欢迎关注我。后面我会持续更新更多 AI Skill、X/Twitter 工具、微信文章工作流和内容抓取自动化。

If this repo helped you, follow me for more AI skills, X/Twitter tools, WeChat workflows, content scraping, and automation ideas.

- X (Twitter): [@xiaoerzhan](https://x.com/xiaoerzhan)
- 微信公众号 / WeChat Official Account: 扫码关注 / Scan to follow

<p align="center">
  <img src="./follow-wechat-qrcode.jpg" alt="Jane WeChat Official Account QR code" width="300" />
</p>

<p align="center"><strong>中文:</strong>欢迎关注我的公众号,一起研究 AI Skill、推文抓取、微信文章工作流和内容自动化实践。</p>

<p align="center"><strong>English:</strong> Follow my WeChat Official Account for more AI skills, X/Twitter scraping tools, WeChat content workflows, and automation ideas.</p>
