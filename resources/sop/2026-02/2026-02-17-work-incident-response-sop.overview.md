# L1 Overview - 工作异常响应与恢复

## When to use
- an incident signal is detected and severity is unknown
- severity is medium or high and impact expands

## Inputs
- Input 1: incident signal and logs
- Input 2: affected scope and users

## Outputs
- Output 1: severity classification and containment action
- Output 2: recovery summary and post-incident action list

## Minimal procedure
1) 接收事件信号并建单
2) 10分钟内完成严重度分级
3) 启动遏制动作
4) 执行恢复并验证核心链路
5) 对外/对内同步状态
6) 24小时内完成复盘与规则回写

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：工作异常响应与恢复 <输入>`
