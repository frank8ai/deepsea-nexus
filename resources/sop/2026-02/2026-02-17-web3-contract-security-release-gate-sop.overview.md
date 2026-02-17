# L1 Overview - 合约安全上线门禁

## When to use
- 智能合约进入主网发布前
- 权限模型或升级策略发生变更

## Inputs
- 合约版本与审计结果
- 权限配置与升级计划

## Outputs
- 安全门禁通过记录（审计/测试/权限）
- 上线决策与回滚预案

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
`按SOP执行：合约安全上线门禁 <输入>`
