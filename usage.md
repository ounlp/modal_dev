# Modal Usage Manual for RL/ML Development

This guide focuses only on how to use [Modal](https://modal.com?utm_source=chatgpt.com) as a reusable GPU development environment.

---

# 1. Install Modal

Install:

```bash
pip install modal
```

Authenticate:

```bash
modal setup
```

This opens a browser login.

Verify:

```bash
modal profile current
```

---

# 2. Prepare `dev.py`

Save your Modal environment file:

```bash
dev.py
```

This file defines:

* image
* GPU
* shared workspace Volume
* packages
* startup behavior

---

# 3. How Modal Works

Modal has 3 important concepts:

| Component | Purpose                      |
| --------- | ---------------------------- |
| Image     | Environment (packages/tools) |
| Function  | Runtime configuration        |
| Volume    | Persistent storage           |

Containers themselves are temporary.

Volumes persist.

---

# 4. Create the Image

You define the image in Python:

```python
image = (
    modal.Image.debian_slim()
    .apt_install("tmux", "git")
    .pip_install("torch", "transformers")
)
```

Modal automatically builds this image.

No Dockerfile needed.

---

# 5. Launch a GPU Shell

Run:

```bash
modal shell dev.py::dev
```

Modal will:

1. build image if needed
2. allocate GPU
3. mount Volume
4. open interactive shell

You are now inside the remote container.

---

# 6. Check GPU

Inside shell:

```bash
nvidia-smi
```

or:

```bash
gpu
```

---

# 7. Use tmux

Start tmux:

```bash
tmux new -s rl
```

This keeps your work alive if terminal disconnects.

---

# 8. Detach tmux

Detach safely:

```text
Ctrl-b d
```

The session continues remotely.

---

# 9. Logout Modal Shell

Simply:

```bash
exit
```

The container may continue running.

---

# 10. Resume Later

Reconnect:

```bash
modal shell dev.py::dev
```

Reattach tmux:

```bash
tmux attach -t rl
```

---

# 11. Persistent Workspace

Inside your Modal function:

```python
workspace = modal.Volume.from_name(
    "shared-workspace",
    create_if_missing=True
)
```

Mounted:

```python
volumes={"/workspace": workspace}
```

Everything under:

```bash
/workspace
```

persists.

---

# 12. Save Changes

Important:

```bash
save
```

or:

```python
workspace.commit()
```

This publishes Volume changes.

---

# 13. Reload Latest Changes

If another machine updated the Volume:

```bash
refresh
```

or:

```python
workspace.reload()
```

---

# 14. Multiple Machines

You can connect from:

* desktop
* laptop
* office machine

using the SAME:

```bash
modal shell dev.py::dev
```

All machines share the same Volume.

---

# 15. Rebuilding Environment

If you modify:

```python
.pip_install(...)
```

or:

```python
.apt_install(...)
```

Modal automatically rebuilds image next launch.

No manual rebuild command required.

---

# 16. Change GPU Type

Inside function:

```python
gpu="A100"
```

Possible:

* `"H100"`
* `"A100"`
* `"A10G"`
* `"L40S"`

Restart shell afterward.

---

# 17. List Active Containers

```bash
modal container list
```

Example:

```text
ta-xxxxxxxx
```

---

# 18. Attach to Existing Container

```bash
modal shell <container-id>
```

Useful for reconnecting.

---

# 19. List Volumes

```bash
modal volume list
```

---

# 20. Browse Volume Files

```bash
modal volume ls shared-workspace /
```

---

# 21. Upload Local Files

```bash
modal volume put shared-workspace ./local.txt /local.txt
```

---

# 22. Download Files

```bash
modal volume get shared-workspace /model.pt ./model.pt
```

---

# 23. Recommended Workflow

## Start work

```bash
modal shell dev.py::dev
```

## Start tmux

```bash
tmux new -s rl
```

## Run experiments

```bash
python train.py
```

## Before leaving

```bash
save
```

Detach:

```text
Ctrl-b d
```

Logout:

```bash
exit
```

## Resume later

```bash
modal shell dev.py::dev
tmux attach -t rl
```

---

# 24. Important Persistence Rules

## Persisted

Inside mounted Volume:

```bash
/workspace
```

Examples:

* code
* checkpoints
* datasets
* logs

## NOT persisted

Outside Volume:

* `/tmp`
* running processes
* RAM
* shell history

---

# 25. Common Issue

## tmux disappeared

Container stopped.

Files remain in Volume.

Start new tmux session.

---

# 26. Recommended Structure

```text
/workspace
    /code
    /data
    /checkpoints
    /logs
    /.cache
```

---

# 27. Typical Daily Usage

Morning:

```bash
modal shell dev.py::dev
tmux attach -t rl
```

Work normally.

Before leaving:

```bash
save
Ctrl-b d
exit
```

Resume anytime later.

