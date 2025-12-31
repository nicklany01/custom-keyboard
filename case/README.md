# Case Implementation
This case is built with build123d and viewed with ocp_vscode.
## 1. Install
```bash
pip install build123d ocp_vscode
```

## 2. Start Viewer
*Ignore this section if using the OCP VSCode extension.*
Run this once to start the server in a detached tmux session:
```bash
tmux new -s viewer -d 'python -m ocp_vscode'
```
Open browser to: `http://127.0.0.1:3939`
*Note: other options are to use screen, run in background with &, suspend with ctrl z and send to background using bg, or use another terminal.*

## 3. Usage
### Dependencies
Make sure pcb_outline.svg exists by running:
```sh
kicad-cli pcb export svg --layers Edge.Cuts --exclude-drawing-sheet --drill-shape-opt 0 -o case/build/pcb_outline.svg pcb/pcb.kicad_pcb
```

Ensure this is in the python source code:

```python
from build123d import *
from ocp_vscode import show

# At the end of the file, where model is the model that was defined
show(model)
```

## 4. Commands
* **Run script:** `python main.py` (updates viewer)
* **Check logs:** `tmux attach -t viewer`
* **Kill server:** `tmux kill-session -t viewer`
