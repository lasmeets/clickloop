# ClickLoop

Automated mouse clicking script for Windows with multi-monitor support. ClickLoop allows you to automate repetitive clicking tasks across multiple monitors using Python's standard library (no external dependencies required for basic functionality).

## Project Description

ClickLoop is a command-line tool designed to automate mouse clicking operations on Windows systems. It's particularly useful for:

- Automating repetitive UI interactions
- Testing applications that require mouse clicks
- Performing routine tasks that involve clicking specific screen coordinates
- Working with multi-monitor setups where coordinates need to be specified per monitor

The tool uses only Python's standard library (specifically `ctypes` for Windows API calls), making it lightweight with no external dependencies beyond Python itself.

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

### 5. Verify Installation

Verify that ClickLoop is installed correctly:

```bash
click --help
```

### 6. Install Development Dependencies (Optional)

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

**How it works:**
1. The tool detects all connected monitors and displays their information
2. Move your mouse to the desired position
3. Press **SPACE**, **ENTER**, or **LEFT MOUSE BUTTON** to capture the current position
4. Press **ESC** to finish and save all captured coordinates
5. Press **Ctrl+C** to exit without saving

**Example output:**
```
============================================================
Coordinate Picker Mode
============================================================

Detected monitors:
  Monitor 0: 1920x1080 at (0, 0) (PRIMARY)
  Monitor 1: 2560x1440 at (1920, 0)

------------------------------------------------------------
Instructions:
  - Move your mouse to the desired position
  - Press SPACE or ENTER to capture current position
  - Click LEFT MOUSE BUTTON to capture current position
  - Press ESC to finish and save coordinates
  - Press Ctrl+C to exit without saving
------------------------------------------------------------

✓ Captured coordinate #1: Monitor 0, (100, 200) [Virtual: (100, 200)]
```

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

**Example execution:**
```
Detected monitors:
  Monitor 0: 1920x1080 at (0, 0) (PRIMARY)
  Monitor 1: 2560x1440 at (1920, 0)
Starting click loop: 3 iterations
Coordinates to click: 4
Wait between clicks: 1.0s
Wait between loops: 2.0s
Loop 1/3
Loop 2/3
Loop 3/3
Click loop completed!
```

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

ClickLoop fully supports multi-monitor configurations. Understanding how monitors are numbered and how coordinates work is essential for proper setup.

### Understanding Monitor Indices

Monitors are automatically detected and numbered starting from `0`:

- **Monitor 0**: First detected monitor (usually the primary monitor)
- **Monitor 1**: Second monitor
- **Monitor 2**: Third monitor
- And so on...

The primary monitor is automatically identified and marked in the output.

### Coordinate System

Each monitor uses its own coordinate system:

- **Origin (0, 0)**: Top-left corner of each monitor
- **X-axis**: Increases from left to right
- **Y-axis**: Increases from top to bottom

Coordinates are specified **relative to each monitor**, not the virtual desktop. For example:
- `(0, 0)` on Monitor 0 is the top-left of Monitor 0
- `(0, 0)` on Monitor 1 is the top-left of Monitor 1

### Finding Monitor Information

When you run `click run` or `click pick`, the tool displays all detected monitors:

```bash
click pick
```

The output will show:
```
Detected monitors:
  Monitor 0: 1920x1080 at (0, 0) (PRIMARY)
  Monitor 1: 2560x1440 at (1920, 0)
```

This shows:
- Monitor index
- Resolution (width x height)
- Virtual desktop position
- Whether it's the primary monitor

### Using the Coordinate Picker with Multiple Monitors

The `pick` command is the easiest way to set up coordinates for multi-monitor setups:

1. Run `click pick`
2. Move your mouse to the desired position on any monitor
3. The tool displays:
   - Which monitor the mouse is on
   - Monitor-relative coordinates
   - Virtual desktop coordinates
4. Press SPACE/ENTER/LEFT CLICK to capture
5. Repeat for all positions you need
6. Press ESC to save

The picker automatically detects which monitor contains your mouse cursor and saves the correct monitor index and relative coordinates.

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

### Common Issues and Solutions

#### "No monitors detected"

**Problem:** ClickLoop cannot detect any monitors.

**Solutions:**
- Ensure your monitors are properly connected and powered on
- Check Windows Display Settings to verify monitors are detected by Windows
- Try restarting the application
- Run ClickLoop with administrator privileges (if needed)

#### "Configuration file not found"

**Problem:** ClickLoop cannot find the configuration file.

**Solutions:**
- Check the file path is correct (default: `data/config/coordinates.json`)
- Use `--config` to specify a different path
- Create the configuration file manually or use `click pick` to generate one

#### "No coordinates specified in configuration"

**Problem:** The configuration file doesn't contain any coordinates.

**Solutions:**
- You must provide at least one coordinate in the `coordinates` array
- Use `click pick` to capture coordinates or manually edit the JSON file

#### "Invalid coordinate: monitor index out of range"

**Problem:** A coordinate references a monitor that doesn't exist.

**Solutions:**
- Run `click run` to see which monitors are detected
- Verify monitor indices in your configuration file (they start at 0)
- If you disconnected a monitor, update your configuration to use valid monitor indices

#### "Invalid coordinate: coordinate out of bounds"

**Problem:** A coordinate is outside the bounds of the specified monitor.

**Solutions:**
- Check the monitor's resolution using `click run` or `click pick`
- Ensure X and Y coordinates are within the monitor's width and height
- Use `click pick` to capture valid coordinates interactively

#### "Invalid JSON in configuration file"

**Problem:** The configuration file contains invalid JSON.

**Solutions:**
- Validate your JSON syntax using a JSON validator
- Check for missing commas, brackets, or quotes
- Ensure all coordinate objects have `monitor`, `x`, and `y` fields
- Use `click pick` to generate a valid configuration file

#### Clicks are happening in the wrong location

**Problem:** The mouse clicks at incorrect positions.

**Solutions:**
- Verify you're using monitor-relative coordinates, not virtual desktop coordinates
- Re-capture coordinates using `click pick` if monitor arrangement changed
- Check if Windows display scaling is affecting coordinates (ClickLoop uses physical pixels)
- Ensure the application window hasn't moved or resized

#### Application becomes unresponsive during clicking

**Problem:** The system or application freezes during automated clicking.

**Solutions:**
- Increase `wait_between_clicks` to give the application more time to respond
- Reduce the number of `loops` for testing
- Check if the target application can handle rapid clicking
- Ensure you're not clicking on system-critical areas

#### Coordinates work on one system but not another

**Problem:** Configuration works on one computer but fails on another.

**Solutions:**
- Monitor resolutions and arrangements differ between systems
- Re-capture coordinates on each system using `click pick`
- Don't share configuration files between systems with different monitor setups

### Getting Help

If you encounter issues not covered here:

1. Check the log file at `data/logs/clickloop.log` for detailed error messages
2. Run with verbose logging to see what's happening
3. Verify your Python version is 3.12 or higher
4. Ensure you're running on Windows (this tool is Windows-specific)

### Debugging Tips

1. **Start simple**: Test with a single coordinate and one loop
2. **Use the picker**: Always use `click pick` to capture coordinates rather than guessing
3. **Check monitor info**: Run `click run` to see detected monitors before configuring
4. **Test incrementally**: Add coordinates one at a time to identify problematic entries
5. **Verify coordinates**: Use the picker's output to verify coordinates are within monitor bounds

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
