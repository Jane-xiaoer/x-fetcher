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
python fetch_x.py <x_url> [--save-md]
```

### 示例

```bash
# 抓取普通推文
python fetch_x.py "https://x.com/elonmusk/status/123456789"

# 抓取 X Article 长文章
python fetch_x.py "https://x.com/thedankoe/status/2010751592346030461"

# 抓取并直接保存为 Markdown 文件
python fetch_x.py "https://x.com/elonmusk/status/123456789" --save-md
```

### 保存为 Markdown

抓取成功后，程序会询问是否保存为 Markdown 文件：
- 输入 `y` 或 `yes` 保存
- 输入 `n` 或 `no` 跳过

也可以使用 `--save-md` 参数直接保存，无需交互确认。

生成的文件名格式：`{用户名}_{推文ID}_{时间戳}.md`

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
