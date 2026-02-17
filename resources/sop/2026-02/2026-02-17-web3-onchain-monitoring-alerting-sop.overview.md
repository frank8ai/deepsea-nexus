# L1 Overview - 链上数据监控与告警

## When to use
- TVL、资金流或价格偏离超过阈值
- 鲸鱼交易或可疑地址活动异常

## Inputs
- 监控指标与阈值配置
- 告警路由与升级规则

## Outputs
- 告警事件与处理记录
- 阈值调优与监控覆盖清单

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
`按SOP执行：链上数据监控与告警 <输入>`
