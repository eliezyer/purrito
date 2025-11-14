"""
CatGt wrapper with pipeline-oriented option grouping and execution support.

This design organizes options by processing stage: input → filters → extraction → output
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
        run: str,
        gate: Optional[int] = None,
        trigger: Optional[int] = None,
    ):
        """Initialize CatGt wrapper with executable path and run info."""
        if not catgt_path:
            raise ValueError("catgt_path cannot be empty")
        if not basepath:
            raise ValueError("basepath cannot be empty")
        if not run:
            raise ValueError("run cannot be empty")
            
        self.catgt_path = catgt_path
        self.basepath = os.path.abspath(basepath)
        self.run = run
        self.gate = gate
        self.trigger = trigger
        self.options: Dict[str, Any] = {}
        
    def set_input(
        self,
        prb: Optional[int] = None,
        prb_fld: Optional[int] = None,
        t: Optional[str] = None,
        t_cat: Optional[str] = None,
        **kwargs
    ) -> 'CatGt':
        """
        Set input data selection options.
        
        Parameters
        ----------
        prb : int, optional
            Probe index to process (e.g., 0, 1, 2)
        prb_fld : int, optional
            Probe folder organization level
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
        >>> catgt.set_input(prb=0, prb_fld=1, t="0,100")
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
    
    def set_filters(
        self,
        ap: Optional[bool] = None,
        lf: Optional[bool] = None,
        ni: Optional[bool] = None,
        loccar: Optional[int] = None,
        gblcar: Optional[bool] = None,
        gfix: Optional[float] = None,
        tshift: Optional[int] = None,
        **kwargs
    ) -> 'CatGt':
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
            **kwargs
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
    ) -> 'CatGt':
        """
        Set channel extraction options (which channels to keep in output).
        
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
        apfilter: Optional[str] = None,
        lffilter: Optional[str] = None,
        **kwargs
    ) -> 'CatGt':
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
        apfilter : str, optional
            Path to AP filter configuration file
        lffilter : str, optional
            Path to LF filter configuration file
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
            'apfilter': apfilter,
            'lffilter': lffilter,
            **kwargs
        }
        self._update_options(params)
        return self
    
    def set_option(self, key: str, value: Any) -> 'CatGt':
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
    
    def set_options(self, **kwargs) -> 'CatGt':
        """
        Set multiple arbitrary options at once.
        
        Parameters
        ----------
        **kwargs
            Key-value pairs of options
            
        Returns
        -------
        CatGt
            Returns self for method chaining
        """
        self._update_options(kwargs)
        return self
    
    def _update_options(self, params: Dict[str, Any]) -> None:
        """Update options dictionary, filtering out None values."""
        for key, value in params.items():
            if value is not None:
                self.options[key] = value
    
    def remove_option(self, key: str) -> 'CatGt':
        """Remove an option by key."""
        self.options.pop(key, None)
        return self
    
    def clear_options(self) -> 'CatGt':
        """Clear all options while keeping base configuration."""
        self.options.clear()
        return self
        
    def build_command(self) -> str:
        """
        Build the CatGt command line string.
            
        Returns
        -------
        str
            The complete command line string for CatGt
            
        Examples
        --------
        >>> catgt = CatGt("/usr/local/bin/CatGt", "/data", "g0", gate=0, trigger=0)
        >>> catgt.set_filters(ap=True, loccar=2)
        >>> cmd = catgt.build_command()
        >>> print(cmd)
        /usr/local/bin/CatGt -dir=/data -run=g0 -g=0 -t=0 -ap -loccar=2
        """
        cmd_parts = [self.catgt_path]
        
        # Add required directory parameter
        cmd_parts.append(f"-dir={self.basepath}")
        
        # Add run parameter
        cmd_parts.append(f"-run={self.run}")
        
        # Add gate if specified
        if self.gate is not None:
            cmd_parts.append(f"-g={self.gate}")
            
        # Add trigger if specified
        if self.trigger is not None:
            cmd_parts.append(f"-t={self.trigger}")
        
        # Add additional options
        cmd_parts.extend(self._format_options())
        
        return " ".join(cmd_parts)
    
    def _format_options(self) -> List[str]:
        """Format additional options as command line arguments."""
        formatted = []
        
        for key, value in self.options.items():
            # Convert Python naming convention to CatGt naming
            option_name = key.replace("_", "-")
            
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
        args.append(f"-run={self.run}")
        
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
        cmd = self.build_command()
        print(f"Would execute: {cmd}")
        return cmd
    
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
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'CatGt':
        """
        Create a CatGt instance from a dictionary.
        
        Parameters
        ----------
        config : Dict[str, Any]
            Configuration dictionary (from to_dict())
            
        Returns
        -------
        CatGt
            New CatGt instance
        """
        instance = cls(
            catgt_path=config['catgt_path'],
            basepath=config['basepath'],
            run=config['run'],
            gate=config.get('gate'),
            trigger=config.get('trigger'),
        )
        instance.options = config.get('options', {}).copy()
        return instance
    
    def __repr__(self) -> str:
        """Return a string representation of the CatGt instance."""
        return (
            f"CatGt(catgt_path='{self.catgt_path}', "
            f"basepath='{self.basepath}', run='{self.run}', "
            f"gate={self.gate}, trigger={self.trigger}, "
            f"options={self.options})"
        )
    
    def __str__(self) -> str:
        """Return the command string when converting to string."""
        return self.build_command()


# Example usage
if __name__ == "__main__":
    # Example 1: Basic usage with execution
    catgt = CatGt(
        catgt_path="/usr/local/bin/CatGt",
        basepath="/data/neuropixels",
        run="g0",
        gate=0,
        trigger=0
    )
    
    # Configure processing pipeline
    catgt.set_input(prb=0, prb_fld=1)
    catgt.set_filters(ap=True, lf=True, loccar=2)
    catgt.set_output(dest="/data/processed")
    
    # Dry run to check command
    catgt.dry_run()
    
    # Execute
    # result = catgt.run()
    # print(f"Processing complete with exit code: {result.returncode}")
    
    # Example 2: Async execution
    # process = catgt.run_async()
    # print(f"Started process with PID: {process.pid}")
    # returncode = process.wait()