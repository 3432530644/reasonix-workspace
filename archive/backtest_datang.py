# -*- coding: utf-8 -*-
"""大唐发电(601991) MA策略回测 — 硬编码Yahoo数据"""
import pandas as pd
import numpy as np
from datetime import datetime

# Yahoo Finance 6个月日K数据 (2026-01-19 ~ 2026-07-17)
closes = [3.82,3.98,4.01,3.92,3.92,3.95,3.86,3.90,3.84,3.78,
          3.73,3.72,3.75,3.69,3.72,3.74,3.70,3.72,3.78,3.63,
          3.75,3.80,3.89,3.99,4.12,4.00,4.00,4.06,4.11,4.06,
          4.06,4.16,4.58,4.74,4.33,4.25,4.31,4.18,4.20,4.03,
          4.24,4.46,4.39,4.48,4.13,3.94,3.94,3.84,3.71,3.73,
          3.84,3.84,3.81,3.83,3.87,3.89,3.87,3.89,3.96,4.11,
          4.15,4.21,4.07,4.05,4.04,4.29,4.16,4.58,5.04,5.54,
          6.09,6.70,7.37,7.20,7.92,7.93,8.38,7.54,7.05,6.89,
          7.40,7.16,7.71,8.00,8.63,8.37,9.18,9.10,8.81,7.93,
          7.27,7.71,7.76,7.99,8.09,8.73,8.70,9.13,8.22,8.37,
          8.34,7.82,7.47,7.32,7.04,7.08,7.79,7.33,7.67,7.39,
          7.00,6.95,6.57,6.64,5.98,5.88,5.78,5.69,5.80]

df = pd.DataFrame({"close": closes})
df.index = pd.date_range(start="2026-01-19", periods=len(closes), freq="B")

print("=" * 60)
print("[1] 大唐发电 (601991) - 近6个月日K")
print("=" * 60)
print(f"  最新价: {df['close'].iloc[-1]:.2f} 元")
print(f"  最高价: {df['close'].max():.2f}")
print(f"  最低价: {df['close'].min():.2f}")
print(f"  数据量: {len(df)} 个交易日")
print()

df["MA5"] = df["close"].rolling(5).mean()
df["MA20"] = df["close"].rolling(20).mean()
df["signal"] = (df["MA5"] > df["MA20"]).astype(int)
df["position"] = df["signal"].diff()
df["daily_return"] = df["close"].pct_change()
df["strategy_return"] = df["signal"].shift(1) * df["daily_return"]
df["cum_market"] = (1 + df["daily_return"]).cumprod()
df["cum_strategy"] = (1 + df["strategy_return"]).cumprod()

tr = df["cum_strategy"].iloc[-1] - 1
mr = df["cum_market"].iloc[-1] - 1
win = (df["strategy_return"] > 0).sum()
tot = (df["strategy_return"] != 0).sum()
wr = win / tot * 100 if tot > 0 else 0
mdd = ((df["cum_strategy"] - df["cum_strategy"].cummax()) / df["cum_strategy"].cummax()).min()
trades = int(df["position"].abs().sum())
ex = df["strategy_return"].dropna() - 0.02 / 252
sp = np.sqrt(252) * ex.mean() / ex.std() if ex.std() > 0 else 0

print("=" * 60)
print("[2] MA5/MA20 金叉死叉策略回测")
print("=" * 60)
print(f"  {'-'*40}")
print(f"  策略总收益:    {tr:>+8.2%}")
print(f"  买入持有收益:  {mr:>+8.2%}")
print(f"  超额收益:      {(tr-mr):>+8.2%}")
print(f"  夏普比率:      {sp:>8.2f}")
print(f"  最大回撤:      {mdd:>8.2%}")
print(f"  胜率:          {wr:>7.1f}%")
print(f"  交易次数:      {trades} 次")
print(f"  {'-'*40}")
print()

print("=" * 60)
print("[3] 最近10日信号")
print("=" * 60)
for _, row in df.tail(10).iterrows():
    sig = "[持有]" if row["signal"] == 1 else "[空仓]"
    act = ""
    if row["position"] == 1:
        act = " << 买入"
    elif row["position"] == -1:
        act = " << 卖出"
    print(f"  {row.name.strftime('%m-%d')} | {row['close']:>7.2f} | MA5:{row['MA5']:>7.2f} | MA20:{row['MA20']:>7.2f} | {sig}{act}")

print()
print("=" * 60)
print("[4] 分析结论")
print("=" * 60)
lc = df["close"].iloc[-1]
m5 = df["MA5"].iloc[-1]
m20 = df["MA20"].iloc[-1]
print(f"  当前价: {lc:.2f} 元")
print(f"  MA5: {m5:.2f} | MA20: {m20:.2f}")
print(f"  信号: {'MA金叉持仓 (MA5 > MA20)' if df['signal'].iloc[-1] == 1 else 'MA死叉空仓 (MA5 <= MA20)'}")
print(f"  源: Yahoo Finance | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"  风险: 过去表现不代表未来收益")
