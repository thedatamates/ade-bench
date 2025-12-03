from ade_bench.agents.agent_name import AgentName
from ade_bench.agents.base_agent import BaseAgent
from ade_bench.agents.installed_agents.claude_code.claude_code_agent import (
    ClaudeCodeAgent,
)
from ade_bench.agents.installed_agents.openai_codex.openai_codex_agent import (
    OpenAICodexAgent,
)
from ade_bench.agents.installed_agents.gemini_cli.gemini_cli_agent import (
    GeminiCLIAgent,
)
from ade_bench.agents.installed_agents.macro.macro_agent import (
    MacroAgent,
)
from ade_bench.agents.none_agent import NoneAgent
from ade_bench.agents.sage_agent import SageAgent


class AgentFactory:
    AGENT_NAME_TO_CLASS = {
        NoneAgent.NAME: NoneAgent,
        SageAgent.NAME: SageAgent,
        ClaudeCodeAgent.NAME: ClaudeCodeAgent,
        OpenAICodexAgent.NAME: OpenAICodexAgent,
        GeminiCLIAgent.NAME: GeminiCLIAgent,
        MacroAgent.NAME: MacroAgent,
    }

    @staticmethod
    def get_agent(agent_name: AgentName, **kwargs) -> BaseAgent:
        agent_class = AgentFactory.AGENT_NAME_TO_CLASS.get(agent_name)

        if agent_class is None:
            raise ValueError(
                f"Unknown agent: {agent_name}. "
                f"Available agents: {AgentFactory.AGENT_NAME_TO_CLASS.keys()}"
            )

        return agent_class(**kwargs)
