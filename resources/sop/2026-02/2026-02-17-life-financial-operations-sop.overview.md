# L1 Overview - 生活财务运行

## When to use
- weekly finance review window starts
- forecasted cash buffer falls below threshold

## Inputs
- Input 1: income and expense records
- Input 2: upcoming bill list

## Outputs
- Output 1: updated weekly budget status
- Output 2: exception list and next-week actions

## Minimal procedure
1) 汇总本周资金流水
2) 核对账单与到期日
3) 对比预算与实际支出
4) 检查现金缓冲阈值
5) 执行纠偏动作（削减/延后/重排）
6) 输出下周财务计划

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：生活财务运行 <输入>`
