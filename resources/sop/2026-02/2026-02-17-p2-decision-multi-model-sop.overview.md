# L1 Overview - 复杂决策与多模型评估

## When to use
- 决策影响级别为medium或high
- 关键信息缺口 >= 3项

## Inputs
- Input 1: 决策问题与约束
- Input 2: 候选方案与风险信息

## Outputs
- Output 1: 多模型对比结论
- Output 2: 执行建议和停止条件

## Minimal procedure
1) 定义决策目标、约束、成功阈值
2) 选择至少3个模型
3) 产出多模型对比表
4) 构建风险矩阵和停止条件
5) 做方案选择并记录理由
6) 执行后复盘并回写规则

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：复杂决策与多模型评估 <输入>`
