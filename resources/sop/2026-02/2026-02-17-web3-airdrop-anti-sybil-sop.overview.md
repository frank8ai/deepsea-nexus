# L1 Overview - 空投与活动反作弊

## When to use
- 空投或活动名单准备发布
- 检测到批量异常地址行为

## Inputs
- 候选地址名单与行为特征
- 活动规则与预算约束

## Outputs
- 反女巫检测结果和冻结名单
- 申诉处理与规则更新记录

## Minimal procedure
1) 定义目标、主结果指标与不可协商约束
2) 准备输入与角色责任
3) 执行核心流程并过门禁
4) 记录双轨指标并检查阈值
5) 触发异常分支时执行Kill Switch与回滚
6) 复盘写回1-3条规则

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：空投与活动反作弊 <输入>`
