# Sketchpad Studio

Sketchpad Studio is a lightweight desktop drawing app built with `pygame`. It keeps the project simple, but behaves like a real app instead of a one-off script.

## Features

- Brush and eraser tools
- Palette swatches plus HSL color controls
- Multiple brush sizes
- Undo support
- Save dialog with PNG export
- Keyboard shortcuts and status feedback

## Run

Create or activate a Python 3.11+ environment, install dependencies, and start the app:

```powershell
pip install -r requirements.txt
python -m sketchpad
```

The legacy launcher still works too:

```powershell
python Simple_Sketchpad.py
```

## Shortcuts

- `B`: brush
- `E`: eraser
- `[ / ]`: smaller or larger preset brush
- `Ctrl+Z`: undo
- `Ctrl+S`: save
- `Ctrl+N`: clear canvas
