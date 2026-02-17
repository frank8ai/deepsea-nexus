# L1 Overview - 用户反馈闭环

## When to use
- 用户反馈量持续增长或集中投诉
- 关键功能反馈闭环率低于目标

## Inputs
- 用户反馈原始数据
- 业务目标和资源约束

## Outputs
- 反馈分类优先级清单
- 验证结果与产品规则更新

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
`按SOP执行：用户反馈闭环 <输入>`
