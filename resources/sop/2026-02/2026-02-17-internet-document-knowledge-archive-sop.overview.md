# L1 Overview - 文档与知识归档（互联网）

## When to use
- 关键决策或架构变更完成
- 同类问题重复出现 >=2 次

## Inputs
- 决策与变更上下文
- 证据链接与结果数据

## Outputs
- 结构化文档条目（ADR/决策卡）
- 版本审计与索引更新

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
`按SOP执行：文档与知识归档（互联网） <输入>`
