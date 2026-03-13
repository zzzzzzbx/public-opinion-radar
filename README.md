# 舆情雷达 (Public Opinion Radar)

🔍 **实时抓取知乎、微博热榜，洞察中国互联网社会情绪与痛点**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd public-opinion-radar
pip install -r requirements.txt
```

### 2. 准备 Cookie（可选但推荐）

**知乎 Cookie：**
1. 浏览器登录 https://www.zhihu.com
2. F12 → Application → Cookies → 复制 `zhihu.com` 的所有 Cookie
3. 保存为 `zhihu_cookies.json`

**微博 Cookie：**
1. 浏览器登录 https://weibo.com
2. F12 → Application → Cookies → 复制 `weibo.com` 的所有 Cookie
3. 保存为 `weibo_cookies.json`

### 3. 启动 API 服务

```bash
python api_scraper.py
```

服务将在 `http://127.0.0.1:8000` 启动

### 4. 使用命令行工具

```bash
# 获取知乎热榜 Top 5
python radar.py zhihu_hot 5

# 获取微博热搜 Top 5
python radar.py weibo_hot 5

# 抓取知乎问题下的深度评论
python radar.py zhihu_scrape "https://www.zhihu.com/question/123456"

# 抓取微博话题下的评论
python radar.py weibo_scrape "https://weibo.com/1234567890/AbCdEfGhI"
```

---

## ✨ 功能特性

### ✅ 已实现

- **知乎热榜实时抓取** — 获取当前最热门的讨论话题
- **微博热搜实时抓取** — 追踪瞬时爆点和社会热点
- **知乎评论深度抓取** — 提取高赞长文评论，洞察用户真实观点
- **微博评论抓取** — 收集高频情绪宣泄和短评
- **Cookie 注入** — 绕过登录验证，获取完整内容
- **语义化提取** — 使用 `itemprop="text"` 无视前端类名混淆，抗更新
- **错误处理完善** — 自动截图调试，完整日志输出

### 📋 计划中（欢迎贡献 PR）

- [ ] 支持分类筛选（科技/财经/社会等）
- [ ] 关键词监控与告警
- [ ] 情感分析（正面/中性/负面）
- [ ] 支持更多平台（豆瓣、虎扑、小红书）
- [ ] 数据导出（CSV/JSON/Excel）
- [ ] Docker 容器化部署

---

## 📖 API 文档

启动服务后访问 `http://127.0.0.1:8000/docs` 查看完整的 Swagger API 文档。

### 主要接口

#### 获取热榜

```bash
GET /api/hot/zhihu?limit=5
GET /api/hot/weibo?limit=5
```

**响应示例：**
```json
{
  "status": "success",
  "count": 5,
  "data": [
    {
      "title": "话题标题",
      "url": "https://..."
    }
  ]
}
```

#### 抓取评论

```bash
POST /api/scrape/zhihu
POST /api/scrape/weibo
```

**请求体：**
```json
{
  "url": "https://...",
  "max_answers": 5
}
```

---

## 🛠 技术栈

- **后端框架**: FastAPI
- **浏览器自动化**: DrissionPage（比 Selenium 更轻量、更快速）
- **HTTP 客户端**: Requests
- **数据验证**: Pydantic

---

## 📁 项目结构

```
public-opinion-radar/
├── api_scraper.py          # FastAPI 后端服务
├── radar.py                # 命令行工具
├── requirements.txt        # Python 依赖
├── SKILL.md               # OpenClaw Skill 文档
├── README.md              # 本文件
├── zhihu_cookies.json     # 知乎 Cookie（需自行准备）
├── weibo_cookies.json     # 微博 Cookie（需自行准备）
└── README.md              # 本文件
```

---

## 💡 使用场景

### 1. 社会痛点分析
每天早上抓取热榜，识别当前社会焦虑和痛点，用于：
- 创业方向调研
- 市场机会发现
- 政策趋势分析

### 2. 舆情监控
监控特定话题的讨论热度，用于：
- 品牌声誉管理
- 危机公关预警
- 竞品动态追踪

### 3. 用户研究
抓取用户对某产品的真实评价，用于：
- 产品改进建议
- 用户需求洞察
- 市场定位调整

### 4. 内容创作
追踪热点话题，用于：
- 自媒体选题
- 内容营销策划
- SEO 关键词优化

---

## ⚠️ 注意事项

1. **Cookie 有效期** — Cookie 会过期（通常 7-30 天），过期后需要重新获取
2. **请求频率** — 建议不要高频调用，避免被封 IP
3. **合法合规** — 请遵守各平台的使用条款，仅用于合法用途
4. **数据使用** — 抓取的数据仅供个人研究和数据分析，请勿用于商业用途

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境搭建

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/public-opinion-radar.git
cd public-opinion-radar

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行服务
python api_scraper.py
```

---

## 📄 开源协议

MIT License — 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [DrissionPage](https://github.com/g1879/DrissionPage) — 强大的浏览器自动化工具
- [FastAPI](https://fastapi.tiangolo.com/) — 现代高性能 Web 框架
- 感谢所有贡献者和使用者

---

## 📬 联系方式

- **作者**: [你的名字]
- **Email**: [你的邮箱]
- **GitHub**: [你的 GitHub 主页]

---

**⭐ 如果这个项目对你有帮助，请给一个 Star！**
