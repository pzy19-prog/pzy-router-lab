# Phase 0 开源技术选型与证据报告

**状态：**研究结论（2026-09-23）；没有下载模型权重、运行候选模型或调用付费 API。文中上游 README 性能数字均是项目方报告，不是本仓库验证结果。

## 结论摘要

- **保留 Rules 作为强制本地基线和安全策略层。** 它依赖标准库、可离线运行、对当前 `routing-v0` 输入与输出最兼容；但它只能按显式元数据规则路由，不能感知正文真实难度或执行结果。
- **Laya 技术上可通过隔离 adapter 接入，但效果可行性为 UNKNOWN。** 当前公开文档将其描述为 typed-decision 分类器及 checkpoint 选择器，并非 `routing-v0` target selector。adapter 可把受控状态和四个路由选项组成 `choice` 问题，再将结果映射为 target；这只是接口设计，未实现或验证。Laya 当前 README 自报其已发布基础 checkpoint 在其 typed-decision 基准上接近/低于多数类基线，较高分来自特定任务微调 checkpoint；因此不得将“能接 API”推断成对本项目零样本路由有效。不能训练/微调的本任务约束下，仅能在独立审核批准后考虑冻结 checkpoint 的 zero-shot smoke，不足以据此宣称效果。中文能力、目标任务效果、CPU 资源及延迟在本仓库均为 **UNKNOWN**。
- **RouteLLM 暂缓纳入近期实测。** 仓库未归档，但 GitHub 默认分支最新提交可见日期为 2024-08-10，且其核心目标是基于 preference data 在一对强/弱模型间作选择；部署或 `mf` 配置还可能涉及 embeddings/API 配置。先锁定模型文件及全部许可证、依赖/API 路径再决定是否复现。
- **vLLM Semantic Router 是架构级参考/条件候选，不是轻量同类库。** Apache-2.0 路由器提供 CPU 本地分类/embedding，面向完整服务数据面与配置面（Envoy、backend、Docker/Kubernetes 等）；其仓库体量与集成面超出本项目 Phase 0 轻量实验的依赖预算。
- **不建议自训模型；当前 go/no-go：** 有条件 GO，仅对可复现基线验证投入少量工程时间；对自研模型、生产化或产品差异化暂 NO-GO，等待同案例的实测效益。

## 范围、身份与维护核验

截至 2026-09-23 的上游页面读取记录。下表 SHA 是此前记录的快照，非本轮重新 pin 的实验版本；动态 main 页面不能用于复现实验。任何实验前必须核对并固定当时的 release/commit、依赖、权重 revision 和文件哈希。

| 项目 | 官方仓库/本次参考快照 | 当前可见维护情况 | 判断 |
|---|---|---|---|
| Rules | 本仓库 `router_lab/rules.py`，HEAD `c4d9fa4` | 本仓库基线 | 可重复、离线；不具语义/执行能力 |
| Laya | [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya)，`3b000c87daf237729aa66614c9f79b6609ee27e3` | 上游主仓库当日仍有提交；Apache-2.0 | 确认可运行路径后再纳入实验 |
| RouteLLM | [lm-sys/RouteLLM](https://github.com/lm-sys/RouteLLM)，`0b64fdafe049e596a3f5657c219329f24af24198` | 非 archived，但本次 GitHub 默认分支最新提交日期 2024-08-10 | 维护活跃度风险；不可把“未归档”说成仍活跃 |
| vLLM Semantic Router | [vllm-project/semantic-router](https://github.com/vllm-project/semantic-router)，`e5bc8c98323189e1e474620a0a35dab0fadce7a7` | 2026-09-23 有提交，Apache-2.0 | 活跃且能力广，但不是轻量依赖 |

**Laya 名称注意：**检索到 `Billie-HE2/laya_robotics`、`he-jev/laya` 等 fork/派生条目。此报告将 Convai Innovations 的 Python 包 `laya` 与其官方模型卡仓库作为候选；不把同名 fork 的实验和权重归属混为一谈。上游包元数据列 `Convai Innovations` 为作者、Apache-2.0；具体使用时仍需将代码 commit 和 Hugging Face checkpoint revision 一起 pin。

## 候选能力与适配差异

| 维度 | 本地 Rules | Laya | RouteLLM | vLLM Semantic Router（补充候选） |
|---|---|---|---|---|
| 核心任务 | 显式风险、复杂度、隐私与可用目标规则 | 对给定 state 回答 `choice` / `score` / `noul` 等 typed questions；其 `Router` 选 Laya 自家 checkpoint（语言/任务），不等同于选下游模型 | 已训练 router 对 prompt 估计强模型 win-rate，在指定强/弱模型对间按 threshold 二选一；支持 `mf`、`sw_ranking`、`bert`、`causal_llm`、`random` | 策略化模型/模型池选择，信号包括语义、任务/领域、能力、偏好、成本/时延、可用性等；可编排有限多模型路径 |
| 代码许可证 | 本仓库 MIT | Apache-2.0（代码） | Apache-2.0（代码） | Apache-2.0（代码） |
| 模型/权重许可证 | 无 | Hugging Face `convaiinnovations/laya` 与 `laya-multilingual` 显示 Apache-2.0；实验时逐个核实具体 checkpoint 的 revision/card | RouteLLM HF 权重 repo 的许可证须按每个 checkpoint 核实；不能由代码 LICENSE 推定。**尚未完成逐个 checkpoint 的许可确认** | Vela/其他模型权重是单独资产；每个配置选用模型的 model card/license 必须单独审核。代码 Apache-2.0 不覆盖权重 |
| 模型规模 / 资源 | 无模型；标准库 | 英文 ModernBERT-large 421M / 512 tokens；多语 mmBERT-base 322M / 1024 tokens；typed-decisions 421M / 1024 tokens。fp32 仅按参数量估算权重约 1.68/1.29 GB，未计运行时开销；不是实测内存 | `mf` 路由器权重在 HF 展示约 833 kB；其它 `bert`/`causal_llm` 路由器及 embeddings 资源/启动占用本次未做完整核验。推理代码依赖 PyTorch、Transformers、scikit-learn 等；不能据小 router 文件大小推导完整运行资源 | Router 可在 CPU；本地模型选择器和 Vela 有额外权重/runtime。官方 CPU 示例使用 Vela Domain 307M，CPU Candle/ONNX；完整部署还需 router 容器/Envoy 与可达的生成 backend |
| CPU / 完全离线 | 是；零模型调用 | 上游支持 device CPU 的 PyTorch 路径；权重缓存后可离线，但首次拉取需网络。**纯 CPU 性能未在本地验证** | Router 可在本机 CPU 的候选实现可能性高，但所有配置、嵌入生成、model-pair endpoint 需拆开验证；README 明示 `mf`/`sw_ranking` 当前需要 `OPENAI_API_KEY` 生成 embeddings，故默认 quickstart 并非断网闭环。Ollama local models 示例不证明 router 本身离线 | Router-side CPU 分类支持；模型准备后本地 inference 可离线，但数据面转发到的生成 backend 必须在本地才能端到端离线；安装/取权重有联网环节 |
| 路由/回退类型 | 静态 local-small → local-strong；显式 cloud opt-in；高风险、未知复杂度、无目标时 manual review | 语言/checkpoint routing + 任意用户定义 typed decision 的概率/阈值；不自带任务执行后的失败感知/升级保证 | pairwise strong-vs-weak quality/cost tradeoff；基本粒度是 prompt，非执行器失败后的 task/session recovery | 单请求模型选择、合规条件、拒绝/升级和有界 multi-model 路径；需配置 backend、recipe、signals 与执行拓扑 |
| 训练/微调 | 无；手写固定规则 | 项目提供预训练 checkpoint；研究方法包含训练/校准，但本轮不做训练。是否开放训练脚本、适用数据与重训成本须独立评估 | 提供训练/评估流程，router 由 preference data 训练；本轮不训练 | 文档提供 selector 训练流程（KNN/KMeans/SVM/MLP artifacts），与纯配置 routing 区分；不在本轮尝试 |
| 中文任务 | 接收复杂度等中性枚举；不理解中文内容 | multilingual checkpoint 声称 100+ languages；Chinese 实测：**UNKNOWN** | README 的 Arena preference 路由没证明中文泛化；Chinese 实测：**UNKNOWN** | 多语模型/模型池可配置但中文效果依赖具体本地模型和信号标签；统一样本实测：**UNKNOWN** |
| `routing-v0` 接入复杂度 | 原生字段与规则输出；最低 | 中：写隔离 adapter，把允许的非机密文本/标注问题映射成决策，再转回 `selected_target`、原因码；必须保留 Rules 安全 veto，不能让模型覆盖 confidentiality/risk | 高：改造 pairwise prompt scorer + calibrate threshold + embedding/backend 配置；目前主要 OpenAI-compatible 客户端/服务契约，与 metadata-only contract 不同 | 很高：部署成独立 gateway/service，配置映射到 YAML recipe，适配 request/response wire contract；不能直接 import 成当前函数替代品 |
| 主要实际痛点/证据边界 | 无语义、不能观察运行中失败、目标列表能力有限；这是本仓库结构事实 | 将概率/质量/复杂度等作出前置分类，不等同于从本项目真实失败历史学习；语言模型 checkpoint 装载体积与切换冷启动是本地资源痛点，具体需要实测 | 发布/依赖/API 与 Embedding 外部依赖、模型对特定偏好数据校准与时间老化、无本合同安全/执行生命周期；维护滞后风险由默认分支时间支持 | 将广泛的生产 routing/caching/replay/learning 作为平台引入，会造成实现与运维复杂度；其中部分功能（学习、replay）上游已涵盖，不能声称它未解决 |

### Laya 适配可行性与未验证项

**接口层可行，决策质量 UNKNOWN。** 后续 adapter 可将 fixture `task_input` 与允许的非敏感 metadata 作为 Laya state，定义 `choice` 问题输出 `local_small`、`local_strong`、`cloud_strong`、`manual_review` 四类，再将选择映射到统一 receipt。这个映射问题本身未证明 Laya 的训练标签或行为符合 Router Lab 路由定义；不要将被选中的 Laya checkpoint 名称误当成下游执行 target。adapter 输出、hard-policy guard 和 receipt 扩展字段均为**设计字段/设计步骤**，并未实现。

安全层必须先于模型：high-risk、confidential/cloud 禁止、cloud 未 opt-in、目标 unavailable 和 metadata unknown 由本地 guard 判定或 veto；confidential 原文不得进入任何网络 API。模型不能放宽这些约束。当前可行性拆分：Python adapter 形态 **可设计**；当前 contract 映射 **未验证**；中文路由质量 **UNKNOWN**；本项目路由准确率与执行成功 **UNKNOWN**；权重许可以上游 checkpoint 具体 revision 重新核验；CPU 加载、内存、离线执行及延迟 **UNKNOWN**。未执行安装、下载权重或运行模型。

**Laya latency 测量方案（尚未执行）：**锁定 Python/torch/transformers 版本、checkpoint revision 与文件 SHA，先人工预缓存权重，再断网运行；固定 CPU 型号、核心/线程数、OS、并发 1。每种语言/checkpoint 单独启动 5 个新进程，分开记录进程启动、权重加载完成、首个 adapter request 返回时间；之后每个 fixture 预热 1 次，串行运行 5 次，以 `time.perf_counter_ns()` 包围 adapter 的 `predict` 调用（包括 tokenize + forward，排除加载和下载），保存全部原始毫秒值并报告每案例 median。Rules 同机测 `route()` 调用及 CLI 冷启动。小样本不报 p95/p99，不与上游 T4 数字直接比较。所有实际耗时、设备和软件版本未测前均为 **UNKNOWN**。

**不可比较的宣传数据：**Laya README 中的 “33ms/T4”、“up to”等数字属项目方特定 benchmark 条件；RouteLLM README 中“最多 85% 成本下降、维持 95% GPT-4 表现”是其基准宣称；vLLM Semantic Router 的能力描述/用例也不代表本仓库数据。它们未使用同一任务集、机器、模型端点或 accounting，本报告不将其视为本地效果证据。

## 公开来源记录

本节链接为一手来源，访问日期 2026-09-23。`main` URL 是动态文档；实验复现请使用上表 SHA 固定的 GitHub commit permalink，并将权重 revision/hash 一并保存。

- 本轮对 [Laya 当前官方 README](https://github.com/NandhaKishorM/laya/blob/main/README.md) 与 [Router implementation](https://github.com/NandhaKishorM/laya/blob/main/laya/router.py) 的只读核对：上游称其 typed-decisions checkpoint 面向四类特定 workflow；其 README 报告发布 base checkpoints 在自有 typed-decisions benchmark 上低于多数类基线，且更高分来自 fine-tuned checkpoint。README 中的 T4 latency 是上游条件，不是本仓库数据。动态 `main` 内容会变化，故未来复现实验仍须 pin commit 和权重 revision。
- [Laya 官方 GitHub README](https://github.com/NandhaKishorM/laya/tree/3b000c87daf237729aa66614c9f79b6609ee27e3)、[LICENSE](https://github.com/NandhaKishorM/laya/blob/3b000c87daf237729aa66614c9f79b6609ee27e3/LICENSE)、[pyproject.toml](https://github.com/NandhaKishorM/laya/blob/3b000c87daf237729aa66614c9f79b6609ee27e3/pyproject.toml)、[Router implementation](https://github.com/NandhaKishorM/laya/blob/3b000c87daf237729aa66614c9f79b6609ee27e3/laya/router.py)。模型卡：[English](https://huggingface.co/convaiinnovations/laya)、[multilingual](https://huggingface.co/convaiinnovations/laya-multilingual)、[typed-decisions](https://huggingface.co/convaiinnovations/laya-typed-decisions)。
- [RouteLLM 官方 GitHub README](https://github.com/lm-sys/RouteLLM/tree/0b64fdafe049e596a3f5657c219329f24af24198)、[LICENSE](https://github.com/lm-sys/RouteLLM/blob/0b64fdafe049e596a3f5657c219329f24af24198/LICENSE)、[pyproject.toml](https://github.com/lm-sys/RouteLLM/blob/0b64fdafe049e596a3f5657c219329f24af24198/pyproject.toml)、[config.example.yaml](https://github.com/lm-sys/RouteLLM/blob/0b64fdafe049e596a3f5657c219329f24af24198/config.example.yaml)、[RouteLLM HF organization](https://huggingface.co/routellm)。README describes model pair, embedding/API caveat, threshold calibration, task benchmarks and router designs.
- [vLLM Semantic Router README](https://github.com/vllm-project/semantic-router/tree/e5bc8c98323189e1e474620a0a35dab0fadce7a7)、[LICENSE](https://github.com/vllm-project/semantic-router/blob/e5bc8c98323189e1e474620a0a35dab0fadce7a7/LICENSE)、[CPU and in-process model docs](https://vllm-sr.ai/docs/installation/runtime/in-process/)、[architecture](https://vllm-sr.ai/docs/overview/semantic-router-overview/)、[ML selector training](https://vllm-sr.ai/docs/training/ml-model-selection/)、[Router Learning](https://vllm-sr.ai/docs/tutorials/learning/overview/)。
- [Issue #1 latest content](https://github.com/pzy19-prog/pzy-router-lab/issues/1) was reread on 2026-09-23. Repository baseline tests: 12/12 pass before changes.

## Jev EXP-0001：历史实验复用

当前 Router Lab checkout 的 tracked/untracked 文件、git 可见历史及本报告/协议中均没有 Jev EXP-0001 的原始数据附件。缺少可访问的 run manifest、案例 ID、时间戳、模型/checkpoint ID、逐次调用结果、费用/token 记录及 latency 原始值，因此该实验不可复核、不可纳入基准。本次没有访问到可供验证的独立原始材料；不据此推断其他位置是否存在数据，也不重新运行该付费实验。

| 字段 | 结果 |
|---|---|
| 实际测试结果 / 案例集合 | UNKNOWN（本仓库 checkout 与可见历史未包含原始材料；缺少可访问附件） |
| 决策准确率 / 执行任务成功率 | UNKNOWN |
| 延迟（router 与端到端） | UNKNOWN |
| 成本及 token 消耗 | UNKNOWN |
| 失效案例 | UNKNOWN |
| 是否能并入统一 benchmark | 否；当前没有可比证据。不得重跑付费实验来填补 |

若后续由数据所有者提供只读原始记录，只纳入同时给出 exact case IDs/版本、真实 router/model revision、运行时间、候选可用性和 cost/token 计量定义的结果。不可推断 Jev 就是 Laya，也不改变他仓库里的任何资料。

## 差异化机会（候选不超过三个）

1. **执行结果驱动的失败感知与升级（优先观察，不是当前实现目标）。** 当前合同只输出 decision 且 `execution_performed=false`，Rules 不知道下游是否失败；Laya 与 RouteLLM 文档侧重点也是前置决策/选择，未提供对 PZY 执行轨迹的原生闭环。记录安全可公开的 execution outcome、attempt index 和升级成本之后，才能判断是否比简单重试/人工处理有增量价值。
2. **本地优先且有硬性策略边界的强弱动态升级。** 当前 Rules 已保证 confidentiality fail-closed 和 cloud opt-in，但不按可观测执行失败升级。Laya / RouteLLM 可研究为可选决策信号；不可代替本地确定性 safety veto。潜在价值是弱模型先试、执行失败时升级，同时预算/重试次数有硬上限。
3. **跨任务的审计型经验记录与多模型成本控制。** RouteLLM以历史 preference data 做强弱二选一；vLLM Semantic Router 已有 Router Learning 与 Replay 机制，故“别人没有历史学习”不是机会。可差异化的问题仅在于更小、离线优先、对路由收据/原因码和真实任务失败成本作一致审计，但需证明上游工具不适用后再做。

以上是待证伪的问题，不是证明产品差异化成立。vLLM 已覆盖 learning/replay 类功能，禁止把它写成行业空白。

## 下一阶段最小实验建议

- 仅在独立审核与预算批准后，评估 **Rules vs 一个已 pin 的 Laya CPU checkpoint** 是否值得 smoke test；代码可适配不构成采用理由，且不得训练/微调。RouteLLM 暂留文献对照，待离线 embedding / model licenses / current-maintenance gate 通过再决定。
- 使用 `docs/benchmark-plan.md` 的合成 prompt fixtures 和 rubric；只有 provisional hypotheses 时不报 decision accuracy。latency 按该协议固定输入、设备与重复次数，保留 raw samples；离线测试关闭网络并预缓存模型，只能验证缓存后的断网行为。
- 端到端任务成功率、升级率/失败恢复必须有实际 executor 与明确授权；若只有 fake/stub executor，结果一律标为 **模拟测试**，仅验证 orchestration/fallback，不作为模型效果。
- 先决定真实执行 outcome 的独立标注规则与盲审流程，再新建并注册独立测试集；当前公开合成数据只属 dev，禁止移作 held-out。
- 若 Rules 已满足隐私/风险 gate 且决策结果与 Laya 无可重复的 outcome/成本收益，则维持 Rules，不接入 Laya、RouteLLM 或自训模型。
