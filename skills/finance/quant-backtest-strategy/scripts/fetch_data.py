# -*- coding: utf-8 -*-
"""
数据获取工具 — 从 Yahoo Finance 获取股票日K数据
输出JSON格式，供 onequant_lite.py 读取

用法（由 AI Agent 调用）：
  python fetch_data.py --code 601991
  python fetch_data.py --code 600519 --name 贵州茅台
"""
import sys, os, json
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 数据缓存目录
DATA_DIR = os.path.join(os.path.dirname(__file__), "stock_data")
os.makedirs(DATA_DIR, exist_ok=True)

def save_data(code, name, closes):
    """保存股票数据为JSON"""
    data = {
        "code": code,
        "name": name,
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "closes": closes,
    }
    path = os.path.join(DATA_DIR, f"{code}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

def load_data(code):
    """读取缓存的股票数据"""
    path = os.path.join(DATA_DIR, f"{code}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def list_cached():
    """列出所有缓存的股票"""
    files = os.listdir(DATA_DIR)
    stocks = []
    for f in files:
        if f.endswith(".json"):
            data = load_data(f.replace(".json", ""))
            if data:
                stocks.append((data["code"], data["name"], data["updated"]))
    return stocks

def parse_yahoo_json(yahoo_json_str):
    """解析 Yahoo Finance API 返回的 JSON，提取收盘价"""
    try:
        data = json.loads(yahoo_json_str) if isinstance(yahoo_json_str, str) else yahoo_json_str
        result = data["chart"]["result"][0]
        quotes = result["indicators"]["quote"][0]
        closes = quotes["close"]
        # 过滤掉 None 值
        closes = [c for c in closes if c is not None]
        meta = result["meta"]
        return {
            "code": meta["symbol"],
            "name": meta.get("longName", meta["symbol"]),
            "price": meta["regularMarketPrice"],
            "high_52w": meta.get("fiftyTwoWeekHigh"),
            "low_52w": meta.get("fiftyTwoWeekLow"),
            "closes": closes,
            "timestamps": result["timestamp"],
        }
    except Exception as e:
        raise ValueError(f"解析Yahoo数据失败: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="股票数据获取工具")
    parser.add_argument("--code", type=str, help="股票代码（A股加后缀.SS或.SZ）")
    parser.add_argument("--name", type=str, default="", help="股票名称")
    parser.add_argument("--list", action="store_true", help="列出已缓存股票")
    parser.add_argument("--load", type=str, help="读取缓存数据")
    args = parser.parse_args()

    if args.list:
        stocks = list_cached()
        if stocks:
            print("已缓存的股票数据:")
            for code, name, updated in stocks:
                print(f"  {code} {name} (更新: {updated})")
        else:
            print("暂无缓存数据")
        sys.exit(0)

    if args.load:
        data = load_data(args.load)
        if data:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"未找到 {args.load} 的缓存数据")
        sys.exit(0)

    if args.code:
        print(f"请通过 web_fetch 获取数据:")
        print(f"  URL: https://query1.finance.yahoo.com/v8/finance/chart/{args.code}?range=6mo&interval=1d")
        print(f"  获取后，将JSON保存到 {DATA_DIR}/{args.code}.json")
        print(f"  或让 AI Agent 自动完成此操作")
