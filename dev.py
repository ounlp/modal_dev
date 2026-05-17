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
