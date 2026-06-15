# Project Log — Agent-Ready Benchmark

> **用途**：每开一个新会话，先读这份 log 当 memory。顶部「当前状态」永远保持最新；下面「决策日志」「会话日志」只追加不改写。
> **维护约定**：每次 session 收尾时，更新「当前状态」+ 在「会话日志」追加一条 + 有新决策就进「决策日志」。日期用绝对日期。

---

## 这个项目是什么（冷启动必读）

一个**行为性 benchmark**，量一个开放平台能不能让 AI agent「把文档 URL 扔过去 + 一句开发者需求，就自主把整个集成应用做出来」。
把 [[agent-friendly-open-platform-design]] 的四层框架 + [[open-platform-metrics]] 的 AI 友好度指标，operationalize 成可跑、可复现的评分系统。

双用途：① 公开横评 Stripe / Shopify / 微信 / 飞书 / POP(得物)；② 量 POP 自家改造前后的增量（简历侧 "shipped & measured"）。

- **评分标准**：`scoring-model-design.md`（仓库内，当前 **v0.3**）
- **KB 跟进页**：`wiki/domains/work/open-platform/agent-ready-benchmark.md`（在 henson-kb）
- **GitHub**：github.com/hensonzyw-git/open-platform-agent-readiness-benchmark（直接推 main，无分支）

---

## 当前状态（截至 2026-06-16）— 从这里继续

**标准**：v0.3 已定型并入库。核心模型稳定，§10 仍有待拍板项。

**仓库 tracked 文件**：`.gitignore`、`scoring-model-design.md`、`PROJECT-LOG.md`。

**harness**：本地 spike，已 gitignore、**不入库**。复用价值低（标准在变）。唯一值钱的本地资产 = 验证过的 POP 签名器（`harness/golden/verify_oracle.py` + `pop_sign`），将来作端到端链路里"签名步骤"的验证器。

**⚠️ 头号 blocker**：POP live 轨道可能**无沙箱**——本人 KB [[sandbox-environment-design]] 已记「得物无 sandbox」。若属实，改造前后的 live ΔTSR（最硬证据）平台层面就走不通，得退守 doc-only 端到端。**下次先确认得物有无可执行测试环境。**

**下一步（v0.3 §9 落地顺序）**：
1. 写第一个场景四件套：**POP × 集成模式 P1「依赖式幂等写」= Playbook A（货号→定价→挂单）**，含 A0–A4 提示阶梯。
2. 搭**渐进披露 harness**（从 URL 起跑、卡住注入提示、按 rung 计分）—— 目前不存在，是大头新工作。
3. 加 Stripe（doc 可静态抓）做第一张横评对照。
4. 视沙箱结论决定 live 轨道是否可行。

**待拍板（标准 §10）**：集成模式数量 / 模型选型（Claude+GPT?+国产?）/ doc-only 公开 surface 边界 / grounding 强制度 / 阶梯粒度（整链 vs 步骤注入提示）/ token 跨模型可比性 / 沙箱可得性。

---

## 决策日志（append-only，含 why）

### D1 — 测量单位：原子单接口 → 端到端场景 [2026-06-16]
单接口 doc-only 能不能调通**毫无信息量**（实测 POP 签名/寄售写都 100%）。真正难点（116 API 选哪个 / 字段多步流转 / 单位陷阱）只在多步链路暴露。→ 只测端到端。

### D2 — 头号指标改名：FPSR → TSR（Task Success Rate）[2026-06-16]
"First-Pass" 名实不符：字面"第一次尝试"，定义却是"不靠人工修改"；且 agent 端到端必然循环自纠，"第一次"无意义。TSR 钉死为「不靠人工干预、在 token 预算内、产出满足全链路全部验收断言的集成」。doc-only 单次采样档 ≈ pass@1。"靠不靠试错才成"挪到成本族 `iterations-to-success`。

### D3 — 加第二条头号轴：token 成本（tokens-to-success）[2026-06-16]
与成功率正交、不折叠成一个分。**是 Layer 4「可 fetch 文档」改造价值的唯一可见度量**——该改造往往不动成功率却把 token 砍一个数量级（POP 文档站 JS-SPA，agent 只能截图/OCR，~10× token）。比原"工具调用次数"准：截图是 1 次调用却吃几千 token。

### D4 — 打分 0/1 → A0–A4 自主度阶梯 [2026-06-16]
按"恢复需多重人工干预"分级：A4 自主 / A3 指路可救 / A2 点破可救 / A1 喂码才救 / A0 死锁。**关键洞察：提示是哪一种 = 哪层坏 = 改造项，打分即诊断。** 头号 TSR 只数 A4；阶梯直方图作严重度剖面（区分"点破就行"和"喂码也没用"）。提示阶梯须预注册冻结，防"钓提示"作弊。

### D5 — doc-only 与 live = 同一端到端任务，两种验证深度 [2026-06-16]
静态 golden 轨迹比对 / 沙箱真执行。消除旧版"两者粒度不同"的别扭。doc-only 抓"agent 把文档暴露的一切都用对了"，live 额外抓 runtime-only 失败（签名时序、真实幂等、文档没写的必填字段）。

### D6 — 场景集 = 冻结的"四件套"交付物 [2026-06-16]
每场景 = ① 开发者需求 ② golden 全链路轨迹 ③ 步骤级验收断言 ④ 提示阶梯。这是 benchmark 本体，最费脑最值钱。跨平台可比靠"集成模式"定义场景。原 T1–T6 archetype 降级为"步骤类型 + 诊断标签"。

### D7 — harness 暂不入库 [2026-06-16]
spike 复用价值低 + 标准在变 → gitignore、本地保留，等 v0.3 结构定型再放回。

### 工作流约定
直接推 main，无分支无 PR（仅在被要求时提交）。文档默认 Markdown。

---

## 会话日志（append-only，最新在上）

### 2026-06-16 — 从 FPSR 解释到 v0.3 定型 + 首个实跑
- 起点：仓库只有 v0.1 标准（FPSR + 6 原子 archetype）。
- 搭首个 harness，POP doc-only 跑 20 个隔离 agent：T1 签名 5/5、T3 寄售写 5/5（两版，含泄题版）。
- **POP 实测发现**（喂进真正的 scorecard）：
  - L4：open.poizon.com 是 JS-SPA，静态 GET 返回空壳，参数表只能截图 → 只会 HTTP GET 的 agent 读不到文档。
  - L2：自带签名 worked example **自相矛盾**——输入 JSON timestamp(1603354338917) 复现不出 claimed sign(A0BC…)，claimed 只能用 1603353500369 复现 → 忠实照文档做 = 0% 复现。
  - L1：寄售写接口（enterprise-stock-apply/add）**无 requestId 幂等键**。
  - 方法论教训：首版 T3 测出 100% 是因为**把 required 参数喂进了任务** = "假绿"在自己的测量装置里复现。→ 标准 §7 新增两条威胁：harness 泄题、钓提示。
- 标准演化：v0.1 → v0.2（加 token 轴）→ v0.3（端到端 + TSR + 阶梯 + 四件套，见决策 D1–D6）。
- 收尾：harness 移出 repo（D7）；KB 建跟进页并登记进 open-platform-index；建本 log。
- commits：`ab40c40` v0.1 初始 → `9e8a345` v0.2 token 轴+harness → `18cb666` v0.3 整合 → `6959b7e` 移除 harness tracking。
