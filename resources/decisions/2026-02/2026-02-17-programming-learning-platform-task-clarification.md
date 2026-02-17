# Task Clarification Card

## Metadata
- Card ID: TC-20260217-01
- Date: 2026-02-17
- Owner: yizhi
- Status: completed
- SOP: 工作任务澄清与成功标准 (`SOP-20260217-03`)

## Task Objective
在 2026-06-30 前上线一个“类似数学学院风格”的编程学习平台 MVP，支持结构化课程、交互式练习和学习进度追踪，并完成首轮用户验证。

## Deadline
- Hard deadline: 2026-06-30

## Suggested Constraints (default assumptions)
- Time: 2026-02-17 到 2026-06-30（约 19 周）。
- Budget: 首版现金支出上限 USD 8,000（云资源、第三方服务、必要外包）。
- Resources:
  - 产品/开发负责人 1 人（你）
  - AI 协作开发支持（Codex）
  - 设计与内容支持按需投入（不设专职团队）
- Non-negotiables:
  - 用户数据安全与隐私合规（最小化采集、敏感信息脱敏存储）。
  - 课程内容版权可证明（原创或合法授权）。
  - 生产环境数据完整性（关键学习记录可追溯、可恢复）。

## Success Metrics (numeric thresholds)
1. 交付指标（产品可用）:
   - 2026-06-30 前上线 MVP，且核心学习链路成功率 >= 95%（注册/登录 -> 选课 -> 代码练习 -> 提交 -> 查看进度）。
2. 用户指标（首轮验证）:
   - 种子用户注册数 >= 60；
   - 其中 >= 25 人在 7 天内完成首模块（完成率 >= 41%）。
3. 学习效果与留存:
   - 首模块完成人群中，测验通过率（>=80分）>= 75%；
   - D7 留存率 >= 30%。

## Non-goals (explicitly out of scope)
- 不做 iOS/Android 原生 App（仅 Web）。
- 不做多编程语言并行首发（首版只做 1 条主路径，例如 Python）。
- 不做企业端/教务后台复杂功能（班级管理、组织权限、多租户）。
- 不做大型内容库（先做高质量最小课程单元）。

## First-pass Execution Plan (v1)
1. Phase 1 (2026-02-17 ~ 2026-03-10): 明确课程大纲与核心功能边界，冻结 MVP 范围。
2. Phase 2 (2026-03-11 ~ 2026-04-20): 完成核心功能开发与内测（课程/练习/判题/进度）。
3. Phase 3 (2026-04-21 ~ 2026-05-31): 封闭测试，优化学习链路和数据埋点。
4. Phase 4 (2026-06-01 ~ 2026-06-30): 小范围公开发布，收集指标并完成验收。

## Stop/Pivot Conditions
- 若到 2026-04-30 仍未打通“代码练习提交 + 进度记录”核心链路，则立即收缩范围为单课程、单练习类型。
- 若到 2026-06-15 种子注册 < 20 或首模块完成人数 < 8，则暂停公开发布，转为私测迭代并重设目标。

## Open Assumptions (to confirm)
- 课程首发语言暂定 Python。
- 平台语言暂定中文。
- 首发形态暂定 Web 单端。

## Decision
- Clarification result: pass (first pass)
- Next step: 已进入《工作周计划与日计划》SOP，输出 19 周里程碑与本周执行清单。
