/**
 * 元宝 (Tencent Yuanbao) provider adapter config.
 *
 * 腾讯元宝 — 国内可直连（不走代理），支持多模态（看图/生图），
 * 作为 Gemini（需 Clash 代理）的国内替代主力。
 *
 * DOM 结构要点（2026-07-31 实测）：
 *   - 输入框：Quill 编辑器 `.ql-editor`（contenteditable）
 *   - 发送按钮：`<a aria-label="发送" class="style__send-btn___...">`（输入文本后才出现）
 *   - 响应容器：`.agent-chat__speech-text`（文本）→ `.hyc-content-md`（markdown 渲染，
 *     完成后加 `-done`）→ `.hyc-common-markdown`
 *   - 上传入口：`.UploadFileSelector_iconContainer`（图片上传，多模态）
 *   - 登录域：passport.tencent.com / graph.qq.com（微信/QQ 扫码）
 *
 * 注意：Chrome 需配 --proxy-bypass-list 含 *.tencent.com（见 cdp.js），
 * 否则 Clash 关闭时元宝也会 ERR_PROXY_CONNECTION_FAILED。
 */

const { COMMON_CN_QUOTA_PATTERNS, COMMON_DISMISS_PATTERNS } = require('../../providerFactory');
const { makeStillWorkingCheck } = require('../../stillWorking');

// 响应容器选择器：.hyc-common-markdown 同时承载文本与生图图片（混元 text2img 图片在此容器内），
// 放最前保证 responseEl 是含图容器；speech-text/content-md 为纯文本备选。
const RESPONSE_SELECTORS = [
    '.hyc-common-markdown',
    '.agent-chat__speech-text',
    '.hyc-content-md',
    '[class*="speech-text"]',
    '[class*="content-md"]',
    '[class*="markdown"]',
];

// 元宝自定义完成检测：默认检测（文本 busy/停止按钮/spinner）之上，补充
// 生图完成信号——最后响应容器出现已加载图片（.dic-card-item__img--loaded /
// img[src*="hunyuan"]）= 生图完成；出现占位动画（.dic-list--placeholder-ani）
// 且无"图片已生成"提示 = 仍在生成。解决纯图片响应无文本导致的等待卡死。
const _baseYuanbaoCheck = makeStillWorkingCheck({ responseSelectors: RESPONSE_SELECTORS });
async function yuanbaoStillWorking(page, info) {
    if (await _baseYuanbaoCheck(page, info)) return true;
    const st = await page.evaluate((sels) => {
        let host = null;
        for (const s of sels) {
            const l = document.querySelectorAll(s);
            if (l.length) { host = l[l.length - 1]; break; }
        }
        if (!host) return { state: 'none' };
        const text = (host.innerText || '').trim();
        const hasImg = !!host.querySelector(
            '.dic-card-item__img--loaded, img[src*="hunyuan"], img[src*="resource/download"], img[src*="text2img"]'
        );
        if (text.length >= 5 || hasImg) return { state: 'done', hasImg, text: text.slice(0, 20) };
        const placeholder = !!host.querySelector(
            '.dic-list--placeholder-ani, [class*="placeholder-ani"], [class*="loading"]'
        );
        const doneHint = /图片已生成|生成完成/.test(document.body.innerText.slice(-300));
        if (placeholder && !doneHint) return { state: 'busy' };
        return { state: 'waiting' };
    }, RESPONSE_SELECTORS);
    // true = 仍在生成（继续等待，stillGeneratingMaxHoldMs 兜底）；false = 完成可提取
    return st.state === 'busy' || st.state === 'none' || st.state === 'waiting';
}

module.exports = {
    key: 'yuanbao',
    url: 'https://yuanbao.tencent.com/chat',
    navPostDelay: 4000,   // SPA 挂载
    authDomains: ['yuanbao.tencent.com/login', 'passport.tencent.com', 'graph.qq.com', 'wx.qq.com'],
    quotaPatterns: [
        ...COMMON_CN_QUOTA_PATTERNS,
        /繁忙|限流|稍后再试|次数已用完/i,
    ],
    dismissPatterns: [...COMMON_DISMISS_PATTERNS],
    // 元宝欢迎页/引导区常驻内容匹配了 OVERLAY_SEL（如 [class*="dialog"]），
    // 但并非可关闭弹窗——跳过，避免 overlay 检查误判阻塞（同 mimo.js 方案）。
    skipOverlayPatterns: [
        /今天从哪里开始/i,
        /下载元宝电脑版|安装电脑版/i,
        /内容由AI生成，仅供参考/i,
        /深度思考/i,
    ],
    editorSelectors: [
        '.ql-editor',                          // Quill 编辑器（contenteditable）
        'textarea[placeholder*="输入"]',
        'textarea[placeholder*="提问"]',
        'textarea',
        '[contenteditable="true"]',
    ],
    sendSelectors: [
        'a[aria-label="发送"]',
        'button[aria-label="发送"]',
        '[class*="send-btn"]',
    ],
    sendFallback: 'Enter',
    responseSelectors: RESPONSE_SELECTORS,
    responseSelectorTimeout: 60_000,
    stabilityWindow: 12_000,
    minResponseLength: 5,

    // 生成中检测：自定义（默认检测 + 生图图片完成信号）
    // 时间兜底：元宝生图实测 30-40s 内完成，hold cap 45s 保证超时也会强制提取
    stillGeneratingCheck: yuanbaoStillWorking,
    stillGeneratingMaxHoldMs: 45_000,
};
