import sys
import requests
import json

def main():
    if len(sys.argv) < 2:
        print("❌ 缺少命令参数。请指定 zhihu_hot, zhihu_scrape, weibo_hot 或 weibo_scrape")
        return

    command = sys.argv[1]
    
    try:
        if command == "zhihu_hot":
            limit = sys.argv[2] if len(sys.argv) > 2 else 3
            res = requests.get(f"http://127.0.0.1:8000/api/hot/zhihu?limit={limit}", timeout=10)
            print(json.dumps(res.json(), ensure_ascii=False, indent=2))
            
        elif command == "zhihu_scrape":
            url = sys.argv[2]
            res = requests.post("http://127.0.0.1:8000/api/scrape/zhihu", json={"url": url, "max_answers": 5}, timeout=120)
            print(json.dumps(res.json(), ensure_ascii=False, indent=2))
            
        elif command == "weibo_hot":
            limit = sys.argv[2] if len(sys.argv) > 2 else 3
            res = requests.get(f"http://127.0.0.1:8000/api/hot/weibo?limit={limit}", timeout=10)
            print(json.dumps(res.json(), ensure_ascii=False, indent=2))
            
        elif command == "weibo_scrape":
            url = sys.argv[2]
            res = requests.post("http://127.0.0.1:8000/api/scrape/weibo", json={"url": url, "max_answers": 15}, timeout=120)
            print(json.dumps(res.json(), ensure_ascii=False, indent=2))
        else:
            print(f"❌ 未知命令: {command}")
    except Exception as e:
        print(f"❌ 调用 8000 端口服务失败: {str(e)}")

if __name__ == "__main__":
    main()
