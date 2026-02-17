# L1 Overview - 事故分级响应（SEV）

## When to use
- 核心业务指标异常或服务中断
- 监控告警达到SEV阈值

## Inputs
- 告警信号与影响范围
- 当前资源与应急预案

## Outputs
- SEV分级处置记录
- 事故复盘与规则写回

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
`按SOP执行：事故分级响应（SEV） <输入>`
