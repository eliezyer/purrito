"""
Example usage of the CatGt wrapper.

This script demonstrates various ways to use the purrito CatGt wrapper.

Need to update this for the new class
"""

from purrito import CatGt


def basic_example():
    """Basic usage example."""
    print("=" * 60)
    print("BASIC EXAMPLE")
    print("=" * 60)
    
    catgt = CatGt(
        basepath="/data/neuropixels",
        run="g0",
        gate=0,
        trigger=0
    )
    
    cmd = catgt.build_command()
    print(f"Command: {cmd}")
    print()


def preprocessing_example():
    """Example with preprocessing options."""
    print("=" * 60)
    print("PREPROCESSING EXAMPLE")
    print("=" * 60)
    
    catgt = CatGt(
        basepath="/data/neuropixels",
        run="g0",
        gate=0,
        trigger=0,
        ap=True,           # Process AP band
        lf=True,           # Process LF band
        prb=0,             # Probe index
        prb_fld=1,         # Probe folder
        dest="/data/processed"  # Output destination
    )
    
    cmd = catgt.build_command()
    print(f"Command: {cmd}")
    print()


def multi_probe_example():
    """Example with multiple probes."""
    print("=" * 60)
    print("MULTI-PROBE EXAMPLE")
    print("=" * 60)
    
    catgt = CatGt(
        basepath="/data/multi_probe_recording",
        run="g0",
        gate=0,
        trigger=0,
        prb=0,
        prb_list=[0, 1, 2, 3],  # Multiple probes
        ap=True,
        lf=True
    )
    
    cmd = catgt.build_command()
    print(f"Command: {cmd}")
    print()


def subprocess_example():
    """Example for use with subprocess."""
    print("=" * 60)
    print("SUBPROCESS EXAMPLE")
    print("=" * 60)
    
    catgt = CatGt(
        basepath="/data/test",
        run="g0",
        gate=0,
        ap=True
    )
    
    # Get command as list for subprocess
    args = catgt.get_command_args(catgt_path="/usr/local/bin/CatGt")
    
    print(f"Command args: {args}")
    print()
    print("Usage with subprocess:")
    print("  import subprocess")
    print(f"  subprocess.run({args})")
    print()


def custom_options_example():
    """Example with various custom options."""
    print("=" * 60)
    print("CUSTOM OPTIONS EXAMPLE")
    print("=" * 60)
    
    catgt = CatGt(
        basepath="/data/experiment",
        run="g0_t0",
        gate=0,
        trigger=0,
        ap=True,
        lf=True,
        t_cat=1,           # Concatenate trials
        prb=0,
        prb_fld=1,
        xa=[0, 100, 200],  # Extract specific channels
        dest="/output"
    )
    
    cmd = catgt.build_command()
    print(f"Command: {cmd}")
    print()


if __name__ == "__main__":
    basic_example()
    preprocessing_example()
    multi_probe_example()
    subprocess_example()
    custom_options_example()
