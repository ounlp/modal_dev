You can make the devbox automatically:

* clone your GitHub repo
* pull latest changes on startup
* optionally install the repo in editable mode
* persist everything into the shared Modal Volume

Here is the recommended RL research setup.


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


