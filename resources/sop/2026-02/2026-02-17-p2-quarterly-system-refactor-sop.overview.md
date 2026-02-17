# L1 Overview - 个人系统季度迭代

## When to use
- 进入季度重构窗口
- 关键健康指标连续2周恶化

## Inputs
- Input 1: 系统健康指标与技术债列表
- Input 2: 资源预算和发布窗口

## Outputs
- Output 1: 季度重构计划
- Output 2: 分批实施记录和验证结果

## Minimal procedure
1) 收集系统健康与债务指标
2) 确定Top重构目标
3) 拆分分批重构计划
4) 执行一批并回归验证
5) 灰度发布并观测
6) 季度复盘与下季输入

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：个人系统季度迭代 <输入>`
