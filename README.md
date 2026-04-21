# X Fetcher

抓取 X (Twitter) 帖子内容的命令行工具。支持普通推文和 X Article 长文章。

## 功能

- 抓取普通推文（文字、图片、视频链接）
- 抓取 X Article 长文章（完整正文，Markdown 格式）
- 获取互动数据（点赞、转发、浏览量、书签数）

## 安装

```bash
git clone https://github.com/Jane-xiaoer/x-fetcher.git
cd x-fetcher
pip install requests
```

## 使用

```bash
python fetch_x.py <x_url> [选项]
```

### 选项

| 选项 | 说明 |
|------|------|
| `--save-md` | 直接保存主贴为 Markdown |
| `--with-replies` | 同时抓取评论 |
| `--full` | 保存完整归档（主贴+评论） |
| `--json` | 仅输出 JSON，不保存文件 |

### 示例

```bash
# 交互模式（推荐）- 会询问你要保存哪些内容
python fetch_x.py "https://x.com/elonmusk/status/123456789"

# 抓取 X Article 长文章
python fetch_x.py "https://x.com/thedankoe/status/2010751592346030461"

# 直接保存主贴为 Markdown
python fetch_x.py "https://x.com/elonmusk/status/123456789" --save-md

# 保存完整归档（主贴 + 评论）
python fetch_x.py "https://x.com/elonmusk/status/123456789" --full

# 仅输出 JSON（包含评论）
python fetch_x.py "https://x.com/elonmusk/status/123456789" --json --with-replies
```

### 交互模式

不带参数运行时，抓取成功后会显示菜单让你选择：

```
📋 抓取成功！请选择要保存的内容：
==================================================

  [1] 仅保存主贴内容
  [2] 仅保存评论/回复
  [3] 保存主贴 + 评论（完整归档）
  [4] 仅输出 JSON（不保存文件）
  [0] 退出

请输入选项 (0-4):
```

### 生成的文件

文件名格式：`{用户名}_{推文ID}_{类型}_{时间戳}.md`

- `_post_` - 仅主贴
- `_replies_` - 仅评论
- `_full_` - 完整归档

## 输出格式

### 普通推文

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

### X Article 长文章

```json
{
  "source": "fxtwitter",
  "success": true,
  "type": "article",
  "content": {
    "title": "文章标题",
    "preview": "文章预览...",
    "full_text": "完整文章内容（Markdown格式）...",
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

## 支持的 URL 格式

- `https://x.com/username/status/123456789`
- `https://twitter.com/username/status/123456789`

## 工作原理

1. 从 URL 提取 tweet ID
2. 尝试 fxtwitter API（支持 Article）
3. 备选 syndication API
4. 解析并格式化输出

## 限制

- 依赖第三方 API（fxtwitter），可能因服务变更而失效
- 私密账号的内容无法抓取
- 部分媒体内容可能无法获取完整 URL

## License

MIT

---

## 📱 关注作者 / Follow Me

如果这个仓库对你有帮助，欢迎关注我。后面我会持续更新更多 AI Skill、X/Twitter 工具、内容抓取和自动化工作流。

If this repo helped you, follow me for more AI skills, X/Twitter tools, content workflows, and automation ideas.

- X (Twitter): [@xiaoerzhan](https://x.com/xiaoerzhan)
- 微信公众号 / WeChat Official Account: 扫码关注 / Scan to follow

<p align="center">
  <img src="./follow-wechat-qrcode.jpg" alt="Jane WeChat Official Account QR code" width="300" />
</p>

<p align="center"><strong>中文：</strong>欢迎关注我的公众号，一起研究 AI Skill、推文抓取、内容处理和自动化实践。</p>

<p align="center"><strong>English:</strong> Follow my WeChat Official Account for more AI skills, X/Twitter scraping tools, content workflows, and automation ideas.</p>
