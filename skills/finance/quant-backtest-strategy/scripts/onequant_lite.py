# -*- coding: utf-8 -*-
"""
OneQuant Lite — 多股票多策略量化回测工具
模拟 OneQuant REST API 风格，5种策略 + 排行榜输出

用法:
  python onequant_lite.py                          # 默认回测预设股票池
  python onequant_lite.py --symbols 600519,000858  # 指定股票
  python onequant_lite.py --strategy ma            # 指定策略
  python onequant_lite.py --export                 # 导出Excel报告
"""
import sys, json, os
from datetime import datetime
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 输出目录（ponytail: workspace 根下的 output/）
_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "output"))
os.makedirs(_OUTPUT_DIR, exist_ok=True)

# ============================================================
# 预设股票池（A股核心标的）
# ============================================================
PRESET_STOCKS = {
    "601991": "大唐发电",
    "000725": "京东方A",
    "600519": "贵州茅台",
    "000858": "五粮液",
    "300750": "宁德时代",
    "601318": "中国平安",
    "000333": "美的集团",
    "600036": "招商银行",
    "002594": "比亚迪",
    "300059": "东方财富",
    "688981": "中芯国际",
}

# Yahoo Finance 近6月收盘价数据 (2026-01-19 ~ 2026-07-17)
# 通过 web_fetch 从 Yahoo Finance API 获取
STOCK_DATA = {
    "601991": [3.82,3.98,4.01,3.92,3.92,3.95,3.86,3.90,3.84,3.78,3.73,3.72,3.75,3.69,3.72,3.74,3.70,3.72,3.78,3.63,3.75,3.80,3.89,3.99,4.12,4.00,4.00,4.06,4.11,4.06,4.06,4.16,4.58,4.74,4.33,4.25,4.31,4.18,4.20,4.03,4.24,4.46,4.39,4.48,4.13,3.94,3.94,3.84,3.71,3.73,3.84,3.84,3.81,3.83,3.87,3.89,3.87,3.89,3.96,4.11,4.15,4.21,4.07,4.05,4.04,4.29,4.16,4.58,5.04,5.54,6.09,6.70,7.37,7.20,7.92,7.93,8.38,7.54,7.05,6.89,7.40,7.16,7.71,8.00,8.63,8.37,9.18,9.10,8.81,7.93,7.27,7.71,7.76,7.99,8.09,8.73,8.70,9.13,8.22,8.37,8.34,7.82,7.47,7.32,7.04,7.08,7.79,7.33,7.67,7.39,7.00,6.95,6.57,6.64,5.98,5.88,5.78,5.69,5.80],
}

# JSON 数据缓存目录（自动获取的数据优先于此）
_DATA_CACHE_DIR = os.path.join(os.path.dirname(__file__), "stock_data")

def _load_stock_data(code):
    """加载股票数据：优先 JSON 缓存，其次东方财富API，最后内嵌数据"""
    # 尝试 JSON 缓存
    cache_path = os.path.join(_DATA_CACHE_DIR, f"{code}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
            closes = cached.get("closes", [])
            name = cached.get("name", code)
            if closes:
                return closes, name
        except Exception:
            pass
    # 尝试从东方财富获取（通过 web_fetch 或直接API）
    try:
        import urllib.request, ssl
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        market = 1 if code.startswith("6") else 0  # 6xx=沪=1, 0xx/3xx=深=0
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={market}.{code}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20240101&end=20260717"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10, context=ssl_ctx)
        raw = json.loads(resp.read().decode("utf-8"))
        klines = raw["data"]["klines"]
        closes = [float(k.split(",")[2]) for k in klines]
        name = raw["data"].get("name", code)
        # 缓存结果
        os.makedirs(_DATA_CACHE_DIR, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"code": code, "name": name, "closes": closes, "updated": "auto"}, f, ensure_ascii=False, indent=2)
        return closes, name
    except Exception:
        pass
    # 回退内嵌数据
    closes = STOCK_DATA.get(code)
    name = PRESET_STOCKS.get(code, code)
    return closes, name

# ============================================================
# 策略引擎
# ============================================================
class Strategy:
    """策略基类"""
    def __init__(self, name):
        self.name = name

    def generate_signals(self, df):
        raise NotImplementedError

class MAStrategy(Strategy):
    """MA金叉死叉策略"""
    def __init__(self, short=5, long=20):
        super().__init__(f"MA{short}/{long}")
        self.short, self.long = short, long

    def generate_signals(self, df):
        d = df.copy()
        d["fast"] = d["close"].rolling(self.short).mean()
        d["slow"] = d["close"].rolling(self.long).mean()
        d["signal"] = (d["fast"] > d["slow"]).astype(int)
        return d

class RSIStrategy(Strategy):
    """RSI超买超卖策略"""
    def __init__(self, period=14, oversold=30, overbought=70):
        super().__init__(f"RSI({period})")
        self.period, self.oversold, self.overbought = period, oversold, overbought

    def generate_signals(self, df):
        d = df.copy()
        delta = d["close"].diff()
        gain = delta.clip(lower=0).rolling(self.period).mean()
        loss = (-delta.clip(upper=0)).rolling(self.period).mean()
        rs = gain / loss.replace(0, np.nan)
        d["rsi"] = 100 - (100 / (1 + rs))
        d["signal"] = 0
        d.loc[d["rsi"] < self.oversold, "signal"] = 1
        d.loc[d["rsi"] > self.overbought, "signal"] = 0
        return d

class MACDStrategy(Strategy):
    """MACD策略"""
    def __init__(self, fast=12, slow=26, signal=9):
        super().__init__(f"MACD({fast},{slow},{signal})")
        self.fast, self.slow, self.signal = fast, slow, signal

    def generate_signals(self, df):
        d = df.copy()
        ema_f = d["close"].ewm(span=self.fast).mean()
        ema_s = d["close"].ewm(span=self.slow).mean()
        d["macd"] = ema_f - ema_s
        d["macd_signal"] = d["macd"].ewm(span=self.signal).mean()
        d["signal"] = (d["macd"] > d["macd_signal"]).astype(int)
        return d

class BBStrategy(Strategy):
    """布林带策略"""
    def __init__(self, period=20, std=2):
        super().__init__(f"BB({period})")
        self.period, self.std = period, std

    def generate_signals(self, df):
        d = df.copy()
        d["mid"] = d["close"].rolling(self.period).mean()
        d["upper"] = d["mid"] + self.std * d["close"].rolling(self.period).std()
        d["lower"] = d["mid"] - self.std * d["close"].rolling(self.period).std()
        d["signal"] = 0
        d.loc[d["close"] < d["lower"], "signal"] = 1
        d.loc[d["close"] > d["upper"], "signal"] = 0
        # 前 period 天无布林带信号
        d.iloc[:self.period, d.columns.get_loc("signal")] = 0
        return d

class KDJStrategy(Strategy):
    """KDJ 随机指标策略"""
    def __init__(self, period=9, k_smooth=3, d_smooth=3):
        super().__init__(f"KDJ({period},{k_smooth},{d_smooth})")
        self.period, self.k_smooth, self.d_smooth = period, k_smooth, d_smooth

    def generate_signals(self, df):
        d = df.copy()
        low_min = d["close"].rolling(self.period).min()
        high_max = d["close"].rolling(self.period).max()
        rsv = (d["close"] - low_min) / (high_max - low_min).replace(0, np.nan) * 100
        d["kdj_k"] = rsv.ewm(alpha=1/self.k_smooth, adjust=False).mean()
        d["kdj_d"] = d["kdj_k"].ewm(alpha=1/self.d_smooth, adjust=False).mean()
        d["kdj_j"] = 3 * d["kdj_k"] - 2 * d["kdj_d"]
        # K 上穿 D 买入，K 下穿 D 卖出
        d["signal"] = 0
        d.loc[d["kdj_k"] > d["kdj_d"], "signal"] = 1
        d.loc[d["kdj_k"] <= d["kdj_d"], "signal"] = 0
        d.iloc[:self.period + self.k_smooth, d.columns.get_loc("signal")] = 0
        return d

class TurtleStrategy(Strategy):
    """海龟交易法则（唐奇安通道突破）"""
    def __init__(self, entry_period=20, exit_period=10):
        super().__init__(f"海龟({entry_period},{exit_period})")
        self.entry_period, self.exit_period = entry_period, exit_period

    def generate_signals(self, df):
        d = df.copy()
        d["entry_high"] = d["close"].rolling(self.entry_period).max()
        d["exit_low"] = d["close"].rolling(self.exit_period).min()
        d["signal"] = 0
        # 突破20日高点买入
        d.loc[d["close"] > d["entry_high"].shift(1), "signal"] = 1
        # 跌破10日低点卖出
        d.loc[d["close"] < d["exit_low"].shift(1), "signal"] = 0
        d.iloc[:max(self.entry_period, self.exit_period), d.columns.get_loc("signal")] = 0
        return d

class MultiMAStrategy(Strategy):
    """多均线多头排列策略 (MA5 > MA20 > MA60)"""
    def __init__(self, short=5, mid=20, long=60):
        super().__init__(f"多均线({short},{mid},{long})")
        self.short, self.mid, self.long = short, mid, long

    def generate_signals(self, df):
        d = df.copy()
        d["ma_s"] = d["close"].rolling(self.short).mean()
        d["ma_m"] = d["close"].rolling(self.mid).mean()
        d["ma_l"] = d["close"].rolling(self.long).mean()
        d["signal"] = ((d["ma_s"] > d["ma_m"]) & (d["ma_m"] > d["ma_l"])).astype(int)
        d.iloc[:self.long, d.columns.get_loc("signal")] = 0
        return d

class HoldStrategy(Strategy):
    """买入持有（基准）"""
    def __init__(self):
        super().__init__("买入持有")

    def generate_signals(self, df):
        d = df.copy()
        d["signal"] = 1
        return d

# ============================================================
# ASCII 图表
# ============================================================
def ascii_equity_curve(values, width=50, height=12, title=""):
    """绘制 ASCII 资金曲线图"""
    vals = [v for v in values if v is not None and not (isinstance(v, float) and np.isnan(v))]
    if len(vals) < 2:
        return "  数据不足"

    mn, mx = min(vals), max(vals)
    rng = mx - mn if mx > mn else 1
    chars = "\u2500"  # ─
    bar = "\u2502"    # │
    dot = "\u25cf"    # ●
    mid = "\u00b7"    # ·
    result = [f"  {title}  ({mn:.2f} - {mx:.2f})"]
    result.append(f"  {chars}{chars * width}{chars}")

    for row in range(height):
        y = mx - (rng * row / (height - 1))
        line = f"  {bar}"
        for i in range(width):
            idx = int(i * (len(vals) - 1) / (width - 1))
            v = vals[min(idx, len(vals) - 1)]
            if abs(v - y) < rng / height:
                line += dot
            elif v > y:
                line += mid
            else:
                line += " "
        line += bar
        result.append(line)

    result.append(f"  {chars}{chars * width}{chars}")
    return "\n".join(result)

# ============================================================
# 公共计算函数（ponytail: 消除4处重复的指标计算）
# ============================================================
def _calc_metrics(strategy_return):
    """计算策略绩效指标，返回 dict"""
    # ponytail: 4处重复 -> 1个函数。optimize/fusion/risk 模式仍有内联计算，抽完可再省80行
    sr = strategy_return.dropna()
    tr = (1 + sr).prod() - 1
    win = (sr > 0).sum()
    tot = (sr != 0).sum()
    wr = win / tot * 100 if tot else 0
    cum = (1 + sr).cumprod()
    mdd = ((cum - cum.cummax()) / cum.cummax()).min()
    ex = sr - 0.02 / 252
    sp = np.sqrt(252) * ex.mean() / ex.std() if ex.std() > 1e-10 else 0.0
    return {"total_return": tr, "sharpe": sp, "max_drawdown": mdd, "win_rate": wr, "_sr": sr, "_cum": cum}

def _run_strat(base_df, strategy):
    """运行一个策略，返回带 signal/strategy_return/cum 的 DataFrame"""
    df = strategy.generate_signals(base_df)
    df["strategy_return"] = df["signal"].shift(1) * base_df["daily_return"]
    df["cum"] = (1 + df["strategy_return"]).cumprod()
    return df

# ============================================================
# 回测引擎
# ============================================================
def backtest(code, name, closes, strategies):
    """对一只股票运行多个策略，返回结果"""
    dates = pd.date_range(start="2026-01-19", periods=len(closes), freq="B")
    base_df = pd.DataFrame({"close": closes}, index=dates)
    base_df["daily_return"] = base_df["close"].pct_change()
    mr = base_df["close"].iloc[-1] / base_df["close"].iloc[0] - 1

    results = []
    dfs = {}
    for strat in strategies:
        df = _run_strat(base_df, strat)
        df["position"] = df["signal"].diff()
        m = _calc_metrics(df["strategy_return"])
        trades = int(df["position"].abs().sum())
        results.append({
            "code": code, "name": name, "strategy": strat.name,
            "total_return": m["total_return"], "market_return": mr,
            "excess": m["total_return"] - mr, "sharpe": m["sharpe"],
            "max_drawdown": m["max_drawdown"], "win_rate": m["win_rate"],
            "trades": trades, "last_signal": df["signal"].iloc[-1],
            "last_position": df["position"].iloc[-1],
        })
        # 存最佳策略的DataFrame用于图表
        if strat.name not in dfs or m["total_return"] > max(
            r["total_return"] for r in results if r["strategy"] == strat.name
        ):
            df["cum_strategy"] = df["cum"]
            df["cum_market"] = base_df["close"] / base_df["close"].iloc[0]
            dfs[strat.name] = df
    return results, dfs

# ============================================================
# 报告输出
# ============================================================
def print_report(all_results, top_n=10):
    """打印策略排行榜"""
    df = pd.DataFrame(all_results)

    print("=" * 70)
    print(f"  OneQuant Lite — 多策略量化回测报告")
    print(f"  日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  数据: Yahoo Finance (2026-01-19 ~ 2026-07-17)")
    print("=" * 70)

    for strategy in df["strategy"].unique():
        subset = df[df["strategy"] == strategy].sort_values("total_return", ascending=False)
        print(f"\n{'='*70}")
        print(f"  [{strategy}] 策略排行榜")
        print(f"{'='*70}")
        print(f"  {'名次':>3} {'代码':>8} {'名称':<10} {'收益率':>8} {'超额':>8} {'夏普':>6} {'回撤':>8} {'胜率':>6} {'信号':>6}")
        print(f"  {'-'*64}")
        for i, (_, row) in enumerate(subset.head(top_n).iterrows()):
            sig = "持有" if row["last_signal"] == 1 else "空仓"
            print(f"  {i+1:>3} {row['code']:>8} {row['name']:<10} {row['total_return']:>+7.2%} {row['excess']:>+7.2%} {row['sharpe']:>6.2f} {row['max_drawdown']:>7.2%} {row['win_rate']:>5.1f}% {sig:>6}")

    # 多策略综合排名（平均收益率）
    print(f"\n{'='*70}")
    print(f"  多策略综合排名（各策略平均收益率排序）")
    print(f"{'='*70}")
    avg = df.groupby("code").agg({
        "name": "first", "total_return": "mean", "sharpe": "mean",
        "max_drawdown": "mean", "win_rate": "mean"
    }).sort_values("total_return", ascending=False)
    print(f"  {'名次':>3} {'代码':>8} {'名称':<10} {'平均收益':>8} {'平均夏普':>8} {'平均回撤':>8} {'平均胜率':>8}")
    print(f"  {'-'*56}")
    for i, (code, row) in enumerate(avg.head(top_n).iterrows()):
        print(f"  {i+1:>3} {code:>8} {row['name']:<10} {row['total_return']:>+7.2%} {row['sharpe']:>7.2f} {row['max_drawdown']:>7.2%} {row['win_rate']:>6.1f}%")

    print(f"\n{'='*70}")
    print(f"  当前持仓信号总览")
    print(f"{'='*70}")
    print(f"  {'代码':>8} {'名称':<10} {'MA(5,20)':>10} {'RSI(14)':>10} {'MACD':>10} {'布林带':>10}")
    print(f"  {'-'*58}")
    latest = df[df["strategy"].isin(["MA5/20", "RSI(14)", "MACD(12,26,9)", "BB(20)"])]
    for code in df["code"].unique():
        row_data = latest[latest["code"] == code]
        name = row_data["name"].iloc[0] if len(row_data) > 0 else ""
        sigs = {}
        for _, r in row_data.iterrows():
            sigs[r["strategy"]] = "持有" if r["last_signal"] == 1 else "空仓"
        print(f"  {code:>8} {name:<10} {sigs.get('MA5/20','-'):>10} {sigs.get('RSI(14)','-'):>10} {sigs.get('MACD(12,26,9)','-'):>10} {sigs.get('BB(20)','-'):>10}")

    print()
    print(f"  {'='*70}")
    print(f"  📖 指标说明（小白版）")
    print(f"  {'='*70}")
    print(f"  • 收益率     — 策略在这段时间赚了(+)或亏了(-)百分之几")
    print(f"  • 超额收益   — 比\"买了就不动\"多赚了(+)还是少赚了(-)多少")
    print(f"  • 夏普比率   — 每承担1份风险能换回多少回报(>1不错, >2优秀)")
    print(f"  • 最大回撤   — 过程中最多亏了多少，考验心态的指标")
    print(f"  • 胜率       — 交易中赚钱的次数占比")
    print(f"  • 交易次数   — 整个周期里买卖了多少次")
    print(f"  • 持有=持仓中 | 空仓=持币观望")
    print()

    # 总结建议
    df_summary = pd.DataFrame(all_results)
    print(f"  {'='*70}")
    print(f"  💡 总结建议")
    print(f"  {'='*70}")
    best_strat = df_summary.loc[df_summary["total_return"].idxmax()]
    worst_strat = df_summary.loc[df_summary["total_return"].idxmin()]

    # 判断多空
    long_count = sum(1 for r in all_results if r["last_signal"] == 1)
    short_count = sum(1 for r in all_results if r["last_signal"] == 0)
    total = len(all_results)
    all_short = short_count == total
    all_long = long_count == total

    # 找最佳策略的信号
    best_signal = "持有" if best_strat["last_signal"] == 1 else "空仓"

    print(f"  📈 最佳策略: {best_strat['strategy']} (收益 {best_strat['total_return']*100:+.2f}%)")
    print(f"     当前{best_strat['strategy']}信号: {'🟢 持有 → 可继续持仓' if best_strat['last_signal']==1 else '🔴 空仓 → 不建议买入'}")
    print()

    if all_short:
        print(f"  🔴 全部{total}个策略一致空仓")
        print(f"     → 操作建议: 当前不适合买入，持币观望")
        print(f"     → 什么时候买: 等多数策略转为\"持有\"信号再考虑")
    elif all_long:
        print(f"  🟢 全部{total}个策略一致看多")
        print(f"     → 操作建议: 趋势向好，可继续持有或分批买入")
        print(f"     → 什么时候卖: 等多数策略转为\"空仓\"信号再考虑")
    else:
        print(f"  🟡 {long_count}/{total}策略看多, {short_count}/{total}策略看空 → 信号分歧")
        if long_count > short_count:
            print(f"     → 操作建议: 多头略占优，轻仓可持有，重仓需谨慎")
        elif short_count > long_count:
            print(f"     → 操作建议: 空头占优，不建议新开仓，已有仓位可持有观察")
        else:
            print(f"     → 操作建议: 多空均衡，建议观望，等待方向明确")
        print(f"     → 关注点: 当一致性超过{'2/3' if total > 3 else '半数'}时趋势会更明确")

    print()
    print(f"  ⚠️ 风险提示: 以上分析基于历史数据，过去表现不代表未来收益")
    print(f"  💡 建议: 决策前先用 mx-finance-data 查看基本面（PE、营收等）")
    print()

    return df

# ============================================================
# CLI 入口
# ============================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description="OneQuant Lite - 多股票多策略回测")
    parser.add_argument("--symbols", type=str, default="",
                        help="股票代码，逗号分隔，如 600519,000858")
    parser.add_argument("--strategy", type=str, default="all",
                        choices=["all", "ma", "rsi", "macd", "bb"],
                        help="策略类型")
    parser.add_argument("--top", type=int, default=10, help="排行榜前N只")
    parser.add_argument("--export", action="store_true", help="导出CSV报告")
    parser.add_argument("--html", action="store_true", help="生成HTML报告（带资金曲线图）")
    parser.add_argument("--risk", action="store_true", help="风险评估模式（VaR/卡玛/索提诺等）")
    parser.add_argument("--fusion", action="store_true", help="多策略信号融合模式")
    parser.add_argument("--ascii", action="store_true", help="显示ASCII资金曲线图")
    parser.add_argument("--optimize", type=str, default="",
                        help="参数优化: ma / rsi / macd (如 --optimize ma)")
    args = parser.parse_args()

    # 解析股票列表
    if args.symbols:
        codes = [s.strip() for s in args.symbols.split(",")]
    else:
        codes = list(PRESET_STOCKS.keys())

    # 选择策略
    strategies = []
    if args.strategy in ("all", "ma"):
        strategies.append(MAStrategy(5, 20))
    if args.strategy in ("all", "rsi"):
        strategies.append(RSIStrategy(14, 30, 70))
    if args.strategy in ("all", "macd"):
        strategies.append(MACDStrategy(12, 26, 9))
    if args.strategy in ("all", "bb"):
        strategies.append(BBStrategy(20, 2))
    if args.strategy in ("all", "kdj"):
        strategies.append(KDJStrategy(9, 3, 3))
    if args.strategy in ("all", "turtle"):
        strategies.append(TurtleStrategy(20, 10))
    if args.strategy in ("all", "multima"):
        strategies.append(MultiMAStrategy(5, 20, 60))

    # 参数优化模式
    if args.optimize:
        for code in codes:
            closes, name = _load_stock_data(code)
            if closes is None:
                continue
            dates = pd.date_range(start="2026-01-19", periods=len(closes), freq="B")
            base_df = pd.DataFrame({"close": closes}, index=dates)

            if args.optimize == "ma":
                print(f"\n{'='*60}")
                print(f"  MA参数优化 - {name}({code})")
                print(f"{'='*60}")
                print(f"  {'参数':>10} {'收益率':>8} {'夏普':>6} {'回撤':>8} {'胜率':>6}")
                print(f"  {'-'*42}")
                best = {"tr": -999, "params": "", "sp": 0}
                for s in [3, 5, 10, 20]:
                    for l in [10, 20, 30, 60]:
                        if s >= l: continue
                        strat = MAStrategy(s, l)
                        df = strat.generate_signals(base_df)
                        df["sr"] = df["signal"].shift(1) * base_df["close"].pct_change()
                        df["cum"] = (1 + df["sr"]).cumprod()
                        tr = df["cum"].iloc[-1] - 1
                        ex = df["sr"].dropna() - 0.02/252
                        sp = np.sqrt(252) * ex.mean() / ex.std() if ex.std() > 1e-10 else 0
                        mdd = ((df["cum"] - df["cum"].cummax()) / df["cum"].cummax()).min()
                        win = (df["sr"] > 0).sum()
                        tot = (df["sr"] != 0).sum()
                        wr = win/tot*100 if tot > 0 else 0
                        print(f"  MA({s},{l:>2}) {tr:>+7.2%} {sp:>6.2f} {mdd:>7.2%} {wr:>5.1f}%")
                        if tr > best["tr"]:
                            best = {"tr": tr, "params": f"MA({s},{l})", "sp": sp, "mdd": mdd}
                print(f"  {'-'*42}")
                print(f"  最优: {best['params']} | 收益:{best['tr']:+.2%} | 夏普:{best['sp']:.2f} | 回撤:{best['mdd']:.2%}")

            elif args.optimize == "rsi":
                print(f"\n{'='*60}")
                print(f"  RSI参数优化 - {name}({code})")
                print(f"{'='*60}")
                print(f"  {'参数':>10} {'收益率':>8} {'夏普':>6} {'回撤':>8} {'胜率':>6}")
                print(f"  {'-'*42}")
                best = {"tr": -999, "params": ""}
                for period in [6, 9, 14, 21]:
                    strat = RSIStrategy(period, 30, 70)
                    df = strat.generate_signals(base_df)
                    df["sr"] = df["signal"].shift(1) * base_df["close"].pct_change()
                    df["cum"] = (1 + df["sr"]).cumprod()
                    tr = df["cum"].iloc[-1] - 1
                    ex = df["sr"].dropna() - 0.02/252
                    sp = np.sqrt(252) * ex.mean() / ex.std() if ex.std() > 1e-10 else 0
                    mdd = ((df["cum"] - df["cum"].cummax()) / df["cum"].cummax()).min()
                    print(f"  RSI({period:>2})  {tr:>+7.2%} {sp:>6.2f} {mdd:>7.2%}")
                    if tr > best["tr"]:
                        best = {"tr": tr, "params": f"RSI({period})", "sp": sp, "mdd": mdd}
                print(f"  {'-'*42}")
                print(f"  最优: {best['params']} | 收益:{best['tr']:+.2%} | 夏普:{best['sp']:.2f}")

            elif args.optimize == "macd":
                print(f"\n{'='*60}")
                print(f"  MACD参数优化 - {name}({code})")
                print(f"{'='*60}")
                print(f"  {'参数':>14} {'收益率':>8} {'夏普':>6} {'回撤':>8}")
                print(f"  {'-'*42}")
                best = {"tr": -999, "params": ""}
                for f, s in [(8, 17), (12, 26), (16, 34)]:
                    strat = MACDStrategy(f, s, 9)
                    df = strat.generate_signals(base_df)
                    df["sr"] = df["signal"].shift(1) * base_df["close"].pct_change()
                    df["cum"] = (1 + df["sr"]).cumprod()
                    tr = df["cum"].iloc[-1] - 1
                    ex = df["sr"].dropna() - 0.02/252
                    sp = np.sqrt(252) * ex.mean() / ex.std() if ex.std() > 1e-10 else 0
                    mdd = ((df["cum"] - df["cum"].cummax()) / df["cum"].cummax()).min()
                    print(f"  MACD({f},{s:>2}) {tr:>+7.2%} {sp:>6.2f} {mdd:>7.2%}")
                    if tr > best["tr"]:
                        best = {"tr": tr, "params": f"MACD({f},{s})", "sp": sp}
                print(f"  {'-'*42}")
                print(f"  最优: {best['params']} | 收益:{best['tr']:+.2%} | 夏普:{best['sp']:.2f}")
        return

    # 多策略信号融合模式
    if args.fusion:
        fusion_strategies = [
            MAStrategy(5, 20), RSIStrategy(14, 30, 70),
            MACDStrategy(12, 26, 9), KDJStrategy(9, 3, 3),
        ]
        print(f"\n{'='*60}")
        print(f"  多策略信号融合（MA+RSI+MACD+KDJ 一致时交易）")
        print(f"{'='*60}")
        for code in codes:
            closes, name = _load_stock_data(code)
            if closes is None:
                continue
            dates = pd.date_range(start="2026-01-19", periods=len(closes), freq="B")
            base_df = pd.DataFrame({"close": closes}, index=dates)
            base_df["daily_return"] = base_df["close"].pct_change()

            # 计算各策略信号
            signals = []
            for strat in fusion_strategies:
                df = strat.generate_signals(base_df)
                signals.append(df["signal"])

            # 融合信号：多数一致才交易（至少3/4策略同向）
            fusion = (sum(signals) >= 3).astype(int)
            fusion_diff = fusion.diff()
            fusion_sr = fusion.shift(1) * base_df["daily_return"]
            fusion_cum = (1 + fusion_sr).cumprod()

            tr = fusion_cum.iloc[-1] - 1
            mr = base_df["close"].iloc[-1] / base_df["close"].iloc[0] - 1
            ex_ret = fusion_sr.dropna() - 0.02/252
            sp = np.sqrt(252) * ex_ret.mean() / ex_ret.std() if ex_ret.std() > 1e-10 else 0
            trades = int(fusion_diff.abs().sum())

            print(f"\n  {name}({code})")
            print(f"  {'-'*40}")
            print(f"  融合策略收益:  {tr:>+7.2%}")
            print(f"  买入持有收益:  {mr:>+7.2%}")
            print(f"  超额收益:      {(tr-mr):>+7.2%}")
            print(f"  夏普比率:      {sp:>7.2f}")
            print(f"  交易次数:      {trades} 次")
            print(f"  当前信号:      {'持有' if fusion.iloc[-1]==1 else '空仓'}")

            # 对比各单一策略
            print(f"  单一策略对比:")
            for strat in fusion_strategies:
                sdf = strat.generate_signals(base_df)
                ssr = sdf["signal"].shift(1) * base_df["daily_return"]
                scum = (1 + ssr).cumprod()
                print(f"    {strat.name:>15}: {scum.iloc[-1]-1:>+7.2%}")

        return

    # 风险评估模式
    if args.risk:
        risk_strategies = [
            MAStrategy(5, 20), RSIStrategy(14, 30, 70),
            MACDStrategy(12, 26, 9), KDJStrategy(9, 3, 3),
            TurtleStrategy(20, 10), MultiMAStrategy(5, 20, 60),
        ]
        print(f"\n{'='*70}")
        print(f"  风险评估报告")
        print(f"{'='*70}")
        for code in codes:
            closes, name = _load_stock_data(code)
            if closes is None:
                continue
            dates = pd.date_range(start="2026-01-19", periods=len(closes), freq="B")
            base_df = pd.DataFrame({"close": closes}, index=dates)
            base_df["daily_return"] = base_df["close"].pct_change()
            base_daily = base_df["daily_return"].dropna()

            print(f"\n  {name}({code}) - 基础风险指标")
            print(f"  {'-'*50}")

            # 基础统计
            mu = base_daily.mean()
            sigma = base_daily.std()
            print(f"  日均收益率:     {mu*100:+.4f}%")
            print(f"  日波动率:       {sigma*100:.4f}%")
            print(f"  年化波动率:     {sigma*np.sqrt(252)*100:.2f}%")

            # VaR (95%, 99%)
            var_95 = np.percentile(base_daily, 5)
            var_99 = np.percentile(base_daily, 1)
            print(f"  VaR(95%):       {var_95*100:+.2f}%（单日最大损失）")
            print(f"  VaR(99%):       {var_99*100:+.2f}%")

            # 最大回撤
            cum = (1 + base_daily).cumprod()
            mdd_bh = ((cum - cum.cummax()) / cum.cummax()).min()
            print(f"  买入持有最大回撤: {mdd_bh*100:.2f}%")

            # 胜率（日）
            win_days = (base_daily > 0).sum()
            total_days = len(base_daily)
            print(f"  日胜率:         {win_days/total_days*100:.1f}%")

            # 各策略风险评估
            print(f"\n  {name}({code}) - 各策略风险指标")
            print(f"  {'-'*50}")
            print(f"  {'策略':>16} | {'年化收益':>8} | {'夏普':>6} | {'卡玛':>6} | {'索提诺':>7} | {'回撤':>7} | {'VaR95':>7}")
            print(f"  {'-'*70}")
            for strat in risk_strategies:
                sdf = strat.generate_signals(base_df)
                s_sr = sdf["signal"].shift(1) * base_daily
                s_sr = s_sr.dropna()
                # 年化收益
                s_cum = (1 + s_sr).cumprod()
                ann_ret = s_cum.iloc[-1] ** (252 / len(s_sr)) - 1 if len(s_sr) > 0 else 0
                # 夏普
                sp = np.sqrt(252) * s_sr.mean() / s_sr.std() if s_sr.std() > 1e-10 else 0
                # 最大回撤
                mdd = ((s_cum - s_cum.cummax()) / s_cum.cummax()).min()
                # 卡玛比率
                calmar = ann_ret / abs(mdd) if abs(mdd) > 1e-10 else 0
                # 索提诺比率（只考虑下行风险）
                downside = s_sr[s_sr < 0].std()
                sortino = np.sqrt(252) * s_sr.mean() / downside if downside > 1e-10 else 0
                # VaR 95%
                var95 = np.percentile(s_sr, 5)
                print(f"  {strat.name:>16} | {ann_ret*100:>+7.2f}% | {sp:>5.2f} | {calmar:>5.2f} | {sortino:>6.2f} | {mdd*100:>5.2f}% | {var95*100:>5.2f}%")

        return

    # 运行回测
    all_results = []
    df_dict = {}  # 用于HTML图表: {code: {strategy_name: DataFrame}}
    for code in codes:
        closes, name = _load_stock_data(code)
        if closes is None:
            print(f"  [跳过] {code} {name}: 无数据")
            continue
        results, strat_dfs = backtest(code, name, closes, strategies)
        all_results.extend(results)
        df_dict[code] = strat_dfs

    # 输出报告
    report_df = print_report(all_results, args.top)

    # HTML 报告
    if args.html:
        try:
            from report_html import generate_html_report, save_report
            code_names = {c: PRESET_STOCKS.get(c, c) for c in codes}
            html = generate_html_report(all_results, df_dict, code_names)
            # 生成易读的文件名
            parts = []
            for c in codes:
                n = PRESET_STOCKS.get(c)
                parts.append(f"{n}_{c}" if n else c)
            names = "_".join(sorted(set(parts)))
            if not names:
                names = codes[0] if codes else "stock"
            html_name = f"回测_{names}_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
            html_path = os.path.join(_OUTPUT_DIR, html_name)
            path = save_report(html, path=html_path)
            print(f"\n  HTML报告已生成: {path}")
        except Exception as e:
            print(f"\n  HTML报告生成失败: {e}")

    # ASCII 资金曲线图
    if args.ascii:
        print()
        for code in codes:
            if code not in df_dict:
                continue
            name = PRESET_STOCKS.get(code, code)
            strat_dfs = df_dict[code]
            if isinstance(strat_dfs, dict):
                for sname, sdf in strat_dfs.items():
                    if "cum_strategy" in sdf.columns:
                        print(ascii_equity_curve(sdf["cum_strategy"].values,
                                                  title=f"{name}({code}) {sname}"))
                        break
            elif hasattr(strat_dfs, "columns") and "cum_strategy" in strat_dfs.columns:
                print(ascii_equity_curve(strat_dfs["cum_strategy"].values,
                                          title=f"{name}({code})"))

    # 导出
    if args.export:
        parts = []
        for c in codes:
            n = PRESET_STOCKS.get(c)
            parts.append(f"{n}_{c}" if n else c)
        names = "_".join(sorted(set(parts)))
        if not names:
            names = codes[0] if codes else "stock"
        out_path = os.path.join(_OUTPUT_DIR, f"回测_{names}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
        report_df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"\n  报告已导出: {out_path}")

if __name__ == "__main__":
    main()
