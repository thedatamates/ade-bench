from enum import Enum


class AgentName(Enum):
    # Abstract agents
    ABSTRACT_INSTALLED = "abstract-installed"

    # Non-abstract agents
    NONE = "none"
    ORACLE = "oracle"
    CLAUDE_CODE = "claude-code"
    OPENAI_CODEX = "openai-codex"
    GEMINI_CLI = "gemini-cli"
    MACRO = "macro"

    def model_name_from_agent_name(model_name, agent_name):
        if agent_name == AgentName.ORACLE:
            return "Oracle"
        elif agent_name == AgentName.NONE:
            return "None"
        else:
            return model_name
