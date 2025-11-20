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
        run_name="g0",
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


#%% trying to replicate command used in lab

from purrito import CatGt_wrapper
catgt_local_path = "/Users/elie/Documents/github/CatGt/CatGt-linux/CatGt"
basepath_local = "/Users/elie/Documents/github/CatGt/data/NPX3_11_13_25_offline2_CA_TH_g0"
catgt_output_path = "/Users/elie/Documents/github/CatGt/data/NPX3_11_13_25_offline2_CA_TH_g0_catgt" # this will be generated automatically in pipeline

# intializing CatGt wrapper
catgt = CatGt_wrapper(
    catgt_path=catgt_local_path, # mandatory path to CatGt executable
    basepath=basepath_local, # mandatory basepath where data is located
    gate=0, # optional gate number (default 0)
    trigger=0, # optional trigger number (default 0)
)

catgt.set_input(prb=0, prb_fld=True) # setting input probe and probe field
catgt.set_filters(ap=True, apfilter="butter,12,300,9000") # setting filters: ap, lf, gblcar
catgt.set_filters(lf=True, lffilter="butter,12,1,600") # setting filters: ap, lf, gblcar
catgt.set_car_options(gblcar=True) # setting gblcar option

catgt.set_options({'t_miss_ok':True,'no_catgt_fld':True,'gfix':'0.4,0.1,0.02'}) # setting other options

# setting output destination
catgt.set_output(dest=catgt_output_path)

# use dry run to show which command would execute
catgt.dry_run()

# execute CatGt 
catgt.run()

# other settings to add '-prb=0' ,'-prb_fld','-t_miss_ok','-ap','-lf','-apfilter=butter,12,300,9000','-lffilter=butter,12,1,600','-gblcar','-gfix=0.4,0.1,0.02','-dest=...','-no_catgt_fld'
# %% example running supercat to concatenate the data
# Method 1: Manual specification
from purrito import CatGt_wrapper
catgt = CatGt_wrapper(
    catgt_path="/usr/local/bin/CatGt",
    basepath="/data",  # Just a placeholder. Not used for supercat, but required
    run_name="combined", # Just a placeholder. Not used for supercat, but required
    gate=0, # Ignored in supercat
    trigger=0  # Ignored in supercat
)

runs = [
    {'dir': '/data/output', 'run_ga': 'catgt_exp1_g0'},
    {'dir': '/data/output', 'run_ga': 'catgt_exp2_g0'},
    {'dir': '/data/output', 'run_ga': 'catgt_exp3_g0'}
]

catgt.set_supercat(runs, trim_edges=True, dest="/data/final")
catgt.set_filters(ap=True, lf=True)  # Which streams to supercat
catgt.set_input(prb=0)  # Which probes to supercat

# If you used extractors in first pass, specify them again
catgt.set_extraction(xd="2,0,384,6,500")

result = catgt.dry_run()

# Method 2: Using FYI files
fyi_files = [
    "/data/run1/run1_g0_fyi.txt",
    "/data/run2/run2_g0_fyi.txt"
]
runs = CatGt_wrapper.build_supercat_from_fyi_files(fyi_files)
catgt.set_supercat(runs, dest="/data/combined")

# %%
