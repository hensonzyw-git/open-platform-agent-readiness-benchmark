# AGENTS.md — Agent-Ready Benchmark

开始任何工作前，先读 [`PROJECT_STATE.md`](PROJECT_STATE.md)，再读 [`PROJECT-LOG.md`](PROJECT-LOG.md)。

## Source Of Truth

- 当前状态：`PROJECT_STATE.md`
- 详细工作记忆：`PROJECT-LOG.md`
- 评分标准：`scoring-model-design.md`（当前 v0.3）
- 长期决策：`docs/DECISIONS.md`
- 下一位 agent 接手：`docs/HANDOFF.md`

## Workflow

工作流：直接推 main，无分支无 PR（仅在被要求时提交）。

## Closeout

每次 session 收尾时：

- 更新 `PROJECT_STATE.md`。
- 如有新决策，更新 `docs/DECISIONS.md`。
- 如有里程碑，更新 `docs/PROJECT_LOG.md`。
- 如有接手信息变化，更新 `docs/HANDOFF.md`。
- 若继续保留 `PROJECT-LOG.md` 作为详细历史，也同步更新它的「当前状态」和「会话日志」。
