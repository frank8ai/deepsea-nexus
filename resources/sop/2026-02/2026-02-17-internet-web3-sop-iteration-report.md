# Internet + Web3 SOP 三优迭代报告

- Date: 2026-02-17
- Scope: 20 SOP
- External evidence pack: `resources/sop/2026-02/2026-02-17-internet-web3-sop-toolchain-research-pack.md`

| SOP | 领域 | 优先级 | 最佳实践 | 最佳方法 | 最佳工具 | 研究记录 |
|---|---|---|---|---|---|---|
| resources/sop/2026-02/2026-02-17-internet-requirements-review-acceptance-sop.md | 互联网通用 | P0 | 需求评审必须绑定验收用例与不可协商约束。 | 三段评审（需求澄清 -> 约束核对 -> 验收走查）。 | PRD模板 + 验收用例模板 + 评审看板。 | resources/sop/2026-02/research-toolchain/internet-requirements-review-acceptance-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-internet-release-rollout-rollback-sop.md | 互联网通用 | P0 | 发布必须灰度、监控、回滚三件套同时具备。 | 发布前门禁 + 分阶段灰度 + 触发阈值即回滚。 | CI/CD流水线 + 灰度控制 + 统一状态页公告。 | resources/sop/2026-02/research-toolchain/internet-release-rollout-rollback-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-internet-incident-sev-response-sop.md | 互联网通用 | P0 | 事故响应先止损再优化，沟通与技术动作并行。 | SEV分级 -> Kill Switch -> 节奏化通报 -> 恢复验证。 | 告警平台 + 事故战情室 + 复盘模板。 | resources/sop/2026-02/research-toolchain/internet-incident-sev-response-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-internet-metrics-experiment-review-sop.md | 互联网通用 | P0 | 实验评审必须明确主指标、护栏指标和停止条件。 | 假设 -> 干预 -> 指标 -> 幅度 -> 停止条件五段法。 | 实验模板 + 指标看板 + 统计检查脚本。 | resources/sop/2026-02/research-toolchain/internet-metrics-experiment-review-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-internet-user-feedback-loop-sop.md | 互联网通用 | P1 | 反馈闭环必须从“收集”走到“验证”，不能停在记录。 | 反馈分桶 -> 价值/成本评分 -> 小步验证 -> 回写规则。 | 反馈工单系统 + 标签体系 + 复盘看板。 | resources/sop/2026-02/research-toolchain/internet-user-feedback-loop-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-internet-project-risk-board-sop.md | 互联网通用 | P1 | 项目看板必须同步风险热度和阻塞责任人。 | 周节奏更新 -> 风险分级 -> 升级处置 -> 复盘写回。 | 项目看板 + 风险矩阵 + 升级日志模板。 | resources/sop/2026-02/research-toolchain/internet-project-risk-board-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-internet-document-knowledge-archive-sop.md | 互联网通用 | P1 | 关键决策必须沉淀为可检索文档并绑定证据。 | 模板化记录 + 标签索引 + 月度审计。 | ADR模板 + 索引脚本 + 路径校验器。 | resources/sop/2026-02/research-toolchain/internet-document-knowledge-archive-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-internet-hiring-probation-evaluation-sop.md | 互联网通用 | P1 | 面试必须结构化评分，试用期必须目标化评估。 | 岗位画像 -> 结构化面试 -> 试用期里程碑评估。 | 评分卡模板 + 题库管理 + 试用期目标看板。 | resources/sop/2026-02/research-toolchain/internet-hiring-probation-evaluation-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-internet-vendor-outsourcing-management-sop.md | 互联网通用 | P1 | 供应商治理必须同时覆盖交付质量和权限安全。 | 准入尽调 -> SLA签署 -> 周期验收 -> 权限审计。 | 供应商评分卡 + SLA看板 + 权限审计清单。 | resources/sop/2026-02/research-toolchain/internet-vendor-outsourcing-management-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-internet-cost-budget-optimization-sop.md | 互联网通用 | P1 | 成本优化必须以结果价值为前提，避免“省钱伤业务”。 | 成本拆分 -> 价值评估 -> 优先级执行 -> ROI复盘。 | 成本看板 + 标签分摊 + FinOps评审模板。 | resources/sop/2026-02/research-toolchain/internet-cost-budget-optimization-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-web3-contract-security-release-gate-sop.md | Web3特有 | P0 | 合约上线必须满足审计、权限、暂停与升级四重门禁。 | 预发布清单 -> 安全测试 -> 权限演练 -> 上线审批。 | Slither/Echidna + OpenZeppelin库 + 多签审批面板。 | resources/sop/2026-02/research-toolchain/web3-contract-security-release-gate-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-web3-security-incident-response-sop.md | Web3特有 | P0 | 安全事件响应必须先控制资金风险，再发布证据化沟通。 | 检测 -> 暂停/限流 -> 公告 -> 取证 -> 恢复 -> 复盘。 | 链上监控 + 多签紧急操作 + 事件公告模板。 | resources/sop/2026-02/research-toolchain/web3-security-incident-response-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-web3-wallet-key-management-sop.md | Web3特有 | P0 | 私钥管理必须去单点化并可演练恢复。 | 权限分层 -> 多签审批 -> 周期轮换 -> 应急演练。 | Safe多签 + HSM/硬件钱包 + 密钥审计台账。 | resources/sop/2026-02/research-toolchain/web3-wallet-key-management-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-web3-onchain-monitoring-alerting-sop.md | Web3特有 | P0 | 监控阈值必须可量化并绑定响应动作。 | 指标分层 -> 阈值设置 -> 告警分级 -> 周期调优。 | 链上索引平台 + 告警编排 + 值班SOP。 | resources/sop/2026-02/research-toolchain/web3-onchain-monitoring-alerting-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-web3-tokenomics-incentive-adjustment-sop.md | Web3特有 | P1 | 激励参数调整必须先做风险门禁再执行。 | 假设建模 -> 小范围试行 -> 效果评估 -> 参数落地。 | 参数评审表 + 预算看板 + 女巫检测规则集。 | resources/sop/2026-02/research-toolchain/web3-tokenomics-incentive-adjustment-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-web3-exchange-partner-due-diligence-sop.md | Web3特有 | P1 | 合作准入必须通过分层尽调与风险评级。 | 清单尽调 -> 风险分级 -> 缓解条件 -> 准入决策。 | 尽调问卷 + 风险评分卡 + 合作方档案库。 | resources/sop/2026-02/research-toolchain/web3-exchange-partner-due-diligence-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-web3-governance-proposal-process-sop.md | Web3特有 | P0 | 治理提案必须包含执行路径和回滚方案。 | 论坛讨论 -> 草案定稿 -> 投票 -> 执行 -> 复盘。 | 论坛模板 + Snapshot/链上投票 + 执行清单。 | resources/sop/2026-02/research-toolchain/web3-governance-proposal-process-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-web3-airdrop-anti-sybil-sop.md | Web3特有 | P1 | 空投执行前必须完成反女巫检测并保留申诉通道。 | 规则检测 -> 风险分层 -> 冻结复核 -> 申诉复审。 | 女巫检测规则引擎 + 地址标签库 + 申诉工单系统。 | resources/sop/2026-02/research-toolchain/web3-airdrop-anti-sybil-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-web3-legal-compliance-review-sop.md | Web3特有 | P1 | 跨地区Web3业务必须先完成合规门禁再上线。 | 地区映射 -> 规则判定 -> 合规审批 -> 发布复核。 | 合规清单 + 规则引擎 + 审查台账。 | resources/sop/2026-02/research-toolchain/web3-legal-compliance-review-toolchain-research.md |
| resources/sop/2026-02/2026-02-17-web3-pr-crisis-communication-sop.md | Web3特有 | P0 | 危机沟通必须事实先行、节奏可控、口径统一。 | 事实确认 -> 首次公告 -> 周期更新 -> 复盘澄清。 | 公告模板 + 状态页 + 问答口径库。 | resources/sop/2026-02/research-toolchain/web3-pr-crisis-communication-toolchain-research.md |

## Acceptance
- Strict validation command:
  - `python3 scripts/validate_sop_factory.py --sop <file> --strict`
