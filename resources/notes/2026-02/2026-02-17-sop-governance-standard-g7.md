---
uuid: 20260217230000
type: fact
tags: [sop, governance, standard, three-optimal, quality-gates]
status: active
project: deepsea-nexus
---

# Governed SOP Standard (G7) - 治理层 + 三佳执行层

这份标准用于升级与治理 SOP 库：不是替代“三佳（最佳实践→最佳方法→最佳工具）”，而是把三佳降到执行层，在其上叠加治理层硬约束（不可互相抵消），防止“做了不该做的事”或“证据不够就上线”。

## 最高标准（不可互相抵消）
1. 非可协商约束（合规/安全/数据完整性）
2. 结果价值优先
3. 证据强度随风险升级
4. 可逆性决定速度
5. 三佳执行层（最佳实践→最佳方法→最佳工具）
6. 简洁可维护
7. 闭环写回与规则更新

## 为什么比单独三佳更好
- 三佳擅长优化“怎么做”，但不一定能防止：
  - 做了不该做的事（合规/安全/数据完整性被忽略）
  - 证据不够就上线（高风险却用低证据）
  - 不可逆操作却追求速度（没有刹车与回滚）

## 下一轮升级建议：4 项硬机制
1) 生命周期字段
- 生效条件 / 复审周期 / 退役条件

2) Kill Switch 表
- 触发阈值 -> 立即停止 -> 回滚动作

3) 双轨指标
- 结果指标（主）+ 过程指标（辅），过程指标不得替代结果指标

4) 自动降级门禁
- 月度趋势连续 2 个周期退化：active -> draft

## 落地建议（文档结构）
- Metadata: Effective when / Review cadence / Retire when / Owner + backup owner
- New section: Kill Switch table
- SLA and Metrics: Outcome KPI (primary) + Process KPI (secondary)
- Change Control or Release: Auto-demotion rule + trend data source
