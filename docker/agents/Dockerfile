ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG AGENT_DIR
COPY ade_bench/agents/installed_agents/${AGENT_DIR}/*-setup.sh \
     /installed-agent/install-agent.sh

RUN bash /installed-agent/install-agent.sh
