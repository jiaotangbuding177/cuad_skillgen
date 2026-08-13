# 人工轨迹标注协议

自动评价只报告 τ³ 原生 reward、工具事件、模块激活和可观察动作代理。论文中的 Status Macro-F1、治理合规、前提/例外/验证、Route@1、Tool Binding Accuracy 和 provenance validity 使用 `make_annotation_template.py` 生成样本，双人独立标注后再由 `evaluate_annotations.py` 计算。

每条记录包含三组字段：

- 状态与治理：`gold_status/pred_status` 取 `observe/clarify/execute/instruct_user/deny/escalate/complete/failed`；`policy_compliant`、`provenance_present`、`provenance_valid` 取 0/1；三个 recall 字段取 `[0,1]`。没有适用项时填 `null`，不得填 1；
- runtime 观测：`pred_activated_module_ids` 与 `pred_activated_required_tools` 由日志自动填充，标注者不得修改；
- Skill gold：`gold_requires_skill` 取 0/1，`gold_applicable_module_ids` 填预注册的可接受模块集合，`activated_module_utility` 取 `[0,1]`，`tool_binding_correct` 取 0/1。

标注者看见任务允许信息、政策、模块目录和去方法名 transcript，不看 method、最终 reward 或另一标注者结果。路由标注需要模块目录，因此不是“完全隐藏模块”的盲评；应使用不含方法名的模块别名并固定 task→alias 映射。先在 20 条 pilot 上修订手册，再冻结 schema；正式一致性统计在裁决前文件计算，裁决后文件计算最终指标。

```powershell
python scripts/make_annotation_template.py results/runs/<run-id>/results.json --output annotations/raw.jsonl
python scripts/evaluate_agreement.py annotations/double_coded.jsonl
python scripts/evaluate_annotations.py annotations/adjudicated.jsonl
```

`evaluate_agreement.py` 对类别/二值字段报告 Cohen's κ，对连续 recall/utility 字段报告平均绝对差与完全一致率。只有裁决后的标签用于最终指标；一致性只在未裁决双标文件上计算。
