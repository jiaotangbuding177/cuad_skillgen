# τ³-SkillBench 实验就绪审计

## 当前结论

数据、Skill 生成、运行时、增量调度、轨迹抽取、确定性指标、人工标注和统计比较脚本已经形成闭环；56 个 deterministic Skill package 已实际生成并通过静态审计。**尚未产生任何正式 LLM Agent benchmark 结果**，原因是尚未冻结 agent/user model 且当前环境未检测到模型 API 凭据。因此当前状态是“离线管道就绪，live 实验待模型配置”，不能把 mock、单元测试或 dry-run 当作论文结果。

## 逐项检查

| 用户要求 | 状态 | 已落实资产 | 尚需操作 |
|---|---|---|---|
| 1. 所有基线 Skill 生成脚本 | 已落实 | `generate_skills.py` 支持 11 个主方法、3 个消融、4 个领域、输入哈希跳过和 OpenAI-compatible 可选 backend；已有 56 个 package | 若正式论文采用 LLM 编译，需冻结 compiler model 后单独生成 `skills_formal/`，不能与 deterministic 版本混报 |
| 2. 所有基线 Agent 运行结果与链路记录 | Runtime 已落实，live 结果未运行 | 统一 catalog、显式激活、simulation-local state、single run、增量矩阵、checkpoint、manifest、官方 Results、activation/tool audit trace | 冻结模型/凭据后先跑 4 领域 smoke test；当前真实 `results.json` 数量为 0 |
| 3. 评估指标脚本 | 已落实 | native reward、strict success、pass 指标、cost/duration、actor ownership、Banking Recall/MRR、动作约束代理、paired bootstrap、McNemar、Route@1/Trigger 人工指标、Cohen's κ | Tool Binding Accuracy、政策合规、异常分支与 provenance validity 必须依赖预注册标注，不能由代理指标替代 |
| 4. 其他必要操作 | 离线已落实 | 固定 commit、Python 3.12 环境、数据泄漏边界、56 包审计、19 项测试、preflight、mock、文档与 dry-run | 冻结模型、费用/turn 预算和标注协议；执行 live smoke/full matrix；之后才能做失败分类和论文结果表 |

## 增量行为

- 数据：存在 manifest 时跳过；`--force` 可显式重建；
- Skill：以 compilation source hash、backend 和 model 判断是否跳过；
- Run：以 run ID 为目录，τ³ checkpoint + `auto_resume` 恢复；矩阵脚本跳过 `status=complete` 的单元；
- Evaluation：完全读取结果离线计算，不再次调用 agent；
- 统计：按相同 task × trial 配对，缺失 pair 不进入配对比较并需单独报告。

## 推荐正式执行顺序

1. 运行 `python scripts/preflight.py`；
2. 冻结 compiler、agent、user simulator 模型和费用预算；
3. 每种方法先生成/审计一个 formal Telecom Skill；
4. 对四领域各抽一条任务执行 11 个主方法 seed 42 smoke test；
5. 确认结果结构、激活日志、工具所有权与费用后，运行冻结的主矩阵；
6. 离线生成 audit/extended metrics；
7. 对 EvoSkill/GESC 与强基线进行 paired bootstrap 和 McNemar；
8. 使用 `--include-ablations` 运行三项消融；
9. 完成分层双人标注、一致性统计与裁决，再报告路由、绑定、治理、状态和 provenance 指标。
