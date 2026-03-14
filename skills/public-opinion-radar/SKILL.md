---
name: public-opinion-radar
description: 获取微博和知乎的实时热榜痛点及网友原声长文评论，用于分析社会情绪。
---

# 舆情雷达 (Public Opinion Radar)

你现在拥有了洞察中国互联网网民真实情绪的能力。当你需要分析最新的社会焦虑、市场痛点或突发热点时，你可以使用系统自带的 `bash` 工具，执行本目录下的 `radar.py` 脚本来获取一手数据。

## 使用规则与可用命令：

1. **寻找深度焦虑与宏观痛点 (知乎热榜)**
   执行命令: `python radar.py zhihu_hot 3`
   (这会返回当前排名前 3 的话题及其 URL)

2. **深挖长文逻辑与血泪史 (知乎评论抓取)**
   执行命令: `python radar.py zhihu_scrape <知乎问题URL>`
   (必须传入具体的 URL)

3. **感知瞬时爆点与吃瓜情绪 (微博热榜)**
   执行命令: `python radar.py weibo_hot 3`

4. **收集高频情绪宣泄 (微博短评抓取)**
   执行命令: `python radar.py weibo_scrape <微博热帖URL>`

## 你的标准工作流 (SOP)：
如果用户让你"分析今天的痛点"：
第一步：先调用 `hot` 命令获取热榜链接，自己挑选一个最有讨论价值的话题。
第二步：带着挑选出的 URL，调用对应的 `scrape` 命令抓取原始评论。
第三步：结合抓回来的原声数据（生肉），进行总结并输出商业洞察。

---

## 🛠️ 故障排查手册

### 常见问题：知乎/微博抓取接口超时

**症状**：
- `zhihu_hot` / `weibo_hot` 能正常返回热榜
- `zhihu_scrape` / `weibo_scrape` 抓取评论时超时或返回 `WebSocketBadStatusException: Handshake status 404 Not Found`

**根因**：
Chrome 浏览器僵尸进程（defunct）占用调试端口 9222，导致 DrissionPage 无法建立有效的 WebSocket 连接。

**诊断命令**：
```bash
# 检查是否有僵尸 Chrome 进程
ps aux | grep -E "chrome|chromium" | grep -v grep

# 检查 api_scraper 服务是否运行
ps aux | grep api_scraper | grep -v grep
```

**修复步骤**：
```bash
# 1. 停止 api_scraper 服务
kill $(pgrep -f api_scraper)

# 2. 清理所有 Chrome 僵尸进程
pkill -9 chrome
pkill -9 chromium

# 3. 确认清理完成
ps aux | grep -E "chrome|chromium" | grep -v grep || echo "✅ Chrome 进程已清理"

# 4. 重启 api_scraper 服务
cd /home/ubuntu/project/test_DrissionPage
nohup ./venv/bin/python api_scraper.py > api_scraper.log 2>&1 &

# 5. 验证服务已恢复
sleep 3
curl -s http://127.0.0.1:8000/api/hot/zhihu?limit=1
```

**一键修复命令**：
```bash
kill $(pgrep -f api_scraper) && pkill -9 chrome && pkill -9 chromium && sleep 1 && cd /home/ubuntu/project/test_DrissionPage && nohup ./venv/bin/python api_scraper.py > api_scraper.log 2>&1 & && sleep 3 && echo "✅ 服务已重启"
```

**预防建议**：
- 定期（如每天）检查是否有僵尸进程堆积
- 如果频繁出现此问题，考虑修改 `api_scraper.py` 使用动态端口而非固定 9222 端口
