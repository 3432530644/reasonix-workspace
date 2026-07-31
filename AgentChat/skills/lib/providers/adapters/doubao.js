/**
 * 豆包 (Doubao / 字节跳动) provider adapter config.
 *
 * 国内直连（无需代理），多模态（看图/生图）。作为元宝之后的第二国内主力。
 *
 * DOM 结构要点（2026-08-01 实测）：
 *   - 输入框：Semi Design `textarea[placeholder*="发消息"]`（Enter 发送）
 *   - 发送：无 aria 发送按钮，Enter 直接发送（sendFallback='Enter'）
 *   - 消息列表：虚拟列表 `.v_list_row`（list_items 内，最后一行 = 最新消息）；
 *     responseSelectors 用 `.v_list_row` + echo guard 防提取到用户消息
 *   - 登录域：sso.doubao.com / passport 等
 *   - 类名 tailwind/hash 化，无稳定语义类名——v_list_row 是列表库稳定类
 */

const { COMMON_CN_QUOTA_PATTERNS, COMMON_DISMISS_PATTERNS } = require('../../providerFactory');
const { makeStillWorkingCheck } = require('../../stillWorking');

// 虚拟列表行 = 每条消息；最后一行即最新消息（assistant 回复）。
// echo guard（factory 内置）会拒绝与 prompt 近似的文本，防止提取到用户消息行。
const RESPONSE_SELECTORS = [
    '.v_list_row',
    '.list_items',
    '[class*="v_list_row"]',
];

module.exports = {
    key: 'doubao',
    url: 'https://www.doubao.com/chat/',
    navPostDelay: 4000,   // SPA 挂载
    authDomains: ['sso.doubao.com', 'login.doubao.com', 'passport.doubao.com', 'sso.snssdk.com'],
    quotaPatterns: [
        ...COMMON_CN_QUOTA_PATTERNS,
        /繁忙|限流|稍后再试|太频繁/i,
    ],
    dismissPatterns: [...COMMON_DISMISS_PATTERNS],
    editorSelectors: [
        'textarea[placeholder*="发消息"]',
        'textarea[placeholder*="message"]',
        'textarea[placeholder*="提问"]',
        'textarea',
        '[contenteditable="true"]',
    ],
    // 豆包无 aria 发送按钮，Enter 即发送（实测有效）
    sendSelectors: [],
    sendFallback: 'Enter',
    responseSelectors: RESPONSE_SELECTORS,
    responseSelectorTimeout: 60_000,
    stabilityWindow: 12_000,
    minResponseLength: 5,
    // 过滤小图标/头像（豆包回复常夹带 UI 图）；生成图以 rc_gen_image URL 为主
    imageMinPx: 128,

    // 生成中检测：共享多信号检测器；45s 时间兜底（豆包响应一般在 10-30s）
    stillGeneratingCheck: makeStillWorkingCheck({ responseSelectors: RESPONSE_SELECTORS }),
    stillGeneratingMaxHoldMs: 45_000,
};
