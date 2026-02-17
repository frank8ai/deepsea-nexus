# L1 Overview - 家务与周期维护

## When to use
- 存在周期任务且过去30天有遗漏
- 同类维护任务连续2次延迟

## Inputs
- Input 1: 周期任务列表
- Input 2: 本周可用时间

## Outputs
- Output 1: 本周家务维护执行计划
- Output 2: 执行完成和异常记录

## Minimal procedure
1) 更新周期任务清单
2) 安排本周执行窗口
3) 按窗口执行任务
4) 记录异常和耗时
5) 处理未完成任务
6) 周末复盘并优化清单

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：家务与周期维护 <输入>`
