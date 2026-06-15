---
title: "Agent-Ready — 开放平台 Agent 友好化评分模型设计"
project: agent-ready
type: design-spec
version: v0.2 (draft)
created: 2026-06-14
updated: 2026-06-16
status: 设计中
related:
  - "[[agent-friendly-open-platform-design]]"  # 四层框架（被测对象的诊断骨架）
  - "[[open-platform-metrics]]"                  # AI 友好度指标（FPSR 出处）
---

# Agent-Ready：开放平台 Agent 友好化评分模型

> 一句话定位：**一个行为性 benchmark，量一个开放平台对 AI agent 到底有多友好。**
> 两条正交头号轴：**成功率** First-Pass Success Rate（FPSR，第一次就做对的比例）+ **成本** tokens-to-success（做对花多少 token）。给真 agent 一组标准任务、只准用平台公开文档/接口，二维呈现，不折叠成一个分。

---

## 0. 这份文档要解决什么

把"开放平台 agent 友不友好"这个**模糊判断**，变成一个**可测量、可复现、可驱动决策**的评分模型。具体产出三样东西的设计：

1. **怎么测**（两条头号轴 FPSR + tokens-to-success 的精确定义 + hybrid 测量协议）；
2. **测什么**（跨平台标准任务集）；
3. **怎么打分 + 怎么呈现**（双层评分架构 + scorecard + 榜单）。

两个用途**等权**服务，且共用同一套评分：
- **公开 benchmark**：横评 Stripe / Shopify / 微信 / 飞书，发 GitHub + 方法论文章；
- **POP 改造前后**：用同一把尺子量自家改造的效果增量。

---

## 1. 第一性原理：到底在评什么

**被测对象不是"文档好不好看"，是"agent 能不能一次做对"。**

退回到最根本的判断标准：一个 agent，拿到一个集成任务 + 平台的公开 surface（文档 / schema / 接口），**不依赖人工修改，第一次就产出正确集成**的概率有多高。这个结果（outcome）就是平台 agent 友好度的硬定义。

由此推出三条设计约束：

1. **结果优先于过程。** 不能靠"文档清晰度打 1–5 分"这种软指标当头号度量——它可注水、可自卖自夸。头号指标必须是**行为性的**（agent 真去做、做没做对），这是硬验证器。
2. **但结果是黑箱，需要诊断层解释。** 光有 FPSR 知道"差"，不知道"为什么差、改哪里"。所以四层框架（API Quality → Semantic Clarity → Navigation → Callable Interface）退一步当**诊断层**：解释 FPSR 为什么是这个数，并直接产出改造 backlog。
3. **可复现是公信力的唯一来源。** （呼应"假绿"教训——一次跑绿不可信。）任务集、golden、跑分日志、harness 全部公开，多次跑取均值+方差，别人能复现才算数。

> **心智模型沿用框架原文**：agent 不是"更聪明的用户"，是"有限上下文的代码生成器"。它只能消费被显式表达的语义，不靠经验推断。整套评分都站在这个假设上。

---

## 2. 双层评分架构

```
┌─────────────────────────────────────────────────────────┐
│  Tier 1 — 结果层：两条正交头号轴（行为、客观、硬验证器）  │
│  轴 A  成功率 FPSR        "第一次做对几个"                │
│  轴 B  成本 tokens/成功   "做对花了多少 token"            │
│  二维 scorecard，不折叠成一个分                           │
└─────────────────────────────────────────────────────────┘
              ↑ 解释 / 定位失败原因 ↓
┌─────────────────────────────────────────────────────────┐
│  Tier 2 — 诊断层：四层 rubric（客观项 + 主观项混合）      │
│  解释 FPSR/成本、定位失败模式、产出改造 backlog           │
│  Layer1 API Quality / Layer2 Semantic / Layer3 Nav /     │
│  Layer4 Callable Interface                                │
└─────────────────────────────────────────────────────────┘
```

**关键原则一：两层不混成一个分去排名。** 榜单**按 Tier 1 两条轴排序**（行为性、难注水）；四层 rubric 以**雷达图/分项**形式呈现，回答"为什么是这个成绩"。可选综合指数（ARI，见 §6）明确标注为诊断辅助视图，不是排序依据——否则退化成可注水的复合分。

**关键原则二：成功率与成本正交，分两条轴报，不折叠。** 一个平台可以 FPSR 100% 却 token 成本极高（典型：文档站是 JS-SPA，agent 只能靠截图/OCR 绕，最终做对但代价 10×）。只看 FPSR 会给这种平台满分；成本轴才让它露馅。**成本轴还是 Layer 4「可 fetch 文档」改造价值的唯一可见度量**——该改造往往不动 FPSR（agent 靠截图也能成），却把 token 成本砍掉一个数量级。

---

## 3. Tier 1 两条头号轴：精确定义与测量协议

### 3.1 指标层级

| 指标 | 轴 | 定义 | 用途 |
|---|---|---|---|
| **FPSR-strict** | A 成功率（头号） | 单任务全部验收点一次通过 = 1，否则 = 0；对任务集取均值 | 榜单排序、对外引用 |
| **Tokens-to-success** | B 成本（头号） | 成功 run 完成任务消耗的总 token（input+output+图像 token）均值 | 榜单第二轴、量 Navigation/Callable 层 |
| **Criterion pass rate** | 诊断 | 任务内验收点级别的通过率（部分得分） | 失败定位、改造前后细粒度对比 |
| **Tool-call count** | 诊断 | 完成任务的平均工具调用次数 | 辅助诊断；**注意它会低估 L4 惩罚**——截图是 1 次调用却吃几千 token |

"一次通过"= agent 输出的集成代码/答案满足该任务**全部验收点**，无需任何人工修改。验收点是**具体可判定的检查**（见 §4），不是主观印象。

> **为什么用 token 成本而非工具调用次数当头号效率轴**：截图/OCR 是 1 次调用但吃几千 token，markdown fetch 也是 1 次调用却只几百 token——用调用次数数，两者看起来一样；用 token 数，差距才暴露。token 成本是设计文档原「20+ → 5 次」效率目标的正确推广。

### 3.1b Tokens-to-success 的测量纪律（让成本轴可信）

1. **只在成功 run 上计成本**，失败 run 的 token 没定义（可能空转到预算上限）→ 失败/超时率单列另报。
2. **固定 model + harness 横评，只报相对值。** token 数依赖模型（图像 tokenization 各模型不同）与工具集，绝对值不可跨模型搬运；有意义的是同一模型同一套工具下「平台 A vs B」或「POP 改造前 vs 后」的差。分模型报，跑 K 次取均值±方差。
3. **必须与 FPSR + grounding 联读，防"便宜但作弊"。** 被模型背过的平台（如 Stripe）token 会偏低——那是记忆不是文档好（与 FPSR 同源的训练污染，见 §7）。"便宜"只在 grounding（真去读了文档）前提下才算平台的功劳。POP 改造前后两边都无记忆优势，这条轴最干净。

### 3.2 Hybrid 测量协议（核心可比性设计）

> 决策：竞品用 doc-only，POP 用 live。但这带来一个陷阱——**两种方法测出的数不可直接比较**。解法如下。

**doc-only（代码生成）—— 跨平台可比的主指标，5 个平台全做（含 POP）**
- agent 只拿到平台**公开文档快照**，产出集成代码，对 golden 验收点打分。
- 无需任何平台凭证，对 Stripe / Shopify / 微信 / 飞书 / POP **完全一致**，任何人可复现。
- 这是**公开榜单排序所用的唯一可比指标**——POP 和竞品坐在同一张榜上，无特殊待遇。

**live（真实执行）—— 仅 POP，额外的深度轨道**
- agent 真去调 POP 沙箱 API，量真实第一次成功率。
- 用途：改造前后的最硬证据 + 抓 doc-only 抓不到的 runtime-only 失败（如签名、时序、幂等真实行为）。

**可比性的关键招：POP 同时跑两种方法。**
```
公开榜单：       doc-only FPSR（含 POP，和竞品同尺）
POP 改造叙事：   doc-only FPSR（可比基线） + live FPSR（额外深度）
交叉验证：       两个数应同向变动 → 同向 = 验证了 doc-only 作为代理的有效性
```
这样既满足"等权"（同一套 doc-only scorecard 服务公开 benchmark），又给 POP 加了一条 live 轨道服务内部改造证据。

### 3.3 跑分控制（让数可信）

| 控制项 | 做法 | 为什么 |
|---|---|---|
| **模型标准化** | 固定 ≥2 个模型（如 Claude + GPT），分别报告 | 避免单模型 artifact；agent 友好度不该只对一个模型成立 |
| **方差控制** | 每任务跑 K 次（建议 3–5），报均值 ± 方差 | 呼应"假绿"——单次跑绿不可信 |
| **上下文隔离** | doc-only 时 agent 只喂该平台公开文档，禁联网搜其他来源 | 隔离"文档质量"与"模型外部知识" |
| **Grounding 要求** | 要求 agent 对每个字段/接口选择**引用文档出处**，无出处的正确不计为"文档驱动成功" | 见 §7 训练数据污染 |
| **Token 预算上限** | 每任务设硬上限（如 200k token），超限判失败 | 让 tokens-to-success 有界、可比；防 agent 在烂文档上空转刷成本 |
| **冻结** | 任务集 + 验收点 + harness + 模型版本 + 工具集，跑一个平台前全部冻结并记录 | 可复现 + 防止事后调任务美化结果；工具集冻结对成本轴尤其关键 |

---

## 4. 标准任务集

### 4.1 难点与解法：异构平台怎么可比

五个平台跨了三个域：支付（Stripe）、电商（Shopify、POP/得物）、IM/协作（微信、飞书）。"创建商品"在飞书不存在。

**解法：不按业务对象定义任务，按"集成原语"（archetype）定义。** 每个 archetype 是所有开放平台都有的跨域能力，在每个平台上实例化成一个具体任务 + golden 验收点。FPSR 在 archetype 上计算，于是异构平台可比。

### 4.2 六个 archetype（v1）

| # | Archetype | 跨平台实例（示例） | 主要压测的层 |
|---|---|---|---|
| **T1** | 鉴权 / 拿 access token | Stripe key、Shopify OAuth、微信 access_token、飞书 tenant_access_token、POP 鉴权 | Navigation（找得到流程）+ API Quality |
| **T2** | 读一个核心资源 | Stripe customer / Shopify product / 微信用户信息 / 飞书用户或文档 / POP 订单 | Semantic Clarity（字段语义）+ Navigation |
| **T3** | 带幂等的写操作 | Stripe PaymentIntent / Shopify 建单 / 微信模板消息 / 飞书发消息或建记录 / POP 挂单或调价 | API Quality（幂等）+ Semantic（单位/requestId 等陷阱） |
| **T4** | 分页列表查询 | 各平台列表接口 + 翻页 | Semantic Clarity（游标/分页语义） |
| **T5** | 处理 webhook / 回调 | 各平台事件回调：验签 + 解析事件 | API Quality（结构化 payload）+ Semantic（验签陷阱） |
| **T6** | 错误恢复 | 触发一个具体错误（限流/重复请求）并正确处理 | API Quality（结构化错误码）+ Semantic（错误处理示例） |

> archetype ↔ 层 的映射是**故意设计**的：哪个任务挂了，直接指向哪一层的缺陷，失败定位天然内建。

### 4.3 单任务的验收点（以 T3「带幂等的写」为例）

每个 archetype 在每个平台落成一张 golden 卡，列**具体可判定**的验收点。例如 POP 挂单：

```
T3 / POP 挂单 — 验收点（全过才算 first-pass success）
[ ] 用对了接口（submit-bid，而非 query/recommend）
[ ] price 用货币最小单位（分），$154.00 → 15400         ← Semantic 陷阱
[ ] requestId 作为幂等键，生成新 UUID                    ← Semantic 陷阱
[ ] skuId 优先于 globalSkuId                              ← Semantic 陷阱
[ ] 处理了文档列明的错误码（如 DUPLICATE_REQUEST_ID）     ← API Quality
[ ] 每个上述选择都附了文档出处引用                        ← Grounding
```

任意一条不过 → FPSR-strict 该任务记 0；criterion pass rate 记 5/6。

---

## 5. 四层诊断 Rubric（Tier 2）

每个维度标注**客观（O）/ 主观（S）**及打分方式。客观项走确定性检查，主观项走 LLM-as-judge（带校准）。

### Layer 1 — API Quality（地基，多为客观）
| 维度 | O/S | 打分方式 |
|---|---|---|
| 结构化错误码 | O | 错误响应是否含机读字段（error_code/error_type/hint）；按样本接口比例打分 |
| 幂等性 | O | 写接口是否幂等、幂等键是否显式标注 |
| 参数命名一致性 | O | 同一语义概念是否全平台单一字段名；抽样检测冲突率 |
| Scope 粒度 | S | 是否按场景聚合、能力语义是否自解释（LLM-judge + 人工校准） |

### Layer 2 — Semantic Clarity（对 FPSR 影响最直接，混合）
| 维度 | O/S | 打分方式 |
|---|---|---|
| Integration Notes / 陷阱说明 | O+S | 是否存在（O）+ 是否覆盖真实陷阱（S，LLM-judge） |
| 枚举值集中页 | O | 是否有独立 Reference 页、是否散落 |
| Error Handling 示例 | O | 详情页是否配 2–3 个错误场景完整示例 |
| 字段名→语义可推断性 | S | 给字段名+描述，judge 能否推出单位/含义；**用你的人工标注当 ground truth 校准** |

### Layer 3 — Navigation（解决有限上下文，混合）
| 维度 | O/S | 打分方式 |
|---|---|---|
| 场景化 Playbook | O+S | 是否存在（O）+ 场景内字段流转是否唯一确定（S） |
| Fact Sheet 全量索引 | O | 是否一次 fetch 拿全、是否依赖 JS/多步交互 |
| llms.txt | O | 是否存在 + 内容是否聚焦陷阱/枚举/playbook |
| **工具调用次数** | O | 即 §3.1 的 tool-call efficiency，行为性测得 |

### Layer 4 — Callable Interface（工程最重，多为客观）
| 维度 | O/S | 打分方式 |
|---|---|---|
| 可 fetch 文档 API | O | GET 是否返回机读 markdown/json |
| OpenAPI Spec 覆盖率 | O | 是否存在 + 覆盖接口比例 |
| MCP 接口暴露率 | O | 是否提供 MCP + 覆盖能力比例 |

### LLM-as-judge 的防注水设计
主观项不打"感觉分"。每个主观维度：(1) 给 judge **具体锚点示例**（什么算 5 分、什么算 1 分）；(2) 要求 judge **逐条引用证据**再打分；(3) 用**你的人工标注**在抽样集上校准 judge，报告 judge 与人工的一致性（如 Cohen's κ）。judge 不可靠的维度降级为纯客观项或人工。

---

## 6. 综合呈现

**榜单（对外）**：二维呈现——主排序 **doc-only FPSR-strict**，并列报 **tokens-to-success**（同模型同 harness 下可比）。理想平台落在「高 FPSR + 低 token」象限；JS-SPA 这类平台会显形为「高 FPSR + 高 token」。附均值±方差、分模型。

**单平台 Scorecard**：
```
平台：______        模型：______        日期：______
─────────────────────────────────────────────
轴 A  FPSR-strict        ██████░░░░  62%   (±8%, n=5×6 任务)
轴 B  Tokens-to-success            48.3k  (±12k, 仅成功 run)
      失败/超时率                  18%
─────────────────────────────────────────────
Criterion 通过率                   78%
平均工具调用次数                    9.2
─────────────────────────────────────────────
四层雷达：  L1 ███░░  L2 ██░░░  L3 ████░  L4 █░░░░
Top 失败模式：
  1. T3 price 单位错（Semantic）          5/5 平台×模型挂
  2. T5 验签算法猜错（Semantic/API）      ...
  3. T1 token 刷新流程找不到（Navigation） ...
Top 成本黑洞：
  1. 文档站 JS-SPA，参数表只能截图/OCR 获取  → ~10× token（指向 L4 可 fetch 改造）
  2. 无 Fact Sheet，逐页点开找接口            → 多轮导航（指向 L3）
```

**可选综合指数 ARI（Agent-Readiness Index）**：`ARI = 0.6 × FPSR + 0.4 × 四层 rubric 归一分`。**明确标注为诊断辅助，非排序依据。** 建议 v1 先不强推 ARI，避免复合分稀释 FPSR 的硬度；先把 FPSR + 雷达跑扎实。

---

## 7. 效度威胁与解药（这一节是 eval 产品 sense 的核心）

| 威胁 | 说明 | 解药 |
|---|---|---|
| **训练数据污染** | Stripe 在所有模型训练集里，POP 不在。doc-only FPSR 会偏向 Stripe，**不是因为它文档好，而是模型背过**。 | (1) **Grounding 要求**：正确但无文档出处的不计为"文档驱动成功"，测的是文档而非记忆；(2) 选**不易被记忆的任务/边缘参数**；(3) 可选**doc-ablation**：抹平台名/换代号跑，隔离品牌熟悉度；(4) 作为已知局限公开声明——也正因如此，**POP 的改造前后 delta 是最干净的信号**（同法测、无记忆优势）。 |
| **自卖自夸**（自造标准又恰好证明自家变好） | 公信力风险。 | (1) POP 同法上同一张榜，无特殊待遇；(2) 改造前**预注册**任务集+验收点，事后不可改；(3) 公开方法论+golden+跑分日志；(4) 第三方平台锚定刻度，POP 的数只在相对位置上才有意义。 |
| **假绿**（单次跑通即宣称成功） | 呼应本人血的教训。 | 每任务跑 K 次取均值±方差；公开原始 run log；验收点机器可判定，不靠人眼"看着对"。 |
| **任务集偏置** | 任务选得巧可美化某平台。 | archetype 是跨平台中立原语；任务集冻结+公开+版本化；欢迎外部 PR 加任务。 |

---

## 8. POP 改造前后协议

```
1. 改造前：冻结任务集/验收点/harness/模型 → 跑 doc-only + live → 记为 baseline
2. 实施改造（你已提需的 POP agent 友好化改造点）
3. 改造后：同一冻结配置重跑 → 记为 post
4. 报告（两条轴都报）：
   - 轴 A：doc-only ΔFPSR（可比，进公开榜单）+ live ΔFPSR（额外深度）
   - 轴 B：Δtokens-to-success——L4「可 fetch 文档」改造的价值主要落在这条轴上（FPSR 可能不动，token 砍一个数量级）
   - 同轴改造前后同向 → 互证；并列出每个改造项消除了哪个 Top 失败模式 / 哪个成本黑洞
```

证据强度：`"POP 改造后 doc-only FPSR 从 X% → Y%，且 live 同向；tokens-to-success 从 48k → 6k（约 8×，因可 fetch markdown 文档消除截图/OCR 路径）；#1 失败模式（price 单位）因新增 Integration Notes 被消除。"` —— 两个正交硬数字，比单一 FPSR 更能体现改造全貌，是简历里"shipped & measured"的开发者侧硬指标。

---

## 9. v1 范围与执行路线

**v1 锁定：**
- 6 个 archetype × 5 平台（Stripe / Shopify / 微信 / 飞书 / POP）；
- doc-only 全平台 + POP 额外 live；
- 2 个模型 × 每任务 5 次；
- 两条头号轴（FPSR + tokens-to-success）+ 四层雷达 + Top 失败模式 + Top 成本黑洞；ARI 暂缓。

**建议落地顺序（先客观闭环、再扩主观）：**
1. 先定 golden 验收点（最费脑、最值钱的设计活）；
2. 搭 doc-only harness（与你已有 loop harness 同构）→ 先跑通 Stripe + POP 两个平台闭环；
3. 接 LLM-as-judge 做诊断层，用人工标注校准；
4. 补齐另外三个平台横评；
5. POP live 轨道 + 改造前后。

**Surface 分工**（沿用上次结论）：评分模型设计/竞品文档研究/方法论写作在 Cowork；harness 实现+跑分+GitHub commit 在 Code 标签。

---

## 10. 开放问题（需你拍板）

1. **archetype 数量**：6 个够不够？要不要砍到 4 个先跑通，还是加"OAuth 授权用户态"第 7 个？
2. **模型选型**：固定哪两个模型当标准被测 agent？（Claude + GPT？要不要加一个国产模型以示中立？）
3. **doc-only 的"公开文档"边界**：只算官网文档站，还是含官方 SDK README / OpenAPI 文件？边界要写死才可复现。
4. **grounding 强制度**：无出处的正确"不计成功"会不会太严？还是降级为"标记但仍计分 + 单列 grounded-FPSR"？
5. **ARI 要不要进 v1**：还是坚持只露两条头号轴 + 雷达？
6. **tokens-to-success 的跨模型可比性**：图像 token 各模型口径不同，是否只在「同模型」内做改造前后/平台对比，公开榜单分模型列两套 token 数？还是引入一个归一化基准任务做缩放？
