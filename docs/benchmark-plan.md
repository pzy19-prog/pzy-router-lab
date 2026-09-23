# Phase 0 统一路由基准协议

**协议版本：** `phase0-v2`

**状态：** 协议设计与合成开发数据已冻结；正式实验尚未预注册、尚未获准开始。未运行任何 Laya、RouteLLM 或 vLLM Semantic Router 模型评测，也未做付费调用。`data/phase0-cases.jsonl` 与 `data/phase0-prompts.jsonl` 是已公开的合成开发/协议验证输入，不是真实任务数据或模型结果，不能作为独立 heldout 测试集。

## 1. 研究问题与比较对象

同一测试案例、候选模型池、隐私约束和执行结果标注下，语义/学习型 router 是否比本地 Rules 提高任务成功率，并且成本、时延和隐私风险满足预算？不以“路由决策看起来更聪明”或 README benchmark 代替真实执行结果。

候选：

- **Rules**：本仓库当前确定性 `routing-v0` 实现。
- **Laya**：适配 typed decision 到路由类别/目标；仅本地 CPU checkpoint 实测。Rules 的风险/敏感级别 veto 必须在其外层保持有效。
- **RouteLLM**：在明确固定的 strong/weak model pair 上测 `mf` 或其它单个指定 router；先过许可证、依赖、embedding/API、版本活跃度 gate。
- **vLLM Semantic Router**（扩展候选）：选定一个本地分类/决策 recipe，测真实 route preview；若完整 runtime 超出可用预算，则作为技术对照不实测，记为排除原因。

结果表必须写出候选**实际运行版本**、checkpoint revision 和 sha256、tokenizer、设备、dtype、依赖锁定文件、配置文件 hash。候选无法做同一接口决策时不得伪装成 1:1 完全可比；将其标为 adapter/wire-integration track。

## 2. 案例集和拆分

`data/phase0-cases.jsonl` 每行一个合成 request metadata 案例；`data/phase0-prompts.jsonl` 用同一 ID 提供实际合成任务输入、rubric、执行模式和判分方法。唯一连接规则为 `case_id == prompt_fixture_id == fixture_id`。Rules 输入只含其 contract 接受的路由元数据，并使用 `task_id == case_id`；Rules 不接收 task prompt。CLI receipt 的 `input_digest` 必须是该精确 Rules 输入规范 JSON 的 SHA-256。`examples/phase0-rules-receipt.json` 是 CLI 以 `data/phase0-p0-001-rules-input.json` 实际运行得到的 p0-001 receipt；`examples/example-rules-receipt.json` 是单独的 EXAMPLE-LOW-001 示例。前者是执行记录，后者是示例；二者都不是模型任务执行结果。`examples/phase0-evidence-design.json` 明确标为未来 evidence 结构的**设计样例**，链接前者而不冒充 benchmark 运行结果。数据文件 SHA-256 和数据版本记录在 `data/phase0-freeze.json`；修改案例或 rubric 必须升 data version 并重做协议审核。

覆盖类别：低成本直答、中文/英文、代码/数学等较复杂任务、缺失/未知信号、高风险人工复核、confidential cloud 禁止、本地目标缺失、provider outage、local-only 与 cloud opt-in。该小集合只适用于可行性/协议验证，不足以代表线上分布或支持效果推断。

**语言标注规则：**按任务原文中要求完成工作的自然语言指令标记语言；代码、标识符、数字和被分析的引用材料不决定语言。若指令实质上要求用两种语言完成，标为 `mixed`。若缺少明确指令，则按需处理的主要自然语言内容标记；无法唯一判断时标为 `mixed`。执行 checkpoint 必须覆盖该标签中要求的所有语言（或为 `mixed` 使用经预注册确认支持所有相关语言的多语 checkpoint）；否则该案例/配置不合格并报告排除，不得改写原任务来迁就模型。Rules metadata baseline不读取 prompt，也不据语言选择 checkpoint；语言/能力匹配由执行适配器按冻结清单验证。当前 p0-001 和 p0-003 为英文指令，其余 10 个案例为中文指令；p0-007 中的代码不改变中文标签。

- 当前 12 个案例全部是 `dev`，只用于开发和协议验证，不报告为 held-out 指标。它们已公开并用于阈值/协议讨论，禁止重新命名或移作 heldout。
- 独立测试集必须在正式实验前由数据所有者新建、封存并版本化；在其来源、样本量依据、访问控制和隔离审核完成前，`independent_test` 状态为 **PRE-REGISTRATION REQUIRED**。不得使用当前合成案例填充这一集合。
- 正式数据按 `train`（拟合/训练；本项目当前无训练计划）、`dev`（开发和选择）、`independent_test`（锁定后最终评估）三类互斥划分。案例 ID 与内容哈希不得跨集合复用；模型预训练语料不是本实验 train split。当前 train 与 independent_test 均不存在，正式拆分为 **PRE-REGISTRATION REQUIRED**。
- `provisional_gold.target_class` 是作者按当前元数据和预想能力写下、尚未独立审阅的**路由假设**；`status=unreviewed_hypothesis` 是唯一允许的当前状态。它既不是实测标签，也不是模型/执行结果。本轮不得据此计算或宣称 decision accuracy、模型胜负或实际路由质量。
- 将来若要产生 `verified_gold`，至少两位标注者必须在看不到 router 输出和执行结果的情况下，按书面路由标准独立判断；冲突由第三人裁定，记录版本与裁定。只有冻结后的 verified set 可用于报告 decision accuracy。当前数据没有 verified gold。
- `acceptance_criteria` 是任务 outcome rubric，与 provisional route hypothesis 分开。未来仅对 `execution_mode=execute_and_grade` 的任务运行同一固定执行器；由不知道 router 身份的 reviewer 按 fixture 中逐项规则盲评。所有必需项通过才记 success，否则 failure；超时、拒答、格式错误按 rubric 记失败或单列 abstention。`policy_only` 只检查安全/可用性决策，不产生 task success 标签。
- prompt fixture 内容都是人工构造的合成实际任务输入，不是从用户日志抽样。报告 fixture ID 和文件 hash，不记录 secrets/真实 PII；confidential 是策略测试标签，任何 confidential fixture 禁止发往 cloud。

## 3. 三种测试类别（不可混报）

| 类别 | 内容 | 可支持的结论 |
|---|---|---|
| **模拟测试 (simulation)** | 预先编写 stub router/executor 响应，用来测 schema、决策 receipt、状态流转、超时/异常和升级 policy；stub 固定延迟/成本是人为参数 | 只证明控制逻辑按预期工作；不得声称模型准确率、实际 task success 或真实 latency/cost |
| **离线测试 (offline)** | 已 pin 并本地缓存权重；关闭网络；真实 router 在固定合成集上做决策。Rules 全程必须能在网络关闭时工作 | 可报告 router-only decision/latency；若无 executor，执行成功率、token/cost、云 outage 降级均不应报为实际值 |
| **真实模型实测 (real-model)** | 固定本地或获明确授权的非付费测试 endpoint、真实模型执行任务；显式授权/预算后才可执行。本轮禁止付费 API | 允许报告端到端 outcome、actual tokens、真实端到端 latency；每个 endpoint 需记录价格来源/日期，实际支出需 0 或预授权非付费额度 |

本轮仓库测试只验证 Rules 行为及 fixture 结构，不是上述三类基准数据中的 model benchmark。计划数据集尚未运行。

## 3.1 执行步骤与结果判定

当前仓库没有模型 adapter、executor 或 benchmark runner。以下是后续获批实验的固定方法，不表示已经执行：

1. 冻结数据/fixture/rubric hash、adapter commit/config、checkpoint、依赖与执行环境；先只在 dev 做映射/合同检查。独立测试集必须另行封存并经审核，当前尚不存在。不得用 independent_test 修改任何配置。
2. 对每个实验 track 应用下述输入规则；记录实际提供给 router 和 executor 的输入摘要。共同 policy guard、目标可用性场景与 executor 版本固定；记录拒答、错误、超时和 fallback，不删样本。
3. `policy_only` 案例不调用 executor，逐项检查 fixture 的路由/隐私 invariant；任一 confidential cloud route、不可用目标 route 或应人工复核却未复核即该项失败。`execute_and_grade` 仅在允许的 executor 上执行同一 prompt，保存 attempt 序列和原始输出的脱敏/合成记录，盲评 acceptance criteria。
4. 先完成 Rules 与候选的 dev smoke，再评估独立测试集；比较采用配对 case。报告原始计数、分母、每 case outcome、decision 及 execution 分层。仅在存在 verified gold 时算 decision accuracy；provisional hypotheses 只可列作待审设计数据，不进指标。
5. 预定主要指标为 end-to-end track 的盲评 task success rate；安全不变量（confidential 不出 cloud、不可用目标不被报告可用、未知风险 fail-closed）是绝对验收条件。Controlled track 只有在 independent_test 有 verified gold 后才报告 decision accuracy。成本与时延为预算约束指标。具体非劣界限、预算、样本量及统计检验依据均为 **PRE-REGISTRATION REQUIRED**；当前不能作实证通过/失败判定。

## 4. 输入能力、比较轨道与场景控制

报告必须先区分三类内容：

- **共同可见路由元数据**：`case_id/task_id`、复杂度、风险、敏感级别、可用目标、cloud opt-in 和场景状态。各轨道中按冻结 mapping 提供；缺失值必须保持缺失，不能从 task prompt 推导后只给部分 router。
- **任务原文**：prompt fixture 的原始 `task_input`，用于真实任务执行；本身不是 `routing-v0` 字段。
- **实际 router 执行输入**：每个 adapter 真正支持且收到的序列化数据，逐方法记录其字段与摘要。禁止把计划输入描述成已执行输入。

当前 Rules `routing-v0` 只接受 `task_id`、`complexity`、`sensitivity`、`risk`、`available_targets` 与可选 `allow_cloud`。它拒绝未知字段，不读取 prompt。该安全约束保持不变；Rules 的输入只需包含上述受支持的共同元数据子集，不向 Rules 注入 task text。

| 比较轨道 | 决策输入 | 可回答的问题和报告边界 |
|---|---|---|
| **A. Controlled Routing Comparison** | 仅用所有纳入方法共同支持的路由元数据字段及相同可用性状态。不得提供 task prompt；如公共交集为空或某方法不能接受完全相同的序列化能力，则该方法不进入此轨道。 | 比较同一信息条件下的 routing decision、policy invariant、router latency；只可用 verified routing labels 评估 decision quality。不能据此推断任务回答质量。Rules 用原生受支持字段运行，禁止添加未知字段。 |
| **B. End-to-End System Comparison** | 每个 Router 使用其正式 adapter 实际支持的输入。task fixture 的原文和共同元数据都可提供给支持它们的组件；Rules 继续只收元数据，prompt 交给选定 executor。 | 比较完整系统的盲评任务结果、总成本、router 与端到端时延、错误/拒答/升级。逐 router 列出实际输入能力差异、adapter 映射与执行模型；结果只代表这些端到端配置，不解释为 router 单体因果效应。 |

两个轨道分表报告、分开计算与解释。禁止把 A 的决策指标和 B 的任务 outcome、成本或时延拼接成一个胜负结论。相同案例原文与 rubric 保持固定；模型不能处理该案例语言时，按预注册规则标为配置不合格/排除并报告，不得改写输入。所有实际 router 输入与 task prompt 均记录 fixture ID、版本/hash 和字段清单；隐私 guard 在两轨道中相同且先于任何 cloud 发送。

适配规则：Rules 使用原生 `routing-v0` JSON，不扩充字段；Laya 使用经 pin 的 typed-decision adapter，仅传其 contract 支持且策略允许的字段；RouteLLM 使用固定的模型对/评分器与它所需的 prompt 输入，只纳入允许的非机密案例；vLLM Semantic Router 使用冻结 recipe 实际声明的 signals。每个 adapter 必须有能力清单，字段映射不得静默丢失或合成。配置中不可表达的共同字段标记 unavailable，并依预注册纳入/排除规则处理。所有 cloud opt-in、confidential、risk veto 由相同外层本地 hard-policy guard 执行，不允许模型覆盖。

场景成对运行：

1. **Available-set**：相同目标池，先 local-only，再按明确 opt-in 加 cloud。
2. **Confidential**：即使模型建议 cloud，也强制期待拒绝/人工复核；不得发送 confidential case 文本至任何网络 endpoint。
3. **Outage**：将 target availability 输入 adapter 或统一 policy wrapper，移除一个本地目标、所有本地目标或 provider，确认 unavailable target 从不被报告成 available。区分真实健康探测与模拟 health state。
4. **Router unavailable**：断网、进程异常、timeout，Rules fallback 独立执行；若 Rules 也不能执行，则 fail-closed/manual review，不隐式发 cloud。
5. **Long-task failure**：先运行 executor 才能测；固定 task ID、attempt budget、失败判定及升级路径。没有真实 executor 的用例只作 simulation。

真实执行时所有比较方应使用同一版本的执行模型、system prompt 和解码设置（当这些能力相同且配置可用时）。无法一致的配置按 end-to-end system track 报告其差异，不并入 controlled track。具体模型版本和语言能力须在冻结清单中 pin；checkpoint 不支持案例语言则排除该配置，不改任务原意。

## 5. 指标及计算口径

| 指标 | 定义/报告 |
|---|---|
| Decision accuracy | 仅 verified gold 存在时，以 raw target class 精确匹配 verified label 计数/有效 cases；报告分母、混淆矩阵、按隐私/语言/复杂度分层计数。只有 provisional gold 时为 **UNKNOWN**，不得算准确率 |
| Task success rate | 按 fixture acceptance rubric，由不知道 router 身份的 reviewer 标记成功/失败；成功数/实际执行数。弃答和人工处理单列。无 executor 结果为 **UNKNOWN** |
| False weak-route rate | 弱模型决策且执行失败或未达预定 rubric 的次数/弱模型调用数。没有 executor result 就是 **UNKNOWN**，不估算 |
| Unnecessary escalation | verified gold 允许弱路线但 router 选强/人工的次数/符合弱路由的 cases；没有 verified gold 时为 **UNKNOWN** |
| Error escalation / recovery | 弱路线执行失败后在预算内升级，且重试后满足同一 acceptance rubric 的比例；统计错误升级（不该升级）、漏升级、升级后仍失败 |
| Router latency | 固定机器、并发、线程数和重复次数；分别报告 cold-start 分项、每案例原始 warm 值及 median。当前小样本不报告 p95/p99 |
| End-to-end latency | 首个执行请求至最终成功/人工终止；仅真实执行才报告，区分请求排队与 model time |
| Tokens | router 输入/输出 tokens 与 executor 各次尝试 tokens 分列；非生成式分类模型标为 N/A，不填 0 |
| Cost | 每 case 的 router+所有 executor calls 总和。规则/本地推理以机器功耗或 CPU 时间估算时另标 proxy，不等价美元成本；API 使用 0 付费调用，本轮不会发生 |
| Offline availability | 在网络禁用时 N/M case 能完成决策的个数；区分断网前预缓存与首次安装/权重下载 |
| Failure fallback | router unavailable / endpoint outage 下返回合法 fail-closed receipt 的比例及最终行为；router-only 与 task recovery 分开 |

Latency 方案：固定机器/OS、CPU 型号和线程数、Python/runtime、并发=1、输入顺序与 checkpoint revision；网络关闭且权重已预缓存，禁止把下载纳入推理耗时。分别启动 5 个全新进程测 cold-start（进程启动至模型加载完成、首次请求返回分开记）；每个 independent_test 输入预热 1 次，再逐案串行调用 5 次，用单调高精度时钟在 adapter `predict` 调用前后计时，包含 tokenization 和模型 forward，不含加载/下载，保存每个原始毫秒值。报告每案原始值与 median；小样本不报告无解释力的 p95/p99 或置信区间。Rules CLI 同法另记进程启动开销和纯 `route()` 调用时间。端到端时延只有执行器确实运行后才统计，并拆分 queue、router、executor 和人工等待。记录硬件、OS、runtime、功耗口径和计量来源到 manifest。该方案尚未实际测量 Laya 延迟。

## 6. token/cost 与正确性 accounting

- 语义模型路由输入通常是完整 prompt；另计 adapter 产生的任何 system/context tokens。Rules-only 没有 router token consumption，标 0（不是缺测）。Laya/embedding 分类用 N/A/encoder-token count，依工具能力记录，不套用生成 token。
- 真实 API 实验如后续另获授权，按每次调用 usage 返回值优先；若缺 usage，明确估算方式和误差，不将估算与实际混合。记录币种、provider、价目表来源与抓取日期、输入/输出/缓存 tokens，含 router 自身调用。
- 用同一 executor 和盲审答案评分；decision accuracy 不足以证明回答质量。人工 review 计作策略结果而非模型成功。
- adapter invalid/error 不删除样本，按预注册 policy 映射为 fallback，错误率和 fallback 另报。

## 7. 合规/失败规则/停止标准

- 当前唯一真实离线基线必须无网络可运行。模型候选没有缓存权重时不做断网首装声称；候选无法加载时保留失败日志、记录被阻塞，不擅自切其它 checkpoint。
- 执行 confidential case 只用虚构材料；敏感性由 case 标签控制，先应用 hard veto，再调用语义模型（若允许）。
- 不在 independent_test 调阈值；train/calibration/dev 与 independent_test 的 ID 和内容哈希不得重合。模型/router 的开源预训练训练数据不等于本实验 fit set，单独列明。
- 若任一候选没有合法可用权重、正确接口或在既定设备上运行，则**排除并报告**，不把失败补值为模拟结果。
- 安全不变量（confidential 不出 cloud、不可用目标不被报告可用、未知风险 fail-closed）必须全部通过。统计通过条件、主要指标、样本量依据、非劣界限、成本/时延预算及停止条件在依据和审核者签署前全部为 **PRE-REGISTRATION REQUIRED**；不得用当前小型公开合成集推断门槛。
- 未达标准、差异低于噪声、或结果不可复现：停在 Rules，不训练、不产品化。

## 8. 执行顺序与当前状态

1. Rules-only 基线和 CLI 已实现；unittest 是实现检查，不是 benchmark。
2. 本轮交付的公开合成 fixtures 全部只作 dev 和协议验证；没有独立测试集，也没有 verified gold。预算、样本量依据、非劣界限与统计验收门槛未定。
3. 候选冻结：选择具体项目 SHA / package version / HF revision / weight hash / CPU环境；逐 checkpoint 审 license。
4. Adapter contract test：只需轻量 harness；验 JSON schema、错误 fallback、离线 Rules path、安全 veto。
5. 开发集 smoke test：运行记录写入 `results/<run-id>/manifest.json` 和 JSONL receipt；不改任何冻结数据，不将开发结果报告为独立测试结果。
6. 独立审核批准后，才进行 offline model runs；真实执行任务需要额外明确授权，不能隐含授权付费 API。
7. 完成分析和 go/no-go 后停止，任何 adapter/product 实现另立任务批准。

## 9. 正式实验冻结门

正式实验开始前，run manifest 必须列出并经人工签署：

| 冻结项 | 当前状态 | 开始实验的必要记录 |
|---|---|---|
| 测试案例与数据版本 | 当前公开合成 `phase0-synthetic-v1` 已冻结为开发/协议验证用途；不能作测试集 | 新的独立测试集来源、样本清单、版本及逐文件 SHA-256；证明与 train/dev 不重叠 |
| 模型与 adapter | 尚未选择/固定实际候选 checkpoint 和 adapter | model/revision/权重 hash、tokenizer、代码 commit、配置和依赖锁文件 hash、语言覆盖及 license 审查 |
| 执行环境/硬件 | 未冻结 | OS、CPU/GPU 型号、内存、runtime、线程/并发、容器/依赖与执行器版本 |
| 预算上限与停止条件 | **PRE-REGISTRATION REQUIRED** | 经审核者批准的总调用/样本/时间上限、费用（必须为 0 或明确授权）、超预算与安全失败停止规则 |
| 主要指标和验收条件 | **PRE-REGISTRATION REQUIRED** | 预先指定主要 outcome、统计方法、成功/非劣界限、成本/时延界限和多重比较处理依据 |
| 样本量与集合边界 | **PRE-REGISTRATION REQUIRED** | 基于目标效应/方差或其他可审依据给出样本量；train/dev/independent_test 清单与访问控制 |

缺少任一冻结记录或未满足任何 PRE-REGISTRATION REQUIRED 项时，不开始正式模型/端到端实验。无需根据当前资料编造预算、统计门槛或样本量。
