# 互联网 + Web3 常用SOP目录（20）

## 分类方法
- Step 1: 先分类（互联网通用 / Web3特有）
- Step 2: 再列高频任务（高风险+高频优先）
- Step 3: 给可执行SOP名称与触发条件

## 互联网通用（10）
- [P0] 需求评审与验收标准
  - Trigger: PRD进入评审且涉及跨团队交付 | 验收标准或不可协商约束缺失
  - File: resources/sop/2026-02/2026-02-17-internet-requirements-review-acceptance-sop.md
- [P0] 上线发布与回滚
  - Trigger: 变更进入生产发布窗口 | 灰度指标触发异常阈值
  - File: resources/sop/2026-02/2026-02-17-internet-release-rollout-rollback-sop.md
- [P0] 事故分级响应（SEV）
  - Trigger: 核心业务指标异常或服务中断 | 监控告警达到SEV阈值
  - File: resources/sop/2026-02/2026-02-17-internet-incident-sev-response-sop.md
- [P0] 指标体系与实验评审
  - Trigger: 新策略或功能需要实验验证 | 核心指标波动但归因不明确
  - File: resources/sop/2026-02/2026-02-17-internet-metrics-experiment-review-sop.md
- [P1] 用户反馈闭环
  - Trigger: 用户反馈量持续增长或集中投诉 | 关键功能反馈闭环率低于目标
  - File: resources/sop/2026-02/2026-02-17-internet-user-feedback-loop-sop.md
- [P1] 项目推进与风险看板
  - Trigger: 项目进入里程碑阶段 | 依赖阻塞或资源冲突出现
  - File: resources/sop/2026-02/2026-02-17-internet-project-risk-board-sop.md
- [P1] 文档与知识归档（互联网）
  - Trigger: 关键决策或架构变更完成 | 同类问题重复出现 >=2 次
  - File: resources/sop/2026-02/2026-02-17-internet-document-knowledge-archive-sop.md
- [P1] 招聘面试与试用期评估
  - Trigger: 岗位进入招聘阶段 | 新成员进入试用期评估窗口
  - File: resources/sop/2026-02/2026-02-17-internet-hiring-probation-evaluation-sop.md
- [P1] 供应商与外包管理
  - Trigger: 新增供应商或外包合作 | SLA违约或交付质量波动
  - File: resources/sop/2026-02/2026-02-17-internet-vendor-outsourcing-management-sop.md
- [P1] 成本优化与预算控制
  - Trigger: 云成本或工具订阅超过预算阈值 | ROI复盘显示持续低效投入
  - File: resources/sop/2026-02/2026-02-17-internet-cost-budget-optimization-sop.md

## Web3特有（10）
- [P0] 合约安全上线门禁
  - Trigger: 智能合约进入主网发布前 | 权限模型或升级策略发生变更
  - File: resources/sop/2026-02/2026-02-17-web3-contract-security-release-gate-sop.md
- [P0] Web3事件响应（被盗/异常转账/预言机异常）
  - Trigger: 链上异常转账或资金外流超过阈值 | 预言机价格偏离触发告警
  - File: resources/sop/2026-02/2026-02-17-web3-security-incident-response-sop.md
- [P0] 钱包与密钥管理
  - Trigger: 新增资金地址或权限角色 | 密钥轮换周期到期或异常访问
  - File: resources/sop/2026-02/2026-02-17-web3-wallet-key-management-sop.md
- [P0] 链上数据监控与告警
  - Trigger: TVL、资金流或价格偏离超过阈值 | 鲸鱼交易或可疑地址活动异常
  - File: resources/sop/2026-02/2026-02-17-web3-onchain-monitoring-alerting-sop.md
- [P1] 代币经济与激励调整
  - Trigger: 关键激励参数需调整 | 激励效果偏离目标或被滥用
  - File: resources/sop/2026-02/2026-02-17-web3-tokenomics-incentive-adjustment-sop.md
- [P1] 上所与合作方尽调
  - Trigger: 新增交易所/做市商/审计合作 | 合作方风险评级上升
  - File: resources/sop/2026-02/2026-02-17-web3-exchange-partner-due-diligence-sop.md
- [P0] 社区治理与提案流程
  - Trigger: 关键参数或策略需要社区决策 | 治理提案进入草案阶段
  - File: resources/sop/2026-02/2026-02-17-web3-governance-proposal-process-sop.md
- [P1] 空投与活动反作弊
  - Trigger: 空投或活动名单准备发布 | 检测到批量异常地址行为
  - File: resources/sop/2026-02/2026-02-17-web3-airdrop-anti-sybil-sop.md
- [P1] 法务合规审查（Web3）
  - Trigger: 新产品或活动涉及跨地区用户 | 监管政策变更或合规风险预警
  - File: resources/sop/2026-02/2026-02-17-web3-legal-compliance-review-sop.md
- [P0] PR危机沟通（Web3）
  - Trigger: FUD/谣言快速扩散或价格异常波动 | 安全事件或系统故障引发舆情风险
  - File: resources/sop/2026-02/2026-02-17-web3-pr-crisis-communication-sop.md
