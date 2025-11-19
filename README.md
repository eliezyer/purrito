# purrito

A Python wrapper for CatGt, providing a human-readable interface to generate command-line arguments for the CatGt tool.

## Overview

CatGt is a command-line tool for preprocessing SpikeGLX data from Neuropixels probes. This wrapper simplifies the process of creating CatGt commands by allowing users to specify options in Python.

## Installation

```bash
pip install -e .
```

Soon this package will be sent to pypi

## Usage

### Basic Example

```python
from purrito import CatGt

# Create a CatGt instance with basic parameters
catgt = CatGt(
    basepath="/path/to/data",
    run="g0",
    gate=0,
    trigger=0
)

# Check the command that will be executed
catgt.dry_run()

#Output: CatGt -dir=/path/to/data -run=g0 -g=0 -t=0


# Run catgt
catgt.run()
# Generate the command line string

```

### Advanced Example with Options

```python
from purrito import CatGt

# Create a CatGt instance with preprocessing options
catgt = CatGt(
    basepath="/data/neuropixels",
    run="g0",
    gate=0,
    trigger=0,
    ap=True,           # Process AP band
    lf=True,           # Process LF band
    prb=0,             # Probe index
    prb_fld=1,         # Probe folder
    dest="/data/processed",  # Output destination
    channels=[0, 1, 2, 3]    # Channel list
)

cmd = catgt.build_command()
print(cmd)
```

### Using with subprocess

```python
import subprocess
from purrito import CatGt

catgt = CatGt(
    basepath="/data/test",
    run="g0",
    gate=0,
    ap=True
)

# Get command as list for subprocess
args = catgt.get_command_args(catgt_path="/usr/local/bin/CatGt")

# Run the command
# subprocess.run(args)
```

## Features

- **Intuitive Python API**: Specify options using Python arguments
- **Flexible Options**: Support for boolean flags, string values, numeric values, and lists
- **Automatic Formatting**: Converts Python naming conventions (underscores) to CatGt conventions (dashes)
- **Path Handling**: Automatically converts relative paths to absolute paths
- **Command Generation**: Generate command strings for direct use or subprocess execution

## API Reference

### CatGt Class

```python
CatGt(basepath, run, gate=None, trigger=None, **options)
```

**Parameters:**
- `basepath` (str): Base directory path containing the SpikeGLX data
- `run` (str): Run name (e.g., "g0", "g0_t0")
- `gate` (int, optional): Gate index
- `trigger` (int, optional): Trigger index
- `**options`: Additional CatGt options as keyword arguments

**Methods:**
- `build_command(catgt_path="CatGt")`: Build the complete command line string
- `get_command_args(catgt_path="CatGt")`: Get command and arguments as a list for subprocess

## Testing

Run tests using unittest:

```bash
python -m unittest discover tests
```

Or with pytest (if installed):

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
