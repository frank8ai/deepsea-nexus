# L1 Overview - 学习间隔复习

## When to use
- review day arrives for queued items
- recall rate drops below threshold in two consecutive intervals

## Inputs
- Input 1: queued review items
- Input 2: interval rule set

## Outputs
- Output 1: updated recall scores per interval
- Output 2: next-interval schedule

## Minimal procedure
1) 刷新待复习队列
2) 按间隔规则安排当日批次
3) 执行检索复习并评分
4) 低于阈值项缩短间隔
5) 高分项延长间隔
6) 输出下一轮计划

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：学习间隔复习 <输入>`
