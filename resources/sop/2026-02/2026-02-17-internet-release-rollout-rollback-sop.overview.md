# L1 Overview - 上线发布与回滚

## When to use
- 变更进入生产发布窗口
- 灰度指标触发异常阈值

## Inputs
- 发布变更清单与影响范围
- 灰度阈值与回滚脚本

## Outputs
- 发布执行记录与灰度结果
- 回滚记录与公告口径

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
`按SOP执行：上线发布与回滚 <输入>`
