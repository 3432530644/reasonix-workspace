# -*- coding: utf-8 -*-
"""
OneQuant Lite — HTML 报告生成器
生成带资金曲线图的网页报告
"""
import io, base64, os
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ============================================================
# 图表生成
# ============================================================
def _img_to_b64(fig):
    """将 matplotlib 图表转为 base64 HTML 内嵌"""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def plot_equity_curve(df, code, name, strategy):
    """资金曲线图"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={"height_ratios": [3, 1]})

    # 上：资金曲线
    ax1.plot(df.index, df["cum_strategy"], label=f"{strategy} 策略", color="#e74c3c", lw=1.5)
    ax1.plot(df.index, df["cum_market"], label="买入持有", color="#3498db", lw=1.5, alpha=0.7)
    ax1.axhline(y=1.0, color="gray", ls="--", lw=0.5)
    ax1.set_title(f"{name}({code}) - {strategy} 资金曲线", fontsize=12)
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylabel("净值")
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

    # 下：回撤曲线
    dd = (df["cum_strategy"] - df["cum_strategy"].cummax()) / df["cum_strategy"].cummax()
    ax2.fill_between(df.index, dd * 100, 0, color="#e74c3c", alpha=0.3)
    ax2.plot(df.index, dd * 100, color="#e74c3c", lw=0.8)
    ax2.set_title("回撤曲线", fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylabel("回撤(%)")
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

    plt.tight_layout()
    b64 = _img_to_b64(fig)
    plt.close(fig)
    return b64

def plot_strategy_comparison(all_results):
    """多策略收益率对比柱状图"""
    df = pd.DataFrame(all_results)
    fig, ax = plt.subplots(figsize=(10, 5))

    strategies = df["strategy"].unique()
    codes = df["code"].unique()
    x = np.arange(len(codes))
    width = 0.8 / len(strategies)

    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
    for i, strat in enumerate(strategies):
        subset = df[df["strategy"] == strat]
        vals = [subset[subset["code"] == c]["total_return"].values[0] * 100 if len(subset[subset["code"] == c]) > 0 else 0 for c in codes]
        ax.bar(x + i * width, vals, width, label=strat, color=colors[i % len(colors)], alpha=0.8)

    ax.axhline(y=0, color="gray", lw=0.5)
    ax.set_title("多策略收益率对比", fontsize=12)
    ax.set_ylabel("收益率(%)")
    ax.set_xticks(x + width * (len(strategies) - 1) / 2)
    names = [df[df["code"] == c]["name"].values[0] if len(df[df["code"] == c]) > 0 else c for c in codes]
    ax.set_xticklabels(names, fontsize=9)
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)

    plt.tight_layout()
    b64 = _img_to_b64(fig)
    plt.close(fig)
    return b64

# ============================================================
# HTML 模板
# ============================================================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OneQuant Lite - 量化回测报告</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, "Microsoft YaHei", sans-serif; background: #f5f6fa; color: #2c3e50; padding: 20px; }}
.container {{ max-width: 1000px; margin: 0 auto; }}
.header {{ background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 30px; border-radius: 12px; margin-bottom: 24px; }}
.header h1 {{ font-size: 24px; margin-bottom: 8px; }}
.header p {{ opacity: 0.85; font-size: 14px; }}
.section {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
.section h2 {{ font-size: 18px; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #3498db; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
th {{ background: #f8f9fa; padding: 10px 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6; }}
td {{ padding: 8px 12px; border-bottom: 1px solid #eee; }}
tr:hover {{ background: #f8f9fa; }}
.pos {{ color: #e74c3c; font-weight: 600; }}
.neg {{ color: #27ae60; font-weight: 600; }}
.signal-hold {{ color: #e74c3c; }} .signal-empty {{ color: #95a5a6; }}
.chart {{ text-align: center; margin: 16px 0; }}
.chart img {{ max-width: 100%; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }}
.footer {{ text-align: center; color: #95a5a6; font-size: 12px; padding: 20px; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
.badge-hold {{ background: #fde8e8; color: #e74c3c; }}
.badge-empty {{ background: #f0f0f0; color: #95a5a6; }}
.strategy-tabs {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
.strategy-tab {{ padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; cursor: default; }}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>OneQuant Lite - 量化回测报告</h1>
<p>生成时间: {report_time} | 数据: Yahoo Finance ({date_range}) | 股票数: {stock_count} | 策略数: {strategy_count}</p>
</div>

{content}

<div class="footer">
<p>OneQuant Lite v1.0 | 过去表现不代表未来收益，数据仅供参考</p>
<p>报告由 AI Agent 自动生成</p>
</div>
</div>
</body>
</html>"""

# ============================================================
# 报告生成
# ============================================================
def generate_html_report(all_results, df_dict, code_names):
    """生成完整 HTML 报告"""
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_range = "2026-01-19 ~ 2026-07-17"

    result_df = pd.DataFrame(all_results)
    codes = result_df["code"].unique()
    strategies = result_df["strategy"].unique()

    content = ""

    # ===== 策略对比图 =====
    content += '<div class="section">'
    content += "<h2>多策略收益率对比</h2>"
    chart_b64 = plot_strategy_comparison(all_results)
    content += f'<div class="chart"><img src="data:image/png;base64,{chart_b64}" alt="策略对比"></div>'
    content += "</div>"

    # ===== 各策略排行榜 =====
    for strat in strategies:
        subset = result_df[result_df["strategy"] == strat].sort_values("total_return", ascending=False)
        content += '<div class="section">'
        content += f"<h2>{strat} 策略排行榜</h2>"
        content += "<table><thead><tr>"
        content += "<th>排名</th><th>代码</th><th>名称</th><th>收益率</th><th>超额收益</th>"
        content += "<th>夏普比率</th><th>最大回撤</th><th>胜率</th><th>交易次数</th><th>信号</th>"
        content += "</tr></thead><tbody>"
        for i, (_, row) in enumerate(subset.iterrows()):
            tr_class = "pos" if row["total_return"] >= 0 else "neg"
            sig_class = "signal-hold" if row["last_signal"] == 1 else "signal-empty"
            sig_text = "持有" if row["last_signal"] == 1 else "空仓"
            content += f"<tr>"
            content += f"<td>{i+1}</td>"
            content += f"<td>{row['code']}</td>"
            content += f"<td>{row['name']}</td>"
            content += f"<td class='{tr_class}'>{row['total_return']*100:+.2f}%</td>"
            content += f"<td>{row['excess']*100:+.2f}%</td>"
            content += f"<td>{row['sharpe']:.2f}</td>"
            content += f"<td>{row['max_drawdown']*100:.2f}%</td>"
            content += f"<td>{row['win_rate']:.1f}%</td>"
            content += f"<td>{row['trades']}</td>"
            content += f"<td class='{sig_class}'>{sig_text}</td>"
            content += "</tr>"
        content += "</tbody></table>"
        content += "</div>"

    # ===== 资金曲线图（每只股票最好的策略） =====
    for code in codes:
        name = code_names.get(code, code)
        if code not in df_dict:
            continue
        # 找到该股票最好的策略
        stock_results = result_df[result_df["code"] == code]
        best = stock_results.sort_values("total_return", ascending=False).iloc[0]
        strat_name = best["strategy"]
        # 获取对应的 DataFrame
        strat_dfs = df_dict[code]
        if isinstance(strat_dfs, dict):
            # df_dict[code] 是 {strategy_name: DataFrame}
            df = strat_dfs.get(strat_name)
            if df is None:
                # 取第一个可用的
                df = list(strat_dfs.values())[0] if strat_dfs else None
        else:
            df = strat_dfs
        if df is None:
            continue

        content += '<div class="section">'
        content += f"<h2>{name}({code}) - {strat_name}</h2>"
        chart_b64 = plot_equity_curve(df, code, name, strat_name)
        content += f'<div class="chart"><img src="data:image/png;base64,{chart_b64}" alt="{name}资金曲线"></div>'
        content += "</div>"

    # ===== 信号总览 =====
    content += '<div class="section">'
    content += "<h2>当前持仓信号总览</h2>"
    content += "<table><thead><tr>"
    content += "<th>代码</th><th>名称</th>"
    for strat in strategies:
        content += f"<th>{strat}</th>"
    content += "</tr></thead><tbody>"
    for code in codes:
        name = code_names.get(code, code)
        content += f"<tr><td>{code}</td><td>{name}</td>"
        for strat in strategies:
            row = result_df[(result_df["code"] == code) & (result_df["strategy"] == strat)]
            if len(row) > 0:
                sig = "持有" if row["last_signal"].values[0] == 1 else "空仓"
                cls = "badge-hold" if row["last_signal"].values[0] == 1 else "badge-empty"
                content += f'<td><span class="badge {cls}">{sig}</span></td>'
            else:
                content += "<td>-</td>"
        content += "</tr>"
    content += "</tbody></table>"
    content += "</div>"

    # ===== 指标说明 =====
    content += '<div class="section" style="background:#fef9e7;border-left:4px solid #f39c12;">'
    content += '<h2 style="color:#e67e22;">📖 指标说明</h2>'
    content += '<table style="font-size:13px;">'
    content += '<tr><td><b>收益率</b></td><td>策略在这段时间赚了(+)或亏了(-)百分之几</td></tr>'
    content += '<tr><td><b>超额收益</b></td><td>比"买了就不动"多赚了(+)还是少赚了(-)多少</td></tr>'
    content += '<tr><td><b>夏普比率</b></td><td>每承担1份风险能换回多少回报（>1不错，>2优秀）</td></tr>'
    content += '<tr><td><b>最大回撤</b></td><td>过程中最多亏了多少，考验心态的指标</td></tr>'
    content += '<tr><td><b>胜率</b></td><td>交易中赚钱的次数占比</td></tr>'
    content += '<tr><td><b>信号</b></td><td>持有=持仓中，空仓=持币观望</td></tr>'
    content += '</table></div>'

    # ===== 总结建议 =====
    best = result_df.loc[result_df["total_return"].idxmax()]
    worst = result_df.loc[result_df["total_return"].idxmin()]
    long_count = sum(1 for r in all_results if r["last_signal"] == 1)
    short_count = sum(1 for r in all_results if r["last_signal"] == 0)
    total = len(all_results)
    all_short = short_count == total
    all_long = long_count == total
    best_sig = "持有" if best["last_signal"] == 1 else "空仓"

    if all_short:
        advice = f"全部{total}个策略一致空仓 → 当前不适合买入，持币观望。等多数策略转为持有信号再考虑。"
    elif all_long:
        advice = f"全部{total}个策略一致看多 → 趋势向好，可继续持有或分批买入。等多数策略转为空仓信号再考虑卖出。"
    elif long_count > short_count:
        advice = f"多头略占优（{long_count}/{total}），轻仓可持有，重仓需谨慎。"
    elif short_count > long_count:
        advice = f"空头占优（{short_count}/{total}），不建议新开仓，已有仓位可持有观察。"
    else:
        advice = "多空均衡，建议观望等待方向明确。"
    content += '<div class="section" style="background:#eafaf1;border-left:4px solid #27ae60;">'
    content += '<h2 style="color:#27ae60;">💡 总结建议</h2>'
    content += f'<p style="font-size:14px;line-height:1.8;">'
    content += f'<b>📈 最佳策略:</b> {best["strategy"]}（收益 {best["total_return"]*100:+.2f}%）<br>'
    content += f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;当前{best["strategy"]}信号: {"🟢 持有 → 可继续持仓" if best["last_signal"]==1 else "🔴 空仓 → 不建议买入"}<br><br>'
    content += f'<b>🎯 操作建议:</b> {advice}<br>'
    content += f'<b>⚠️ 风险提示:</b> 以上分析基于历史数据，过去表现不代表未来收益<br>'
    content += f'<b>💡 建议:</b> 决策前用 mx-finance-data 查看基本面（PE、营收等）综合判断'
    content += '</p></div>'

    # ===== 渲染 =====
    html = HTML_TEMPLATE.format(
        report_time=report_time,
        date_range=date_range,
        stock_count=len(codes),
        strategy_count=len(strategies),
        content=content,
    )
    return html


def save_report(html, path=None, output_dir=None):
    """保存 HTML 报告"""
    if path is None:
        out_dir = output_dir or "."
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"onequant_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.abspath(path)
