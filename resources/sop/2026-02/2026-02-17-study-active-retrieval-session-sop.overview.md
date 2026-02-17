# L1 Overview - 学习主动检索会话

## When to use
- study session starts
- retrieval accuracy below threshold for two sessions

## Inputs
- Input 1: topic prompts and questions
- Input 2: session duration and rules

## Outputs
- Output 1: retrieval score log
- Output 2: session summary and next focus list

## Minimal procedure
1) 选择本次主题和题目集
2) 先做闭卷检索测试
3) 标注错误并定位原因
4) 进行定向复习
5) 进行二次检索测试
6) 写会话总结与下次计划

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：学习主动检索会话 <输入>`
