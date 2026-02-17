# L1 Overview - 工作执行闭环与状态更新

## When to use
- a task is in progress and next action is not logged
- blocker remains unresolved for more than 4 hours

## Inputs
- Input 1: current task record
- Input 2: available work window

## Outputs
- Output 1: updated task status with evidence
- Output 2: blocker log and next action

## Minimal procedure
1) 选择当前最高优先任务
2) 定义30分钟下一步动作
3) 执行并记录中间结果
4) 更新状态（done/in-progress/blocked）
5) 若阻塞则触发升级或切换备用任务
6) 收盘写回指标

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：工作执行闭环与状态更新 <输入>`
