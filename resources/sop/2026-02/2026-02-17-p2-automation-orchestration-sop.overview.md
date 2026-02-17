# L1 Overview - 自动化编排与集成

## When to use
- 同类任务重复 >= 3次/周
- 自动化异常率 > 10%

## Inputs
- Input 1: 任务流程定义
- Input 2: 运行约束和异常阈值

## Outputs
- Output 1: 自动化脚本和执行计划
- Output 2: 监控告警与回滚说明

## Minimal procedure
1) 识别可自动化重复任务
2) 设计脚本输入输出和失败分支
3) 实现最小可运行脚本
4) 接入告警与日志
5) 执行回滚演练
6) 灰度启用并追踪指标

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：自动化编排与集成 <输入>`
