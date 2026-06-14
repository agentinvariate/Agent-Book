#!/usr/bin/env bash
set -Eeuo pipefail

APP="fabricops-deepagent"
INSTALL_DIR="/opt/${APP}"

echo "=================================================="
echo " FabricOps DeepAgent Bootstrap"
echo "=================================================="

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root:"
  echo "sudo $0"
  exit 1
fi

apt-get update
apt-get install -y \
  python3 \
  python3-venv \
  python3-pip \
  git \
  curl \
  jq

mkdir -p "${INSTALL_DIR}"
cd "${INSTALL_DIR}"

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install \
  deepagents \
  langchain \
  langgraph \
  langchain-openai \
  kubernetes \
  fastapi \
  uvicorn \
  pydantic

cat > "${INSTALL_DIR}/agent.py" <<'PY'
import os
import subprocess
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI


def run_check(command: str):
    """Run approved VPS, k3s, Fabric, and SurrealDB health checks."""
    allowed = {
        "nodes": "sudo k3s kubectl get nodes -o wide",
        "pods": "sudo k3s kubectl get pods -A -o wide",
        "events": "sudo k3s kubectl get events -A --sort-by=.lastTimestamp | tail -80",
        "disk": "df -h",
        "memory": "free -h",
        "fabric": "sudo k3s kubectl get pods,svc -n fabric -o wide",
        "storage": "sudo k3s kubectl get sc,pv,pvc -A",
        "failed": "systemctl --failed --no-pager"
    }

    if command not in allowed:
        return f"DENIED: {command}. Allowed checks: {list(allowed.keys())}"

    result = subprocess.run(
        allowed[command],
        shell=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return (result.stdout + result.stderr)[-12000:]


SYSTEM_PROMPT = """
You are FabricOps DeepAgent for Chinmay Panda's VPS.

Responsibilities:
- Monitor VPS.
- Monitor k3s.
- Monitor Fabric namespace.
- Monitor SurrealDB.
- Detect failures.
- Recommend repairs.

Never:
- Delete namespaces.
- Delete PVCs.
- Delete databases.
- Delete nodes.
- Change firewall.
- Rotate secrets.

For risky actions output:
APPROVAL_REQUIRED

Return a concise health report with status, findings, risk, and next action.
"""

model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    temperature=0,
)

agent = create_deep_agent(
    model=model,
    tools=[run_check],
    system_prompt=SYSTEM_PROMPT,
)

result = agent.invoke({
    "messages": "Check VPS, Kubernetes, Fabric namespace, SurrealDB, storage, events, and failed services. Generate health report."
})

print(result)
PY

cat > "${INSTALL_DIR}/run.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd /opt/fabricops-deepagent
source .venv/bin/activate
python agent.py
SH

chmod +x "${INSTALL_DIR}/run.sh"

cat > "${INSTALL_DIR}/.env" <<'ENV'
OPENAI_API_KEY=PUT_KEY_HERE
OPENAI_MODEL=gpt-4.1-mini
ENV

cat > /etc/systemd/system/fabricops.service <<'SERVICE'
[Unit]
Description=FabricOps DeepAgent
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/opt/fabricops-deepagent
EnvironmentFile=/opt/fabricops-deepagent/.env
ExecStart=/opt/fabricops-deepagent/run.sh
SERVICE

cat > /etc/systemd/system/fabricops.timer <<'TIMER'
[Unit]
Description=Run FabricOps DeepAgent every 15 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min

[Install]
WantedBy=timers.target
TIMER

systemctl daemon-reload
systemctl enable fabricops.timer

echo ""
echo "======================================"
echo "INSTALLATION COMPLETE"
echo "======================================"
echo ""
echo "Update API key:"
echo "nano ${INSTALL_DIR}/.env"
echo ""
echo "Then run:"
echo "systemctl start fabricops.timer"
echo "systemctl start fabricops.service"
echo ""
echo "Check logs:"
echo "journalctl -u fabricops.service -n 100 --no-pager"
echo ""
