# τ³-SkillBench

本目录是论文的 τ³-bench 多场景 Document-to-Skill 实验工作区。上游资源冻结为 τ³-bench v1.0.1 后的 commit `668d3bcd135c02aa3438f987ef45735b7c163ee3`，覆盖 Retail、Airline、Telecom 与 Banking Knowledge。

核心文档：

- [评估方案](docs/EVALUATION_DESIGN.md)
- [Agent Runtime 设计](docs/AGENT_RUNTIME_DESIGN.md)
- [数据组织](docs/DATA_ORGANIZATION.md)
- [单次输入输出案例](docs/SINGLE_RUN_CASE.md)
- [实验就绪审计](docs/EXPERIMENT_READINESS.md)
- [人工标注协议](docs/ANNOTATION_SCHEMA.md)
- [Package-aware Runtime v1](docs/PACKAGE_AWARE_RUNTIME_V1.md)
- [A2SC / G-A2SC 算法与渐进式 Runtime 修改设计](docs/ATOM_TO_ACTION_SKILL_COMPILATION_DESIGN.md)
- [代码实现与审查报告](docs/IMPLEMENTATION_REVIEW.md)

当前状态：四领域规范化完成；11 个主方法与 3 个核心消融在 4 个领域共生成 56 个确定性 Skill package。默认 runtime 为 `hard_progressive_advisory`，统一使用模块目录、显式 `activate_skill`、最多两个模块和 τ³ 原生业务工具。19 项测试、56 包静态审计和离线 preflight 已通过。尚未配置正式 LLM，也尚未产生可用于论文结论的 live benchmark 分数。

最小复现：

```powershell
python scripts/run_pipeline.py
python scripts/run_experiment_matrix.py --agent-model <agent-model> --user-model <user-model> --num-tasks 1 --dry-run
python scripts/run_experiment_matrix.py --agent-model <agent-model> --user-model <user-model> --include-ablations --num-tasks 1 --dry-run
```

旧 τ-bench 实现没有删除，保存在 `legacy/tau-bench-original/`。
