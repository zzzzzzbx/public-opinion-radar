from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from DrissionPage import ChromiumPage, ChromiumOptions
import json
import time
import traceback  # 用于在服务端打印完整的报错追踪
import re

app = FastAPI(title="OpenClaw Data Scraper API")

class ZhihuRequest(BaseModel):
    url: str
    max_answers: int = 5

@app.post("/api/scrape/zhihu")
def scrape_zhihu_endpoint(request: ZhihuRequest):
    print(f"\n🔗 收到 OpenClaw 抓取请求: {request.url}")
    
    co = ChromiumOptions()
    co.set_browser_path('/opt/google/chrome/chrome') 
    co.set_local_port(9222) 
    co.set_argument('--headless=new')  
    co.set_argument('--no-sandbox')    
    co.set_argument('--disable-gpu')   
    co.set_argument('--window-size=1920,1080') 
    co.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        page = ChromiumPage(co)
        
        # 1. 初始化域名环境（防重定向机制）
        print("正在初始化知乎主域名环境...")
        page.get('https://www.zhihu.com')
        time.sleep(1) 
        
        # 2. 注入 Cookie
        print("正在注入身份凭证...")
        try:
            with open('zhihu_cookies.json', 'r', encoding='utf-8') as f:
                cookies_list = json.load(f)
                for cookie in cookies_list:
                    page.set.cookies(cookie)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cookie 注入失败: {e}")

        # 3. 访问目标问题页面
        print(f"正在访问目标问题: {request.url}")
        page.get(request.url)
        page.wait.load_start()
        time.sleep(1)
        
        # 4. 滚动页面触发动态加载
        print("开始向下滚动以加载回答...")
        for _ in range(3):
            page.scroll.down(600)  
            time.sleep(1.5)        

        # 5. 暴力点击展开长文
        print("正在寻找并点击展开按钮...")
        expand_buttons = page.eles('text:阅读全文') 
        for btn in expand_buttons:
            try:
                btn.click() 
                time.sleep(0.5) 
            except Exception:
                pass

        # 6. 降维打击：利用 SEO 语义标签提取，无视前端类名混淆
        print("正在提取正文内容...")
        # 寻找 itemprop="text" 这个专供搜索引擎看的属性，极其稳定
        if page.wait.eles_loaded('@itemprop=text', timeout=5):
            all_answers = page.eles('@itemprop=text')
            results = []
            
            for ele in all_answers:
                try:
                    text_content = ele.text
                    if text_content and len(text_content.strip()) > 50:
                        clean_text = text_content.replace('收起', '').replace('阅读全文', '').strip()
                        results.append(clean_text)
                        
                    if len(results) >= request.max_answers:
                        break
                except Exception as inner_e:
                    continue
            
            return {
                "status": "success",
                "count": len(results),
                "data": results
            }
        else:
            error_title = page.title
            page.get_screenshot(path='api_error_debug.png')
            # 【修复】直接 return 错误字典，不抛异常了，防止被外层的 except Exception 拦截
            return {"status": "error", "detail": f"未找到正文(itemprop)。当前标题:[{error_title}]。"}
            
    except Exception as e:
        # 如果是 HTTPException 就直接抛出，不拦截
        if isinstance(e, HTTPException):
            raise e
        print("❌ 服务端捕获到严重错误，完整堆栈如下:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))
    finally:
        if 'page' in locals():
            page.quit()
            print("浏览器进程已安全清理。")

# ==========================================
# 新增：微博抓取接口 (使用高阶的数据包拦截技术)
# ==========================================
class WeiboRequest(BaseModel):
    url: str
    max_answers: int = 15 # 微博评论比较短，默认多抓一点

@app.post("/api/scrape/weibo")
def scrape_weibo_endpoint(request: WeiboRequest):
    print(f"\n🔗 收到 OpenClaw 抓取请求: {request.url}")
    
    co = ChromiumOptions()
    co.set_browser_path('/opt/google/chrome/chrome') 
    co.set_local_port(9222) 
    co.set_argument('--headless=new')  
    co.set_argument('--no-sandbox')    
    co.set_argument('--disable-gpu')   
    co.set_argument('--window-size=1920,1080') 
    co.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        page = ChromiumPage(co)
        
        # 1. 初始化微博域名环境
        print("正在初始化微博主域名环境...")
        page.get('https://weibo.com')
        time.sleep(1) 
        
        # 2. 注入微博 Cookie
        print("正在注入微博身份凭证...")
        try:
            with open('weibo_cookies.json', 'r', encoding='utf-8') as f:
                cookies_list = json.load(f)
                for cookie in cookies_list:
                    page.set.cookies(cookie)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"微博 Cookie 注入失败，请检查 weibo_cookies.json: {e}")

        # 3. 开启上帝视角：监听微博拉取评论的底层数据包！
        # 桌面版微博拉取评论的内部接口 URL 通常包含 'buildComments'
        print("正在开启底层数据包雷达...")
        page.listen.start('buildComments')

        # 4. 访问目标微博页面
        print(f"正在访问目标微博: {request.url}")
        page.get(request.url)
        page.wait.load_start()
        
        # 5. 向下滚动，强行刺激微博前端去向服务器请求评论数据
        print("滚动页面，刺激前端发送评论请求...")
        page.scroll.down(800)
        time.sleep(1)

        # 6. 核心：守株待兔，拦截数据包
        print("正在拦截并解析 JSON 数据包...")
        # 等待目标数据包出现，最多等 5 秒
        packet = page.listen.wait(timeout=5)
        
        if packet:
            # 降维打击：直接拿到后端传给前端的原生 JSON 字典！里面没有任何多余的 HTML 标签！
            res_json = packet.response.body
            results = []
            
            # 剥洋葱：解析微博的 JSON 结构
            if 'data' in res_json:
                comments_list = res_json['data']
                for c in comments_list:
                    # 微博的新版接口非常贴心，直接提供了一个叫 'text_raw' 的纯文本字段
                    text_content = c.get('text_raw') or c.get('text', '')
                    
                    # 简单清洗一下（去除去掉自带的表情包标记 [doge] 等，看你需求，这里先保留文字）
                    clean_text = re.sub(r'<[^>]+>', '', text_content).strip()
                    
                    if clean_text:
                        results.append(clean_text)
                        
                    if len(results) >= request.max_answers:
                        break
                        
            return {
                "status": "success",
                "count": len(results),
                "data": results
            }
        else:
            error_title = page.title
            page.get_screenshot(path='weibo_error_debug.png')
            return {"status": "error", "detail": f"未能拦截到评论数据包。当前标题:[{error_title}]。"}
            
    except Exception as e:
        print("❌ 微博抓取服务端捕获到错误:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))
    finally:
        if 'page' in locals():
            page.listen.stop() # 记得关掉监听
            page.quit()
            
@app.get("/api/hot/zhihu")
def get_zhihu_hotlist(limit: int = 5):
    print("\n📡 OpenClaw 正在扫描知乎实时热榜...")
    
    co = ChromiumOptions()
    co.set_browser_path('/opt/google/chrome/chrome') 
    co.set_local_port(9222) 
    co.set_argument('--headless=new')  
    co.set_argument('--no-sandbox')    
    co.set_argument('--disable-gpu')   
    co.set_argument('--window-size=1920,1080') 
    co.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        page = ChromiumPage(co)
        
        # 1. 初始化并注入 Cookie（核心修复点：带着通行证去看热榜）
        print("正在初始化并注入 Cookie...")
        page.get('https://www.zhihu.com')
        time.sleep(1) 
        try:
            with open('zhihu_cookies.json', 'r', encoding='utf-8') as f:
                cookies_list = json.load(f)
                for cookie in cookies_list:
                    page.set.cookies(cookie)
        except Exception as e:
            print(f"⚠️ Cookie 注入失败: {e}")

        # 2. 访问知乎热榜
        page.get('https://www.zhihu.com/hot')
        page.wait.load_start()
        time.sleep(1.5) # 给一点渲染时间
        
        print("正在解析热榜数据...")
        # 3. 兼容主流热榜外壳 .HotItem
        if page.wait.eles_loaded('.HotItem', timeout=5):
            hot_items = page.eles('.HotItem')
            hot_list = []
            
            for item in hot_items:
                try:
                    # 热榜的标题通常在 h2 标签里
                    title_ele = item.ele('tag:h2', timeout=0.5)
                    if not title_ele:
                        continue
                    title = title_ele.text
                    
                    # 提取链接
                    link_ele = item.ele('tag:a', timeout=0.5)
                    href = link_ele.attr('href')
                    
                    # 只抓取正经的问题，并去掉 URL 后面的追踪参数（?utm_source=...）
                    if href and '/question/' in href:
                        clean_url = href.split('?')[0]
                        hot_list.append({
                            "title": title,
                            "url": clean_url
                        })
                        
                    if len(hot_list) >= limit:
                        break
                except Exception:
                    continue
                    
            print(f"✅ 成功扫描到 {len(hot_list)} 条热榜问题！")
            return {
                "status": "success",
                "count": len(hot_list),
                "data": hot_list
            }
        else:
            # 4. 终极探头：如果还是找不到，立刻截图！
            error_title = page.title
            page.get_screenshot(path='hotlist_error_debug.png')
            return {"status": "error", "detail": f"未找到热榜(HotItem)。当前标题:[{error_title}]。已保存截图 hotlist_error_debug.png。"}
            
    except Exception as e:
        print("❌ 热榜获取失败:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))
    finally:
        if 'page' in locals():
            page.quit()

# ==========================================
# 新增：微博热点流雷达接口 (XHR 数据包拦截流派)
# ==========================================
@app.get("/api/hot/weibo")
def get_weibo_hotlist(limit: int = 5):
    print("\n📡 OpenClaw 正在扫描微博实时热点流...")
    
    co = ChromiumOptions()
    co.set_browser_path('/opt/google/chrome/chrome') 
    co.set_local_port(9222) 
    co.set_argument('--headless=new')  
    co.set_argument('--no-sandbox')    
    co.set_argument('--disable-gpu')   
    co.set_argument('--window-size=1920,1080') 
    co.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        page = ChromiumPage(co)
        
        # 1. 注入 Cookie
        print("正在初始化并注入微博 Cookie...")
        page.get('https://weibo.com')
        time.sleep(1) 
        try:
            with open('weibo_cookies.json', 'r', encoding='utf-8') as f:
                cookies_list = json.load(f)
                for cookie in cookies_list:
                    page.set.cookies(cookie)
        except Exception as e:
            print(f"⚠️ 微博 Cookie 注入失败: {e}")

        # 2. 开启上帝视角：监听所有 ajax 请求
        print("正在开启底层数据包雷达...")
        page.listen.start('ajax')  # 放大监听范围

        # 3. 访问页面触发数据加载
        print("正在截获热门微博数据...")
        page.get('https://weibo.com/hot')

        # 4. 【核心修复】：持续遍历拦截到的数据包，直到找到我们要的“运钞车”
        hot_list = []
        for packet in page.listen.steps(timeout=5):
            res_json = packet.response.body
            
            # 排除非 JSON 格式的垃圾包
            if not isinstance(res_json, dict):
                continue
                
            # 兼容微博后端多变的 JSON 嵌套格式
            statuses = []
            if 'statuses' in res_json:
                statuses = res_json['statuses']
            elif 'data' in res_json and isinstance(res_json['data'], dict) and 'statuses' in res_json['data']:
                statuses = res_json['data']['statuses']
            elif 'data' in res_json and isinstance(res_json['data'], list):
                statuses = res_json['data']

            # 如果这个数据包里发现了我们要的帖子数组
            if statuses:
                print(f"🎯 成功定位到包含 {len(statuses)} 条数据的核心数据包！")
                for s in statuses:
                    text_raw = s.get('text_raw') or s.get('text', '')
                    uid = s.get('user', {}).get('id', '') or s.get('user', {}).get('idstr', '')
                    mblogid = s.get('mblogid', '') or s.get('bid', '')
                    
                    if uid and mblogid and text_raw:
                        # 深度清洗：去掉 HTML 标签、超链接和换行
                        clean_text = re.sub(r'<[^>]+>', '', text_raw)
                        clean_title = re.sub(r'http\S+', '', clean_text).replace('\n', ' ').strip()
                        
                        if not clean_title:
                            continue
                            
                        title = clean_title[:40] + '...' if len(clean_title) > 40 else clean_title
                        post_url = f"https://weibo.com/{uid}/{mblogid}"
                        
                        # 查重：防止同一个包里有重复的帖子
                        if not any(item['url'] == post_url for item in hot_list):
                            hot_list.append({
                                "title": title,
                                "url": post_url
                            })
                            
                    if len(hot_list) >= limit:
                        break
                        
            # 只要抓满了指定数量，立刻跳出巡飞循环
            if len(hot_list) >= limit:
                break
                
        if hot_list:
            print(f"✅ 成功扫描到 {len(hot_list)} 条热门微博！")
            return {
                "status": "success",
                "count": len(hot_list),
                "data": hot_list
            }
        else:
            error_title = page.title
            page.get_screenshot(path='weibo_hotlist_error.png')
            return {"status": "error", "detail": f"拦截了数据包，但未能解析出帖子状态。当前标题:[{error_title}]。已保存截图。"}
            
    except Exception as e:
        print("❌ 微博热点流获取失败:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))
    finally:
        if 'page' in locals():
            page.listen.stop()
            page.quit()
            

if __name__ == '__main__':
    print("🚀 爬虫 API 服务正在启动...")
    uvicorn.run(app, host="127.0.0.1", port=8000)