"""Example usage of the CatGt wrapper (updated for the new API).

This file demonstrates how to use the refactored `CatGt_wrapper` class
which groups options by stage (input → filters → extraction → output)
and supports method chaining.
"""

from purrito import CatGt_wrapper


def basic_example():
    """Basic usage example using the new grouped methods."""
    print("=" * 60)
    print("BASIC EXAMPLE")
    print("=" * 60)

    catgt = CatGt_wrapper(
        catgt_path="CatGt",
        basepath="/data/neuropixels",
        run="g0",
        gate=0,
        trigger=0,
    )

    # Configure filters and input probe
    catgt.set_filters(ap=True, lf=True).set_input(prb=0)

    cmd = " ".join(catgt.build_command())
    print(f"Command: {cmd}")
    print()


def preprocessing_example():
    """Example with preprocessing options using method chaining."""
    print("=" * 60)
    print("PREPROCESSING EXAMPLE")
    print("=" * 60)

    catgt = CatGt_wrapper(
        catgt_path="/home/user/catgtfolder/CatGt",
        basepath="/data/neuropixels",
        run="g0",
        gate=0,
        trigger=0,
    )

    catgt.set_filters(ap=True, lf=True).set_input(prb=0, prb_fld=1).set_output(dest="/data/processed")

    # Show the command that would be run
    catgt.dry_run()
    print()


def multi_probe_example():
    """Example with multiple probes (passes probe list via input stage)."""
    print("=" * 60)
    print("MULTI-PROBE EXAMPLE")
    print("=" * 60)

    catgt = CatGt_wrapper(
        catgt_path="/home/user/catgtfolder/CatGt",
        basepath="/data/multi_probe_recording",
        run="g0",
        gate=0,
        trigger=0,
    )

    # prb_list is accepted through set_input's **kwargs and will be formatted
    catgt.set_filters(ap=True, lf=True).set_input(prb=0, prb_list=[0, 1, 2, 3])

    print(" ".join(catgt.build_command()))
    print()


def subprocess_example():
    """Example showing how to use `get_command_args` for subprocess calls."""
    print("=" * 60)
    print("SUBPROCESS EXAMPLE")
    print("=" * 60)

    catgt = CatGt_wrapper(
        catgt_path="/usr/local/bin/CatGt",
        basepath="/data/test",
        run="g0",
    )

    catgt.set_filters(ap=True)

    # Get command as list for subprocess
    args = catgt.get_command_args()

    print(f"Command args: {args}")
    print()
    print("Usage with subprocess:")
    print("  import subprocess")
    print(f"  subprocess.run({args})")
    print()


def custom_options_example():
    """Example with various custom options and extraction settings."""
    print("=" * 60)
    print("CUSTOM OPTIONS EXAMPLE")
    print("=" * 60)

    catgt = CatGt_wrapper(
        catgt_path="CatGt",
        basepath="/data/experiment",
        run="g0_t0",
        gate=0,
        trigger=0,
    )

    # Use extraction and output grouped methods; lists are supported
    catgt.set_filters(ap=True, lf=True).set_input(prb=0, prb_fld=1).set_extraction(xa=[0, 100, 200]).set_output(dest="/output")

    print(" ".join(catgt.build_command()))
    print()


if __name__ == "__main__":
    basic_example()
    preprocessing_example()
    multi_probe_example()
    subprocess_example()
    custom_options_example()
