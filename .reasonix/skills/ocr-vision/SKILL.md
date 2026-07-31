---
name: ocr-vision
description: 本地免费 OCR 识图（rapidocr，PaddleOCR ONNX）：识别截图/图片中的中英文字，无需联网。触发：看图/识别文字/OCR/截图内容
---

# 本地 OCR 识图（rapidocr）

> 能力：**本地免费 OCR**——识别图片中的文字（中英文），无需联网、无需代理。
> 引擎：`rapidocr_onnxruntime` 1.4.4（PaddleOCR ONNX 版），本机已装（opencv 4.9 + numpy 1.26.4，注意 numpy 不能升到 2.x 否则 cv2 崩溃）。

## 何时用（Trigger）

- 用户发来截图/图片附件（通常在 `.reasonix/attachments/` 或 `screenshots/` 下），需要读出图中的文字（文件列表、报错信息、表格、聊天记录等）
- 用户说"看看这张图/识别图里的字/OCR 一下"
- 主模型无视觉能力时读取图片文字的首选方案（比联网视觉 API 更快更稳，不受代理影响）

## 使用方式（标准命令）

```powershell
$env:PYTHONIOENCODING="utf-8"
python -c @'
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
img = r"<图片绝对路径>"
result, _ = ocr(img)
if result:
    for box, text, conf in result:
        print(text)
else:
    print("NO_TEXT_DETECTED")
'@
```

**输出**：按行输出识别出的文字（box 是坐标、conf 是置信度，正文只取 text）。识别结果按行序排列，可据此还原截图内容。

## 图片预处理（可选，提高准确率）

- 小字/模糊图：先放大 2 倍再识别（rapidocr 对清晰大图更好）
- 深色背景：可转灰度/反色
- 一般截图直接识别即可

## 补充：批量识别目录

```python
import glob
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
for img in glob.glob(r"<目录>\*.png"):
    result, _ = ocr(img)
    print(f"### {img}")
    if result:
        for _, text, _ in result:
            print(text)
```

## NEVER 规则

- ❌ 不要因为主模型不能直接看图就拒绝——本 skill 就是替代方案，必须先跑 OCR
- ❌ 不要尝试联网视觉 API（Agnes/Gemini）当首选——Clash 关着时它们连不上，本地 OCR 永远可用
- ❌ 不要升级 numpy 到 2.x（opencv 4.9 ABI 不兼容，会导致 cv2 导入崩溃）
- ❌ OCR 失败时不要臆测图片内容，如实报告识别结果

## 已知限制

- 手写体/艺术字/极小字可能识别不准（置信度 conf 低，可标注）
- 纯图形无文字时输出 NO_TEXT_DETECTED，属正常
- 首次调用会加载模型（~2-5 秒），后续快
