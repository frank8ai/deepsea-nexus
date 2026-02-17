# 一页执行卡：复盘写回（规则库/反例库）

## 何时触发
- 任务/决策完成后 24 小时内。
- 同类失败信号 30 天内出现 2 次时立即触发。

## 输入
- 来源卡片：`resources/decisions/YYYY-MM/*.md`
- 结果证据：指标、日志、差异、反馈

## 7 步执行
1. 绑定来源卡片，确认可追溯路径。
2. 写 Postmortem 卡（目标/动作/结果/指标/停止条件）。
3. 抽取 1-3 条 if/then 规则更新。
4. 有失败模式则写反例卡（检测信号+最小复现+缓解）。
5. 给规则补 `confidence` 和 `review_at`。
6. 做轻校验：链接可达、字段完整、无敏感信息。
7. 记入迭代日志并更新版本决策。

## 硬门禁
- 规则更新必须 1-3 条。
- 证据缺失时必须定义可测代理指标。
- 检测到密钥/敏感数据必须停止并脱敏。

## 输出
- 复盘卡：`resources/decisions/YYYY-MM/*.md`
- 规则库：`agent/patterns/decision-rules.md`
- 反例库：`agent/cases/anti-patterns/*.md`（如适用）
- 迭代日志：`resources/sop/2026-02/2026-02-17-postmortem-writeback-iteration-log.md`

## SLA
- 单次周期：<= 30 分钟
- 首次产出率：>= 90%
- 规则返工率：<= 10%

## 校验命令
```bash
python3 scripts/validate_sop_factory.py --sop resources/sop/2026-02/2026-02-17-postmortem-writeback-sop.md --strict
```
