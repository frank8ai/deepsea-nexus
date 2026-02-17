# L1 Overview - Web3事件响应（被盗/异常转账/预言机异常）

## When to use
- 链上异常转账或资金外流超过阈值
- 预言机价格偏离触发告警

## Inputs
- 事件告警与链上证据
- 应急角色与暂停权限清单

## Outputs
- 事件响应时间线与处置记录
- 公告、取证和复盘写回

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
`按SOP执行：Web3事件响应（被盗/异常转账/预言机异常） <输入>`
