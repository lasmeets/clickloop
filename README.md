# ClickLoop

Automated mouse clicking script for Windows with multi-monitor support. ClickLoop allows you to automate repetitive clicking tasks across multiple monitors using Python's standard library (no external dependencies required for basic functionality).

## Features

- **Multi-monitor support**: Automatically detects and handles multiple displays
- **Interactive coordinate picker**: Easy-to-use tool for capturing click positions
- **Configurable loops**: Control how many times the sequence runs
- **Adjustable timing**: Set wait times between clicks and between loop iterations
- **Windows-native**: Uses Windows API via ctypes (no additional dependencies)

## Requirements

- **Windows**: This tool uses Windows-specific APIs and will not work on other operating systems
- **Python 3.12 or higher**: The project requires Python 3.12+
- **No external dependencies**: Uses only Python's standard library

## Installation

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd clickloop
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

**On Windows (Command Prompt):**
```cmd
.venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**On Unix/macOS (for development):**
```bash
source .venv/bin/activate
```

### 4. Install the Package

Install ClickLoop in development/editable mode:

```bash
pip install -e .
```

This installs the `click` command-line tool that you can use to run ClickLoop commands.

### 5. Install Development Dependencies (Optional)

If you want to run tests or linting:

```bash
pip install -e ".[dev]"
```

## Quick Start

### Step 1: Create Configuration File

Create a configuration file at `data/config/coordinates.json`. You can copy the example file:

```bash
cp data/config/coordinates.json.example data/config/coordinates.json
```

Or create it manually with the following structure:

```json
{
  "loops": 10,
  "wait_between_clicks": 1.0,
  "wait_between_loops": 2.0,
  "coordinates": [
    {
      "monitor": 0,
      "x": 100,
      "y": 200
    }
  ]
}
```

### Step 2: Set Up Coordinates

You have two options for setting up coordinates:

#### Option A: Use the Interactive Coordinate Picker (Recommended)

This is the easiest way to capture click positions:

```bash
click pick
```

The picker will:
1. Display all detected monitors
2. Show your current mouse position in real-time
3. Allow you to capture coordinates by:
   - Pressing **SPACE** or **ENTER**
   - Clicking the **LEFT MOUSE BUTTON**
   - Pressing **ESC** to finish and save

The coordinates will be automatically saved to `data/config/coordinates.json` (or the path you specify with `--config`).

#### Option B: Manually Edit the JSON File

Edit `data/config/coordinates.json` directly and add coordinate objects to the `coordinates` array:

```json
{
  "loops": 10,
  "wait_between_clicks": 1.0,
  "wait_between_loops": 2.0,
  "coordinates": [
    {
      "monitor": 0,
      "x": 100,
      "y": 200
    },
    {
      "monitor": 1,
      "x": 300,
      "y": 400
    }
  ]
}
```

**Coordinate Structure:**
- `monitor`: The monitor index (0 for the first monitor, 1 for the second, etc.)
- `x`: X coordinate relative to the monitor (left edge is 0)
- `y`: Y coordinate relative to the monitor (top edge is 0)

**Finding Monitor Indices:**
- Run `click pick` to see which monitor is which (monitors are numbered starting from 0)
- The primary monitor is usually index 0
- Monitor indices are displayed when you run the `pick` command

### Step 3: Run the Click Loop

Execute the automated clicking sequence:

```bash
click run
```

This will:
1. Load the configuration from `data/config/coordinates.json`
2. Detect all monitors
3. Execute the click sequence for the specified number of loops
4. Wait between clicks and between loops as configured

## Configuration File Reference

The configuration file (`data/config/coordinates.json`) controls all aspects of the click loop behavior.

### File Location

Default location: `data/config/coordinates.json`

You can specify a custom path using the `--config` argument:

```bash
click run --config /path/to/your/config.json
```

### Configuration Structure

```json
{
  "loops": 10,
  "wait_between_clicks": 1.0,
  "wait_between_loops": 2.0,
  "coordinates": [
    {
      "monitor": 0,
      "x": 100,
      "y": 200
    }
  ]
}
```

### Configuration Fields

#### `loops` (integer, required)
Number of times to repeat the entire click sequence.

- **Default**: `3` (if not specified)
- **Minimum**: `1`
- **Example**: `10` will repeat the sequence 10 times

#### `wait_between_clicks` (float, required)
Number of seconds to wait between each individual click in the sequence.

- **Default**: `1.0` (if not specified)
- **Minimum**: `0.0` (no wait)
- **Example**: `0.5` waits half a second between clicks

#### `wait_between_loops` (float, required)
Number of seconds to wait between each complete loop iteration.

- **Default**: `2.0` (if not specified)
- **Minimum**: `0.0` (no wait)
- **Example**: `3.0` waits 3 seconds between loop iterations

#### `coordinates` (array, required)
Array of coordinate objects defining where to click. Each coordinate object must have:

- `monitor` (integer): Monitor index (0-based)
- `x` (number): X coordinate relative to monitor (pixels from left edge)
- `y` (number): Y coordinate relative to monitor (pixels from top edge)

**Example:**
```json
"coordinates": [
  {
    "monitor": 0,
    "x": 100,
    "y": 200
  },
  {
    "monitor": 1,
    "x": 300,
    "y": 400
  }
]
```

The clicks will be executed in the order they appear in the array, and this sequence will be repeated `loops` times.

### Default Values

If you omit any of these fields, the following defaults will be used:

```json
{
  "loops": 3,
  "wait_between_clicks": 1.0,
  "wait_between_loops": 2.0,
  "coordinates": []
}
```

**Note**: You must provide at least one coordinate in the `coordinates` array, otherwise the loop will fail to run.

## Command-Line Usage

### Run Command

Execute the click loop:

```bash
click run [OPTIONS]
```

**Options:**

- `--config PATH`: Path to configuration file (default: `data/config/coordinates.json`)
- `--loops NUMBER`: Override the number of loops from config file
- `--wait-clicks SECONDS`: Override wait time between clicks from config file
- `--wait-loops SECONDS`: Override wait time between loops from config file

**Examples:**

```bash
# Use default config file
click run

# Use custom config file
click run --config /path/to/config.json

# Override number of loops
click run --loops 20

# Override timing settings
click run --wait-clicks 0.5 --wait-loops 1.0

# Combine options
click run --config myconfig.json --loops 5 --wait-clicks 2.0
```

### Pick Command

Interactive coordinate picker:

```bash
click pick [OPTIONS]
```

**Options:**

- `--config PATH`: Path to configuration file where coordinates will be saved (default: `data/config/coordinates.json`)

**Usage:**

1. Run `click pick`
2. Move your mouse to the desired position
3. Press **SPACE**, **ENTER**, or click **LEFT MOUSE BUTTON** to capture the current position
4. Repeat step 2-3 for each coordinate you want to add
5. Press **ESC** to finish and save all captured coordinates

**Note**: When using `pick`, captured coordinates are **merged** with existing coordinates in the config file. If you want to start fresh, either delete the coordinates array or create a new config file.

**Example:**

```bash
# Save to default location
click pick

# Save to custom location
click pick --config /path/to/myconfig.json
```

## Working with Multiple Monitors

ClickLoop automatically detects all connected monitors and assigns them indices starting from 0.

### Finding Monitor Information

Run the pick command to see monitor information:

```bash
click pick
```

The output will show:
```
Detected monitors:
  Monitor 0: 1920x1080 at (0, 0) (PRIMARY)
  Monitor 1: 2560x1440 at (1920, 0)
```

### Setting Coordinates on Multiple Monitors

In your `coordinates.json`, specify which monitor each coordinate belongs to:

```json
{
  "coordinates": [
    {
      "monitor": 0,
      "x": 960,
      "y": 540
    },
    {
      "monitor": 1,
      "x": 1280,
      "y": 720
    }
  ]
}
```

Coordinates are relative to each monitor:
- Monitor 0: (0, 0) is the top-left corner of monitor 0
- Monitor 1: (0, 0) is the top-left corner of monitor 1

## Examples

### Example 1: Simple Single-Click Loop

Click once per loop, 10 times:

```json
{
  "loops": 10,
  "wait_between_clicks": 1.0,
  "wait_between_loops": 2.0,
  "coordinates": [
    {
      "monitor": 0,
      "x": 500,
      "y": 300
    }
  ]
}
```

### Example 2: Multi-Click Sequence

Click three different positions in sequence, repeat 5 times:

```json
{
  "loops": 5,
  "wait_between_clicks": 0.5,
  "wait_between_loops": 3.0,
  "coordinates": [
    {
      "monitor": 0,
      "x": 100,
      "y": 100
    },
    {
      "monitor": 0,
      "x": 200,
      "y": 200
    },
    {
      "monitor": 0,
      "x": 300,
      "y": 300
    }
  ]
}
```

### Example 3: Cross-Monitor Clicking

Click positions on two different monitors:

```json
{
  "loops": 3,
  "wait_between_clicks": 1.0,
  "wait_between_loops": 2.0,
  "coordinates": [
    {
      "monitor": 0,
      "x": 960,
      "y": 540
    },
    {
      "monitor": 1,
      "x": 1280,
      "y": 720
    }
  ]
}
```

## Troubleshooting

### "Configuration file not found"

Make sure you've created the configuration file at `data/config/coordinates.json` or specify the correct path with `--config`.

### "No monitors detected"

This usually indicates a problem with Windows API calls. Ensure you're running on Windows and that your display settings are configured correctly.

### "No coordinates specified in configuration"

You must provide at least one coordinate in the `coordinates` array. Use `click pick` to capture coordinates or manually edit the JSON file.

### "Invalid coordinate: monitor index out of range"

The monitor index you specified doesn't exist. Run `click pick` to see which monitors are available (indices start at 0).

### Coordinates seem incorrect

Remember that coordinates are relative to each monitor, not the virtual screen. Use the interactive picker (`click pick`) to accurately capture positions.

## Development

### Running Tests

```bash
pytest
```

### Linting

```bash
pylint src/clickloop
```

## License

MIT

## Author

Chris
