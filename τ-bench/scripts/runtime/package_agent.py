from __future__ import annotations

from pydantic import Field

from tau2.agent.llm_agent import LLMAgent, LLMAgentState
import json

from tau2.data_model.message import MultiToolMessage, SystemMessage, ToolMessage
from tau2.environment.tool import as_tool
from tau2.utils.llm_utils import generate

from runtime.package_runtime import ProgressiveSkillPackage, SkillPackage, build_query


PACKAGE_CONTEXT_INSTRUCTION = """# Retrieved package context

The following items were deterministically retrieved from the selected Skill package.
Use them as task-relevant policy, tool, and workflow evidence. Original source-grounded
policy rules take precedence over workflow frequency. A workflow is a reusable hint, not
the unique correct trajectory. Never expose internal item IDs unless an audit explicitly asks.

{context}
"""


class PackageAwareAgent(LLMAgent):
    """τ³ LLMAgent with deterministic per-turn package retrieval."""

    def __init__(
        self,
        tools,
        fixed_adapter: str,
        retrieval_adapter: str,
        package: SkillPackage,
        llm: str,
        llm_args: dict | None = None,
    ):
        self.package = package
        self.base_policy = fixed_adapter + retrieval_adapter + "\n\n" + package.skill
        super().__init__(tools=tools, domain_policy=self.base_policy, llm=llm, llm_args=llm_args)

    def generate_next_message(self, message, state):
        query = build_query(message, state.messages, self.package.config.history_messages)
        retrieval = self.package.retrieve(query)
        dynamic = PACKAGE_CONTEXT_INSTRUCTION.format(
            context=retrieval["context"] or "No package item matched the current dialogue."
        )
        self.domain_policy = self.base_policy + "\n\n" + dynamic
        state.system_messages = [SystemMessage(role="system", content=self.system_prompt)]
        assistant_message, new_state = super().generate_next_message(message, state)
        raw_data = dict(assistant_message.raw_data or {})
        raw_data["skillgen_package_retrieval"] = {
            "query": retrieval["query"], "items": retrieval["items"],
            "context_chars": retrieval["context_chars"],
            "budget_chars": retrieval["budget_chars"],
            "package_hash": self.package.package_hash,
        }
        assistant_message.raw_data = raw_data
        return assistant_message, new_state


PROGRESSIVE_INSTRUCTION = """# Progressive Skill runtime

The catalog lists the only Skill modules available for this package. When a module clearly
matches the task, call `activate_skill` with its exact id before using its procedure. The runtime
will return the complete module. Skill activation is context loading, not a business action.
Use at most two modules. Never call an unlisted module and never expose internal atom IDs.

{catalog}
"""


ACTIVE_MODULES = """# Activated Skill modules

The following modules were explicitly activated. Follow applicable preconditions, actor ownership,
prohibitions, soft ordering hints, exception paths, and verification requirements. Source-grounded
policy constraints override training-derived soft ordering hints.

{modules}
"""


class ProgressiveSkillAgentState(LLMAgentState):
    """Per-simulation state required for replay-safe Skill activation."""

    active_modules: dict[str, dict] = Field(default_factory=dict)
    activation_events: list[dict] = Field(default_factory=list)


class ProgressiveSkillAgent(LLMAgent[ProgressiveSkillAgentState]):
    """OpenClaw-style catalog disclosure with runtime-enforced module loading."""

    def __init__(
        self,
        tools,
        fixed_adapter: str,
        retrieval_adapter: str,
        package: ProgressiveSkillPackage,
        llm: str,
        llm_args: dict | None = None,
    ):
        self.progressive_package = package
        self.fixed_adapter = fixed_adapter + retrieval_adapter

        def activate_skill(module_id: str) -> str:
            """Load one available Skill module into the agent context.

            Args:
                module_id: Exact module id from available_skill_modules.

            Returns:
                A runtime acknowledgement; the complete module is added to system context.
            """
            return module_id

        model_tools = list(tools)
        if package.modules:
            model_tools.append(as_tool(activate_skill))
        super().__init__(
            tools=model_tools,
            domain_policy=self._build_policy({}),
            llm=llm,
            llm_args=llm_args,
        )

    def _build_policy(self, active_modules: dict[str, dict]) -> str:
        sections = [
            self.fixed_adapter,
            PROGRESSIVE_INSTRUCTION.format(catalog=self.progressive_package.catalog()),
        ]
        if active_modules:
            rendered = []
            for module_id, activation in active_modules.items():
                rendered.append(f"## {module_id}\n\n{activation['instructions']}")
            sections.append(ACTIVE_MODULES.format(modules="\n\n".join(rendered)))
        return "\n\n".join(sections)

    def get_init_state(self, message_history=None):
        self.domain_policy = self._build_policy({})
        base_state = super().get_init_state(message_history)
        return ProgressiveSkillAgentState(
            system_messages=base_state.system_messages,
            messages=base_state.messages,
        )

    @staticmethod
    def _add_usage(target: dict | None, extra: dict | None) -> dict | None:
        if not target and not extra:
            return None
        merged = dict(target or {})
        for key, value in (extra or {}).items():
            if isinstance(value, (int, float)) and isinstance(merged.get(key, 0), (int, float)):
                merged[key] = merged.get(key, 0) + value
            elif key not in merged:
                merged[key] = value
        return merged

    def generate_next_message(self, message, state: ProgressiveSkillAgentState):
        if isinstance(message, MultiToolMessage):
            state.messages.extend(message.tool_messages)
        else:
            state.messages.append(message)

        turn_events: list[dict] = []
        hidden_cost = 0.0
        hidden_usage: dict | None = None
        # Permit correction of an unknown/repeated id without increasing the
        # hard number of modules that may be active.
        max_rounds = self.progressive_package.config.max_active_modules + 3
        for _ in range(max_rounds):
            self.domain_policy = self._build_policy(state.active_modules)
            state.system_messages = [SystemMessage(role="system", content=self.system_prompt)]
            candidate = generate(
                model=self.llm,
                tools=self.tools,
                messages=state.system_messages + state.messages,
                call_name="skillgen_progressive_agent_response",
                **self.llm_args,
            )
            activation_calls = [call for call in (candidate.tool_calls or []) if call.name == "activate_skill"]
            if not activation_calls:
                raw_data = dict(candidate.raw_data or {})
                raw_data["skillgen_activation"] = {
                    "events": turn_events,
                    "active_module_ids": list(state.active_modules),
                    "catalog_chars": len(self.progressive_package.catalog()),
                    "active_context_chars": sum(len(item["instructions"]) for item in state.active_modules.values()),
                    "package_hash": self.progressive_package.package_hash,
                }
                candidate.raw_data = raw_data
                if isinstance(candidate.cost, (int, float)):
                    candidate.cost += hidden_cost
                candidate.usage = self._add_usage(candidate.usage, hidden_usage)
                state.messages.append(candidate)
                return candidate, state

            state.messages.append(candidate)
            hidden_cost += candidate.cost if isinstance(candidate.cost, (int, float)) else 0.0
            hidden_usage = self._add_usage(hidden_usage, candidate.usage)
            for call in activation_calls:
                module_id = str((call.arguments or {}).get("module_id", ""))
                if module_id in state.active_modules:
                    activation = state.active_modules[module_id]
                    status = "already_active"
                elif len(state.active_modules) >= self.progressive_package.config.max_active_modules:
                    activation = {"ok": False, "module_id": module_id, "error": "activation_limit"}
                    status = "rejected"
                else:
                    activation = self.progressive_package.activate(module_id)
                    status = "activated" if activation["ok"] else "rejected"
                    if activation["ok"]:
                        state.active_modules[module_id] = activation
                event = {
                    "module_id": module_id, "status": status,
                    "source_atom_ids": activation.get("source_atom_ids") or [],
                    "required_tools": activation.get("required_tools") or [],
                    "trace_requirements": activation.get("trace_requirements") or [],
                    "context_chars": len(activation.get("instructions", "")),
                }
                turn_events.append(event)
                state.activation_events.append(event)
                content = json.dumps({
                    "status": status, "module_id": module_id,
                    "message": "Module loaded into runtime context." if status in {"activated", "already_active"} else activation.get("error"),
                }, ensure_ascii=False)
                state.messages.append(ToolMessage(
                    id=call.id or f"activate-{len(state.activation_events)}", role="tool",
                    content=content, requestor="assistant", error=status == "rejected",
                ))

            for call in (candidate.tool_calls or []):
                if call.name == "activate_skill":
                    continue
                state.messages.append(ToolMessage(
                    id=call.id or f"deferred-{call.name}", role="tool", requestor="assistant", error=True,
                    content="Business tool calls must be issued in a separate response after Skill activation.",
                ))

        raise RuntimeError("Progressive Skill activation loop exceeded the frozen activation budget")
