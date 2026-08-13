# 完整实验案例 Mock

## 案例身份

- 数据来源：冻结原版 τ-bench retail dev；
- 统一任务 ID：`retail-dev-0000`；
- 方法：`graph_evoskill_compiler`；
- 性质：确定性全链路 smoke test，不调用 LLM，不计入论文结果。

## 1. 输入

### SOP 与 Skill

- 原始 SOP：`data/processed/retail/documents/policy.md`；
- Runtime rules：`data/processed/retail/documents/runtime_rules.json`；
- Tool contracts：`data/processed/retail/documents/tool_catalog.json`；
- 编译结果：`skills/graph_evoskill_compiler/retail/`。

### 用户请求

用户 Olivia Ito，邮编 80218。她因为旅行期间无法收货，希望取消订单 `#W5442520`、获得全额退款且暂时不重新下单。

### 初始环境

从上游 `users.json` 和 `orders.json`读取真实用户与订单。关键初始状态为：

```json
{
  "user_id": "olivia_ito_3591",
  "order_id": "#W5442520",
  "status": "pending"
}
```

### Gold

```json
{
  "decision_status": "execute",
  "consequential_actions": [
    {
      "name": "cancel_pending_order",
      "arguments": {
        "order_id": "#W5442520",
        "reason": "no longer needed"
      }
    }
  ]
}
```

## 2. 经过的操作

| Turn | 状态 | 操作 | 目的与政策约束 |
|---:|---|---|---|
| 1 | — | 用户提出取消请求 | 给出身份线索、订单与期望结果 |
| 2 | `clarify` | `find_user_id_by_name_zip` | 在处理任务前确认身份，引用 `POL-002/003` |
| 3 | `clarify` | `get_order_details` | 确认订单存在且状态为 pending |
| 4 | `clarify` | 请求明确确认 | 后端写操作前说明交易细节，引用 `POL-004` |
| 5 | — | 用户回答 “Yes” | 满足显式授权门控 |
| 6 | `execute` | `cancel_pending_order` | 使用Gold参数执行唯一后端写操作 |
| 7 | `completed` | 验证并回复最终状态 | 确认订单 cancelled 与退款处理信息 |

操作顺序展示了 Skill 的核心作用：不仅选择正确工具，还必须在写操作前完成身份、状态、资格、参数和授权检查。

## 3. 输出

结果文件：`results/mock/graph_evoskill_compiler/retail-dev-0000.json`。

核心最终状态：

```json
{
  "order_id": "#W5442520",
  "status": "cancelled",
  "cancel_reason": "no longer needed"
}
```

输出同时保存：

- 输入 SOP、Skill 路径和初始状态；
- Gold 动作与期望最终状态；
- 预测动作和预测最终状态；
- 每轮 trace；
- 身份、授权、单次工具调用、信息真实性和人工转交检查；
- 政策证据 ID。

## 4. Mock 评测结果的解释

当前 mock 的状态、动作、参数、政策和来源指标均为 1，是因为它按照 Gold 和显式政策构造，目的仅是验证：

1. 数据能够从真实上游任务进入统一格式；
2. Skill package 能进入相同工具执行协议；
3. 最终状态能与 Gold 状态比较；
4. 治理门控与来源能够单独计分；
5. 评测器能输出预期字段。

它不能证明 GESC 优于任何基线。正式结论必须来自相同 test task、相同模型和多 trial 的配对实验。

