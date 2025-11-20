"""
CatGt wrapper with pipeline-oriented option grouping and execution support.

This design organizes options by processing stage: input > filters > extraction > output
"""

import os
import subprocess
from typing import Optional, List, Dict, Any, Union
from pathlib import Path


class CatGt_wrapper:
    """
    A Python wrapper class for CatGt command-line tool with pipeline-oriented option setting.
    
    Parameters
    ----------
    catgt_path : str
        Path to the CatGt executable
    basepath : str
        Base directory path containing the SpikeGLX data
    run : str
        Run name (e.g., "D1R_CRE_001_HPC")
    gate : Optional[int], default=None
        Gate index
    trigger : Optional[int], default=None
        Trigger index
    prb_fld : bool, optional
            Whether the probe data is organized in folders
        
    Examples
    --------
    Basic usage:
    >>> catgt = CatGt_wrapper(
    ...     catgt_path="/usr/local/bin/CatGt",
    ...     basepath="/path/to/data",
    ...     run="D1R_CRE_001_HPC",
    ...     gate=0,
    ...     trigger=0
    ... )
    >>> catgt.set_filters(ap=True, lf=True, loccar=2)
    >>> catgt.set_extraction(prb=0, prb_fld=1)
    >>> result = catgt.run()
    """
    
    def __init__(
        self,
        catgt_path: str,
        basepath: str,
        run_name: Optional[str] = None,
        gate: Optional[int] = 0,
        trigger: Optional[int] = 0,
        prb_fld: Optional[bool] = None,
        **kwargs
    ):
        """Initialize CatGt wrapper with executable path and run info.

        Backwards-compatible: additional keyword arguments are treated as
        CatGt options and stored in the internal options dict.
        """
        if not catgt_path:
            raise ValueError("catgt_path cannot be empty")
        if not basepath:
            raise ValueError("basepath cannot be empty")
        
        # if run_name was not provided, estimate ast the name of the basepath folder (removing _g0 etc)
        if run_name is None:
            run_name = os.path.basename(os.path.normpath(basepath)).split("_g0")[0]

        self.catgt_path = catgt_path
        self.basepath = os.path.abspath(basepath)
        self.run_name = run_name
        self.gate = gate
        self.trigger = trigger
        self.prb_fld = prb_fld
        self.options: Dict[str, Any] = {}

        # Accept older-style options passed in constructor (e.g., ap=True, prb=0)
        if kwargs:
            self._update_options(kwargs)
        
    def set_input(
        self,
        prb: Optional[int] = None,
        prb_fld: Optional[bool] = None,
        t: Optional[str] = None,
        t_cat: Optional[str] = None,
        **kwargs
    ) -> 'CatGt_wrapper':
        """
        Set input data selection options.
        
        Parameters
        ----------
        prb : int, optional
            Probe index to process (e.g., 0, 1, 2)
        t : str, optional
            Time range for processing (e.g., "0,100" for seconds 0-100)
        t_cat : str, optional
            Time range for concatenation operations
        **kwargs
            Additional input options
            
        Returns
        -------
        CatGt
            Returns self for method chaining
            
        Examples
        --------
        >>> catgt.set_input(prb=0, t="0,100")
        """
        params = {
            'prb': prb,
            'prb_fld': prb_fld,
            't': t,
            't_cat': t_cat,
            **kwargs
        }
        self._update_options(params)
        return self
    
    def set_streams(
        self,
        ap: Optional[bool] = None,
        lf: Optional[bool] = None,
        ni: Optional[bool] = None,
        ob: Optional[bool] = None,
    ) -> 'CatGt_wrapper':
    """ Set streams to process
    Parameters
        ----------
        ap : bool, optional
            Process AP (action potential) band data
        lf : bool, optional
            Process LF (local field potential) band data
        ni : bool, optional
            Process NI (National Instruments) channels
        ob : bool, optional
            Process OB (OneBox) channels
        
        """

        params = {
            'ap': ap,
            'lf': lf,
            'ni': ni,
            'ob': ob,
        }
        self._update_options(params)
        return self
    
    def set_filters(
        self,
        loccar: Optional[int] = None,
        gblcar: Optional[bool] = None,
        gfix: Optional[float] = None,
        tshift: Optional[int] = None,
        apfilter: Optional[str] = None,
        lffilter: Optional[str] = None,
        **kwargs
    ) -> 'CatGt_wrapper':
        """
        Set filtering and signal processing options.
        
        Parameters
        ----------
        ap : bool, optional
            Process AP (action potential) band data
        lf : bool, optional
            Process LF (local field potential) band data
        ni : bool, optional
            Process NI (National Instruments) channels
        loccar : int, optional
            Local common average reference radius (0=disable, 2 or 3=number of neighbors)
        gblcar : bool, optional
            Apply global common average reference across all channels
        gfix : float, optional
            Gain correction threshold for fixing gain errors
        tshift : int, optional
            Time shift correction in samples for synchronization
        apfilter : str, optional
            Custom filter specification for AP band (e.g., butter,12,300,9000)
        lffilter : str, optional
            Custom filter specification for LF band (e.g., butter,12,1,600)
        **kwargs
            Additional filtering options
            
        Returns
        -------
        CatGt
            Returns self for method chaining
            
        Examples
        --------
        Apply local CAR with 2 neighbors to AP band:
        >>> catgt.set_filters(ap=True, loccar=2)
        
        Apply global CAR to both AP and LF:
        >>> catgt.set_filters(ap=True, lf=True, gblcar=True)
        """
        params = {
            'ap': ap,
            'lf': lf,
            'ni': ni,
            'loccar': loccar,
            'gblcar': gblcar,
            'gfix': gfix,
            'tshift': tshift,
            'apfilter': apfilter,
            'lffilter': lffilter,
            **kwargs
        }
        self._update_options(params)
        return self
    
    def set_car_options(
            self,
            gblcar: Optional[bool] = None,
            loccar: Optional[int] = None,
            loccar_um: Optional[float] = None,
            gbldmx: Optional[bool] = None,
    ) -> 'CatGt_wrapper':
        """
        Set common average referencing options.
        
        Parameters
        ----------
        gblcar : bool, optional
            Apply global common average reference across all channels
        loccar : int, optional
            Local common average reference radius (0=disable, 2 or 3=number of neighbors)
        loccar_um : float, optional
            Local CAR radius in micrometers
        gbldmx : bool, optional
            Apply global demultiplexing to output
            
        Returns
        -------
        CatGt
            Returns self for method chaining
            
        Examples
        --------
        Apply local CAR with 2 neighbors:
        >>> catgt.set_car_options(loccar=2)
        
        Apply global CAR:
        >>> catgt.set_car_options(gblcar=True)
        """
        params = {
            'gblcar': gblcar,
            'loccar': loccar,
            'loccar_um': loccar_um,
            'gbldmx': gbldmx,
        }
        self._update_options(params)
        return self
    
    
    def set_extraction(
        self,
        xa: Optional[str] = None,
        xd: Optional[str] = None,
        xia: Optional[str] = None,
        xid: Optional[str] = None,
        **kwargs
    ) -> 'CatGt_wrapper':
        """
        Set extraction options .
        
        Parameters
        ----------
        xa : str, optional
            Analog channel extraction pattern (e.g., "0:10" for channels 0-10)
        xd : str, optional
            Digital channel extraction pattern
        xia : str, optional
            Imec analog channel extraction pattern
        xid : str, optional
            Imec digital channel extraction pattern
        **kwargs
            Additional extraction options
            
        Returns
        -------
        CatGt
            Returns self for method chaining
            
        Examples
        --------
        Extract specific analog channels:
        >>> catgt.set_extraction(xa="0:10,20:30")
        
        Extract Imec analog channels:
        >>> catgt.set_extraction(xia="0:383")
        """
        params = {
            'xa': xa,
            'xd': xd,
            'xia': xia,
            'xid': xid,
            **kwargs
        }
        self._update_options(params)
        return self
    
    def set_output(
        self,
        dest: Optional[str] = None,
        out_prb_fld: Optional[bool] = None,
        gbldmx: Optional[bool] = None,
        **kwargs
    ) -> 'CatGt_wrapper':
        """
        Set output configuration options.
        
        Parameters
        ----------
        dest : str, optional
            Destination directory for processed files (default: input directory)
        out_prb_fld : bool, optional
            Organize output using probe folder structure
        gbldmx : bool, optional
            Apply global demultiplexing to output
        **kwargs
            Additional output options
            
        Returns
        -------
        CatGt
            Returns self for method chaining
            
        Examples
        --------
        >>> catgt.set_output(dest="/data/processed", out_prb_fld=True)
        """
        params = {
            'dest': dest,
            'out_prb_fld': out_prb_fld,
            'gbldmx': gbldmx,
            **kwargs
        }
        self._update_options(params)
        return self
    
    def set_option(self, key: str, value: Any) -> 'CatGt_wrapper':
        """
        Set a single arbitrary option not covered by grouped methods.
        
        Parameters
        ----------
        key : str
            Option name (underscores will be converted to dashes)
        value : Any
            Option value
            
        Returns
        -------
        CatGt
            Returns self for method chaining
        """
        if value is not None:
            self.options[key] = value
        return self
    
    def set_options(self, options: Dict[str, Any]) -> 'CatGt_wrapper':
        """
        Set multiple arbitrary options from a dictionary.

        Parameters
        ----------
        options : dict
            Dictionary of key-value pairs to set as options.

        Returns
        -------
        CatGt_wrapper
            Returns self for method chaining
        """
        if not isinstance(options, dict):
            raise TypeError("options must be a dict")
        # _update_options will ignore None values
        self._update_options(options)
        return self
    
    def _update_options(self, params: Dict[str, Any]) -> None:
        """Update options dictionary, filtering out None values."""
        for key, value in params.items():
            if value is not None:
                self.options[key] = value
    
    def remove_option(self, key: str) -> 'CatGt_wrapper':
        """Remove an option by key."""
        self.options.pop(key, None)
        return self
    
    def clear_options(self) -> 'CatGt_wrapper':
        """Clear all options while keeping base configuration."""
        self.options.clear()
        return self
        
    def build_command(self) -> List[str]:
        """
        Build the CatGt command as a list suitable for subprocess.

        Returns
        -------
        List[str]
            The command and its arguments as a list.

        Notes
        -----
        This method returns a list (e.g. ["CatGt", "-dir=/data", "-run=g0", ...])
        so it is safe to pass directly to subprocess.run(). If you need the
        printable command string, use `dry_run()` which will join the list
        for display purposes.
        """
        # Reuse get_command_args which already returns a list of args
        return self.get_command_args()

    def set_supercat(
        self,
        runs: List[Dict[str, str]],
        trim_edges: bool = False,
        skip_ni_ob_bin: bool = False,
        dest: Optional[str] = None,
        **kwargs
        ) -> 'CatGt_wrapper':
        """
        Set supercat options for concatenating multiple runs.

        Parameters
        ----------
        runs : List[Dict[str, str]]
            List of dictionaries containing 'dir' and 'run_ga' keys for each run to concatenate.
            Each dict should have:
            - 'dir': Parent directory of the run folder
            - 'run_ga': Run name with g-index (e.g., "myrun_g0" or "catgt_myrun_g7")
        trim_edges : bool, optional
            If True, trim trailing edges of files to align streams via sync edges
        skip_ni_ob_bin : bool, optional
            If True, skip processing NI/OB binary files (use when first pass didn't create them)
        dest : str, optional
            Required destination directory for supercat output
        **kwargs
            Additional supercat options
            
        Returns
        -------
        CatGt_wrapper
            Returns self for method chaining
            
        Notes
        -----
        - Supercat requires that first-pass CatGt has been run on all listed runs
        - All runs must have 'tcat' tagged output files
        - The dest parameter is required for supercat operations
        - Extractors used in first pass must be specified again for supercat

        Examples
        --------
        Concatenate two runs:
        >>> catgt = CatGt_wrapper(
        ...     catgt_path="/usr/local/bin/CatGt",
        ...     basepath="/data",  # This will be ignored for supercat
        ...     run_name="combined"  # This will be ignored for supercat
        ... )
        >>> runs = [
        ...     {'dir': '/data/run1', 'run_ga': 'experiment1_g0'},
        ...     {'dir': '/data/run2', 'run_ga': 'experiment2_g0'}
        ... ]
        >>> catgt.set_supercat(runs, trim_edges=True, dest="/data/output")
        >>> catgt.set_filters(ap=True, lf=True)  # Specify which streams to supercat
        >>> result = catgt.run()

        With catgt_ output folders from first pass:
        >>> runs = [
        ...     {'dir': '/data/output', 'run_ga': 'catgt_run1_g0'},
        ...     {'dir': '/data/output', 'run_ga': 'catgt_run2_g0'}
        ... ]
        >>> catgt.set_supercat(runs, dest="/data/final")
        """

        if not runs or not isinstance(runs, list):
            raise ValueError("runs must be a non-empty list of dictionaries")

        if not dest:
            raise ValueError("dest parameter is required for supercat operations")

        # Validate each run entry
        for i, run in enumerate(runs):
            if not isinstance(run, dict):
                raise ValueError(f"Run entry {i} must be a dictionary")
            if 'dir' not in run or 'run_ga' not in run:
                raise ValueError(f"Run entry {i} must contain 'dir' and 'run_ga' keys")

        # Build the supercat string: {dir,run_ga}{dir,run_ga}...
        supercat_elements = [f"{{{run['dir']},{run['run_ga']}}}" for run in runs]
        supercat_str = ''.join(supercat_elements)

        params = {
            'supercat': supercat_str,
            'dest': dest,
        }

        if trim_edges:
            params['supercat_trim_edges'] = True

        if skip_ni_ob_bin:
            params['supercat_skip_ni_ob_bin'] = True

        # Add any additional kwargs
        params.update(kwargs)

        self._update_options(params)
        return self
    
    def _format_options(self) -> List[str]:
        """Format additional options as command line arguments."""
        formatted = []
        
        for key, value in self.options.items():
            # Convert Python naming convention to CatGt naming
            # option_name = key.replace("_", "-")
            option_name = key
            
            if isinstance(value, bool):
                if value:
                    # Boolean flags are just present when True
                    formatted.append(f"-{option_name}")
            elif isinstance(value, (list, tuple)):
                # List values are comma-separated
                formatted.append(f"-{option_name}={','.join(map(str, value))}")
            else:
                # Regular key=value pairs
                formatted.append(f"-{option_name}={value}")
                
        return formatted
    
    def get_command_args(self) -> List[str]:
        """
        Get the command and arguments as a list suitable for subprocess.
            
        Returns
        -------
        List[str]
            List of command and arguments
            
        Examples
        --------
        >>> catgt = CatGt("/usr/local/bin/CatGt", "/data", "g0", gate=0)
        >>> catgt.set_filters(ap=True)
        >>> args = catgt.get_command_args()
        """
        args = [self.catgt_path]
        args.append(f"-dir={self.basepath}")
        args.append(f"-run={self.run_name}")
        
        if self.gate is not None:
            args.append(f"-g={self.gate}")
        if self.trigger is not None:
            args.append(f"-t={self.trigger}")
            
        args.extend(self._format_options())
        
        return args
    
    def run(
        self,
        check: bool = True,
        capture_output: bool = True,
        timeout: Optional[float] = None,
        **subprocess_kwargs
    ) -> subprocess.CompletedProcess:
        """
        Execute the CatGt command using subprocess.
        
        Parameters
        ----------
        check : bool, default=True
            If True, raise CalledProcessError if command returns non-zero exit status
        capture_output : bool, default=True
            If True, capture stdout and stderr
        timeout : float, optional
            Timeout in seconds for the command execution
        **subprocess_kwargs
            Additional keyword arguments passed to subprocess.run()
            
        Returns
        -------
        subprocess.CompletedProcess
            The result of the subprocess execution with returncode, stdout, stderr
            
        Raises
        ------
        subprocess.CalledProcessError
            If check=True and the command returns non-zero exit status
        subprocess.TimeoutExpired
            If timeout is specified and exceeded
        FileNotFoundError
            If the CatGt executable is not found
            
        Examples
        --------
        Basic execution:
        >>> catgt = CatGt("/usr/local/bin/CatGt", "/data", "g0", gate=0)
        >>> catgt.set_filters(ap=True, loccar=2)
        >>> result = catgt.run()
        >>> print(f"Exit code: {result.returncode}")
        >>> print(result.stdout.decode())
        
        With custom timeout:
        >>> result = catgt.run(timeout=300)  # 5 minute timeout
        
        Without output capture (for large outputs):
        >>> result = catgt.run(capture_output=False)
        """
        args = self.get_command_args()
        
        try:
            result = subprocess.run(
                args,
                check=check,
                capture_output=capture_output,
                timeout=timeout,
                **subprocess_kwargs
            )
            return result
            
        except subprocess.CalledProcessError as e:
            error_msg = f"CatGt command failed with exit code {e.returncode}"
            if e.stderr:
                error_msg += f"\nStderr: {e.stderr.decode()}"
            raise subprocess.CalledProcessError(
                e.returncode, e.cmd, e.output, e.stderr
            ) from e
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"CatGt executable not found at: {self.catgt_path}\n"
                f"Please verify the path is correct."
            )
    
    def run_async(
        self,
        **subprocess_kwargs
    ) -> subprocess.Popen:
        """
        Execute the CatGt command asynchronously using subprocess.Popen.
        
        This allows you to start the process and continue with other work,
        checking on it periodically or waiting for completion later.
        
        Parameters
        ----------
        **subprocess_kwargs
            Keyword arguments passed to subprocess.Popen()
            
        Returns
        -------
        subprocess.Popen
            The Popen object for the running process
            
        Examples
        --------
        Start process and wait for completion:
        >>> catgt = CatGt("/usr/local/bin/CatGt", "/data", "g0", gate=0)
        >>> catgt.set_filters(ap=True)
        >>> process = catgt.run_async()
        >>> # Do other work...
        >>> returncode = process.wait()
        
        Monitor progress:
        >>> process = catgt.run_async(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        >>> while process.poll() is None:
        ...     # Process is still running
        ...     time.sleep(1)
        >>> stdout, stderr = process.communicate()
        """
        args = self.get_command_args()
        return subprocess.Popen(args, **subprocess_kwargs)
    
    def dry_run(self) -> str:
        """
        Print the command that would be executed without running it.
        
        Useful for debugging and verifying the command before execution.
        
        Returns
        -------
        str
            The command string that would be executed
            
        Examples
        --------
        >>> catgt = CatGt("/usr/local/bin/CatGt", "/data", "g0", gate=0)
        >>> catgt.set_filters(ap=True, loccar=2)
        >>> print(catgt.dry_run())
        /usr/local/bin/CatGt -dir=/data -run=g0 -g=0 -ap -loccar=2
        """
        # build_command now returns a list suitable for subprocess; join for display
        cmd_list = self.build_command()
        cmd_str = " ".join(cmd_list)
        print(f"Would execute: {cmd_str}")
        return cmd_str
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as a dictionary."""
        return {
            'catgt_path': self.catgt_path,
            'basepath': self.basepath,
            'run': self.run,
            'gate': self.gate,
            'trigger': self.trigger,
            'options': self.options.copy()
        }
    
    def __str__(self) -> str:
        """Return the command string when converting to string.

        Since `build_command` returns a list (for subprocess), join it for
        human-readable output.
        """
        return " ".join(self.build_command())
    
    @staticmethod
    def parse_fyi_supercat_element(fyi_path: str) -> Dict[str, str]:
        """
        Parse a supercat element from a CatGt FYI file.
        
        Parameters
        ----------
        fyi_path : str
            Path to the run_ga_fyi.txt file from a first-pass CatGt run
            
        Returns
        -------
        Dict[str, str]
            Dictionary with 'dir' and 'run_ga' keys suitable for set_supercat()
            
        Examples
        --------
        >>> element = CatGt_wrapper.parse_fyi_supercat_element("/data/run1_g0_fyi.txt")
        >>> runs = [element]
        >>> catgt.set_supercat(runs, dest="/data/output")
        """
        import re
        
        if not os.path.exists(fyi_path):
            raise FileNotFoundError(f"FYI file not found: {fyi_path}")
        
        with open(fyi_path, 'r') as f:
            content = f.read()
        
        # Look for the supercat_element line
        match = re.search(r'supercat_element=\{([^,]+),([^}]+)\}', content)
        if not match:
            raise ValueError(f"No supercat_element found in {fyi_path}")
        
        return {
            'dir': match.group(1),
            'run_ga': match.group(2)
        }

    @staticmethod
    def build_supercat_from_fyi_files(fyi_paths: List[str]) -> List[Dict[str, str]]:
        """
        Build a runs list for supercat from multiple FYI files.
        
        Parameters
        ----------
        fyi_paths : List[str]
            List of paths to FYI files from first-pass CatGt runs
            
        Returns
        -------
        List[Dict[str, str]]
            List of run dictionaries suitable for set_supercat()
            
        Examples
        --------
        >>> fyi_files = [
        ...     "/data/run1/run1_g0_fyi.txt",
        ...     "/data/run2/run2_g0_fyi.txt"
        ... ]
        >>> runs = CatGt_wrapper.build_supercat_from_fyi_files(fyi_files)
        >>> catgt.set_supercat(runs, dest="/data/combined")
        """
        runs = []
        for fyi_path in fyi_paths:
            runs.append(CatGt_wrapper.parse_fyi_supercat_element(fyi_path))
        return runs 

