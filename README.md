You can make the devbox automatically:

* clone your GitHub repo
* pull latest changes on startup
* optionally install the repo in editable mode
* persist everything into the shared Modal Volume

Here is the recommended RL research setup.

# Updated `dev.py`

```python
import os
import time
import threading
import subprocess
import modal

APP_NAME = "rl-devbox"
VOLUME_NAME = "rl-shared-workspace"
MOUNT_PATH = "/workspace"

# ===== YOUR REPO =====
GITHUB_REPO = "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
REPO_NAME = "YOUR_REPO"

app = modal.App(APP_NAME)

workspace = modal.Volume.from_name(
    VOLUME_NAME,
    create_if_missing=True,
)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "git",
        "tmux",
        "vim",
        "curl",
        "wget",
        "htop",
        "nvtop",
        "build-essential",
        "cmake",
        "ninja-build",
    )
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "datasets",
        "trl",
        "peft",
        "bitsandbytes",
        "vllm",
        "wandb",
        "tensorboard",
        "jupyterlab",
    )
)

def auto_commit_loop():
    while True:
        time.sleep(300)

        try:
            workspace.commit()
            print("[auto-commit] committed")
        except Exception as e:
            print(f"[auto-commit] failed: {e}")

def run(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

@app.function(
    image=image,
    gpu="A100",
    cpu=16,
    memory=65536,
    timeout=86400,
    scaledown_window=3600,
    volumes={MOUNT_PATH: workspace},
)
def dev():

    workspace.reload()

    os.makedirs(MOUNT_PATH, exist_ok=True)

    repo_path = f"{MOUNT_PATH}/code/{REPO_NAME}"

    # ===== Clone or update repo =====
    if not os.path.exists(repo_path):

        run(f"""
        mkdir -p {MOUNT_PATH}/code
        cd {MOUNT_PATH}/code
        git clone {GITHUB_REPO}
        """)

    else:

        run(f"""
        cd {repo_path}
        git pull
        """)

    # ===== Optional editable install =====
    if os.path.exists(f"{repo_path}/setup.py") or os.path.exists(f"{repo_path}/pyproject.toml"):

        run(f"""
        cd {repo_path}
        pip install -e .
        """)

    # ===== Environment =====
    os.environ["HF_HOME"] = f"{MOUNT_PATH}/.cache/huggingface"
    os.environ["WANDB_DIR"] = f"{MOUNT_PATH}/wandb"

    os.makedirs(os.environ["HF_HOME"], exist_ok=True)
    os.makedirs(os.environ["WANDB_DIR"], exist_ok=True)

    threading.Thread(
        target=auto_commit_loop,
        daemon=True,
    ).start()

    bashrc = f"""
export HF_HOME={MOUNT_PATH}/.cache/huggingface
export WANDB_DIR={MOUNT_PATH}/wandb

alias save="python -c \\"import modal; modal.Volume.from_name('{VOLUME_NAME}').commit(); print('workspace committed')\\""
alias refresh="python -c \\"import modal; modal.Volume.from_name('{VOLUME_NAME}').reload(); print('workspace reloaded')\\""
alias gpu="nvidia-smi"

cd {repo_path}

echo "================================="
echo "RL Devbox Ready"
echo "Repo: {repo_path}"
echo "Workspace: {MOUNT_PATH}"
echo "================================="

exec bash
"""

    os.system(f"bash -lc {bashrc!r}")

    workspace.commit()
```

---

# Usage

## 1. Replace repo

Change:

```python
GITHUB_REPO = "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
REPO_NAME = "YOUR_REPO"
```

---

# 2. Launch shell

```bash
modal shell dev.py::dev
```

---

# 3. First startup

It automatically:

* creates `/workspace`
* clones repo
* installs repo
* creates HF cache
* creates wandb folder
* mounts persistent volume

---

# 4. Later startups

It automatically:

```bash
git pull
```

inside the repo.

---

# 5. Recommended workflow

Inside shell:

```bash
tmux new -s rl
```

Then:

```bash
cd /workspace/code/YOUR_REPO
```

Run training:

```bash
python train.py
```

---

# 6. Reconnect later

```bash
modal shell dev.py::dev
```

Then:

```bash
tmux attach -t rl
```

---

# Optional: multiple repos

You can extend:

```python
REPOS = [
    "...repo1...",
    "...repo2...",
]
```

and loop clone/pull.

---

# Optional: private GitHub repo

Best practice:

* use GitHub SSH deploy key
* or GitHub token secret

with Modal Secrets.

Example:

```python
secrets=[modal.Secret.from_name("github-secret")]
```

Then:

```bash
export GITHUB_TOKEN=...
```

inside container.

---

# Suggested RL repo layout

```text
/workspace
    /code
        /hydro-agent
        /grpo-framework
    /data
    /checkpoints
    /logs
    /.cache
```

This works very well for:

* GRPO
* RLHF
* vLLM
* hydrology simulators
* agent training
* distributed evaluation

on [Modal](https://modal.com?utm_source=chatgpt.com).


