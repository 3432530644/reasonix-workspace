/**
 * PROVIDER_CHAIN — single source of truth for provider priority order.
 *
 * Extracted from AgentChat-OneWeb/index.js so that consumers that only
 * need the chain (e.g. IndependentTasks's buildFallbackChain) don't have to load
 * playwright-core + all 8 adapters just to read a constant array.
 *
 * OneWeb re-exports this for backward compatibility.
 */

const PROVIDER_CHAIN = [
    // { key: 'gemini',   name: 'Gemini',   url: 'https://gemini.google.com/u/0/app', authDomains: ['accounts.google.com'],
    //   // 已弃用（2026-08-01）：需 Clash 代理，用户要求全部走国内直连 provider。
    //   recoveryHint: 'bash scripts/connect-gemini.sh  # 重连一次恢复 Gemini 登录态' },
    { key: 'yuanbao',  name: '元宝',     url: 'https://yuanbao.tencent.com/chat',    authDomains: ['yuanbao.tencent.com/login', 'passport.tencent.com', 'graph.qq.com'] },
    { key: 'doubao',   name: '豆包',     url: 'https://www.doubao.com/chat/',        authDomains: ['sso.doubao.com', 'login.doubao.com', 'passport.doubao.com'] },
    { key: 'kimi',     name: 'Kimi',     url: 'https://www.kimi.com/',              authDomains: ['kimi.moonshot.cn/login', 'kimi.com/login', 'moonshot.cn/login'], tabHosts: ['kimi.moonshot.cn', 'kimi.com'] },
    // ── 以下 provider 已按用户要求禁用（2026-07-31）：未登录或远端不可达，避免每次白试浪费时间 ──
    // 如需启用：取消注释并确保在 Chrome profile 中已登录对应站点。
    // { key: 'chatgpt',  name: 'ChatGPT',  url: 'https://chatgpt.com/',               authDomains: ['auth.openai.com', 'chat.openai.com/auth'] },
    // { key: 'claude',   name: 'Claude',   url: 'https://claude.ai/',                 authDomains: ['claude.ai/login', 'auth.anthropic.com'] },
    // { key: 'qwen',     name: 'Qwen',     url: 'https://www.qianwen.com/?source=tongyigw', authDomains: ['qianwen.com/login', 'login.aliyun.com', 'signin.aliyun.com'] },
    // { key: 'minimax',  name: 'MiniMax',  url: 'https://agent.minimaxi.com/',        authDomains: ['agent.minimaxi.com/login', 'minimax.com/login'] },
    // { key: 'mimo',     name: 'MiMo',     url: 'https://aistudio.xiaomimimo.com/',   authDomains: ['aistudio.xiaomimimo.com/login', 'auth0.com'] },
    // { key: 'deepseek', name: 'DeepSeek', url: 'https://chat.deepseek.com/',         authDomains: ['chat.deepseek.com/login', 'deepseek.com/login'] },
];

module.exports = { PROVIDER_CHAIN };
