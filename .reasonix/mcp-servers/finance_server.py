"""
金融数据 MCP Server
基于 akshare 提供 A股/基金/汇率等数据查询
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import json
from datetime import datetime
import requests

# 全局 requests session，绕过系统代理直连
_http = requests.Session()
_http.trust_env = False
_http.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

server = Server("finance-data")

PREFIX_MAP = {
    "0": "sz", "1": "sh", "2": "sz", "3": "sz",
    "5": "sz", "6": "sh", "8": "bj", "9": "sh",
}

def _detect_prefix(code: str) -> str:
    """根据股票代码首位数判断交易所前缀"""
    first = code[0]
    return PREFIX_MAP.get(first, "sh")


def _sina_realtime(symbol: str) -> list[dict]:
    """通过 Sina 财经 API 获取实时行情（绕过系统代理）"""
    symbols = [s.strip() for s in symbol.split(",")]
    # 拼接 sina 请求参数: sh600519,sz000001,...
    sina_codes = []
    for s in symbols:
        prefix = _detect_prefix(s)
        sina_codes.append(f"{prefix}{s}")

    url = f"http://hq.sinajs.cn/list={','.join(sina_codes)}"
    resp = _http.get(url, headers={"Referer": "https://finance.sina.com.cn"}, timeout=15)
    resp.encoding = "gbk"
    results = []
    for line in resp.text.strip().split("\n"):
        if not line.strip():
            continue
        try:
            # var hq_str_sh601991="大唐发电,7.910,7.990,8.090,8.200,7.800,8.080,8.090,...";
            data = line.split('"')[1].split(",")
            code_full = line.split("_")[1].split("=")[0]
            code = code_full[2:]  # 去掉 sh/sz 前缀
            name = data[0]
            open_p = _f(data[1])
            last_close = _f(data[2])
            price = _f(data[3])
            high = _f(data[4])
            low = _f(data[5])
            bid = _f(data[6])
            ask = _f(data[7])
            volume = _f(data[8])       # 手
            amount = _f(data[9])        # 元
            change = round(price - last_close, 3) if price and last_close else 0
            pct = round((change / last_close) * 100, 2) if last_close else 0
            # 换手率 sina 不直接提供，设为 0
            results.append({
                "代码": code,
                "名称": name,
                "最新价": price if price else 0,
                "涨跌幅": pct,
                "涨跌额": change,
                "成交量": volume if volume else 0,
                "成交额": amount if amount else 0,
                "换手率": 0,
                "最高": high if high else 0,
                "最低": low if low else 0,
                "今开": open_p if open_p else 0,
                "昨收": last_close if last_close else 0,
            })
        except (IndexError, ValueError):
            continue
    return results


def _f(val: str) -> float:
    """安全转浮点"""
    try:
        return float(val) if val else 0.0
    except ValueError:
        return 0.0


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="stock_realtime",
            description="获取A股实时行情（支持多个股票，用逗号分隔）",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "股票代码，如 '600519' 或 '000001,600519,000333'"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="fund_realtime",
            description="获取基金实时估值",
            inputSchema={
                "type": "object",
                "properties": {
                    "fund_code": {
                        "type": "string",
                        "description": "基金代码，如 '000001'"
                    }
                },
                "required": ["fund_code"]
            }
        ),
        Tool(
            name="index_realtime",
            description="获取主要指数实时行情（上证、深证、创业板等）",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="fx_realtime",
            description="获取主要货币对实时汇率（在岸人民币）",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "stock_realtime":
        symbol = arguments["symbol"]
        try:
            result = _sina_realtime(symbol)
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    elif name == "fund_realtime":
        try:
            import akshare as ak
        except ImportError:
            return [TextContent(type="text", text=json.dumps({"error": "akshare 未安装，请 pip install akshare"}, ensure_ascii=False))]
        fund_code = arguments["fund_code"]
        try:
            df = ak.fund_etf_spot_em()
            row = df[df["代码"] == fund_code]
            if not row.empty:
                r = row.iloc[0]
                result = {
                    "代码": str(r["代码"]),
                    "名称": r["名称"],
                    "最新价": float(r["最新价"]),
                    "涨跌幅": float(r["涨跌幅"]),
                    "成交额": float(r.get("成交额", 0))
                }
            else:
                result = {"info": f"未找到基金 {fund_code}"}
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    elif name == "index_realtime":
        try:
            import akshare as ak
        except ImportError:
            return [TextContent(type="text", text=json.dumps({"error": "akshare 未安装"}, ensure_ascii=False))]
        try:
            df = ak.stock_zh_index_spot_em()
            result = []
            for _, r in df.iterrows():
                result.append({
                    "指数": r["指数名称"],
                    "最新价": float(r["最新价"]),
                    "涨跌幅": float(r["涨跌幅"]),
                    "涨跌额": float(r["涨跌额"])
                })
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]

    elif name == "fx_realtime":
        try:
            import akshare as ak
        except ImportError:
            return [TextContent(type="text", text=json.dumps({"error": "akshare 未安装"}, ensure_ascii=False))]
        try:
            df = ak.currency_boc_sina()
            result = []
            for _, r in df.iterrows():
                result.append({
                    "货币对": r["货币对"],
                    "现汇买入价": float(r.get("现汇买入价", 0)),
                    "现钞买入价": float(r.get("现钞买入价", 0)),
                    "现汇卖出价": float(r.get("现汇卖出价", 0)),
                    "现钞卖出价": float(r.get("现钞卖出价", 0))
                })
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
