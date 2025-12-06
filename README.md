# ClickLoop

A simple Python script to automate mouse clicks at specified coordinates on Windows 11. Uses only Python standard library (no external dependencies required).

## Features

- Click at multiple customizable XY coordinates
- Configurable loop count (default: 10 iterations)
- Configurable delays between clicks and between loops
- Support for left-click and right-click
- Input coordinates via command-line or JSON config file
- Uses Windows API via `ctypes` (standard library only)

## Requirements

- Python 3.13
- Windows 11 (uses Windows API)
- Virtual environment (`.venv`)

## Usage

### Basic Usage

Click at coordinates (100, 200) and (300, 400), repeating 10 times:

```bash
.venv/bin/python clickloop.py -c "100,200 300,400"
```

### Custom Loop Count

Run 5 iterations instead of default 10:

```bash
.venv/bin/python clickloop.py -c "100,200 300,400" -l 5
```

### Custom Delays

Set delay between clicks to 0.5 seconds and delay between loops to 1.0 seconds:

```bash
.venv/bin/python clickloop.py -c "100,200 300,400" -d 0.5 -D 1.0
```

### Using Config File

Create a JSON file (see `config.example.json`) and load coordinates:

```bash
.venv/bin/python clickloop.py -f config.json
```

Example `config.json`:
```json
{
  "coordinates": [
    [100, 200],
    [300, 400],
    [500, 600]
  ]
}
```

### Right-Click

Use right-click instead of left-click:

```bash
.venv/bin/python clickloop.py -c "100,200" --button right
```

## Command-Line Options

- `-c, --coordinates`: Coordinates as string (e.g., `"x1,y1 x2,y2"` or `"x1,y1;x2,y2"`)
- `-f, --file`: Path to JSON config file with coordinates
- `-l, --loops`: Number of times to repeat the click sequence (default: 10)
- `-d, --delay`: Delay in seconds between clicks (default: 1.0)
- `-D, --delay-loops`: Delay in seconds between loop iterations (default: 2.0)
- `--button`: Mouse button to use - `left` or `right` (default: left)

## Examples

```bash
# Simple click sequence
.venv/bin/python clickloop.py -c "100,200 300,400"

# Fast clicks with shorter delays
.venv/bin/python clickloop.py -c "100,200 300,400" -d 0.2 -D 0.5 -l 20

# Load from config file with custom loop count
.venv/bin/python clickloop.py -f my_coords.json -l 5

# Right-click at single coordinate
.venv/bin/python clickloop.py -c "500,600" --button right -l 1
```

## Safety

The script includes a 3-second countdown before starting to give you time to position your cursor or cancel the operation (Ctrl+C).

## Notes

- This script uses Windows API functions via `ctypes` and will only work on Windows
- The script moves the cursor to each coordinate before clicking
- All coordinates are absolute screen coordinates
- Press Ctrl+C to interrupt the script at any time

