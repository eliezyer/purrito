"""
CatGt wrapper class for generating command line arguments.

CatGt is a command-line tool for preprocessing SpikeGLX data from Neuropixels probes.
This wrapper provides a Pythonic interface to generate CatGt command lines.
"""

import os
from typing import Optional, List, Dict, Any


class CatGt:
    """
    A Python wrapper class for CatGt command-line tool.
    
    This class allows users to specify a base path and various preprocessing options,
    and generates the appropriate command-line string for CatGt.
    
    Parameters
    ----------
    basepath : str
        Base directory path containing the SpikeGLX data
    run : str
        Run name (e.g., "g0", "g0_t0")
    gate : Optional[int], default=None
        Gate index
    trigger : Optional[int], default=None
        Trigger index
    **options : dict
        Additional CatGt options as keyword arguments
        
    Examples
    --------
    >>> catgt = CatGt(
    ...     basepath="/path/to/data",
    ...     run="g0",
    ...     gate=0,
    ...     trigger=0,
    ...     ap=True,
    ...     lf=True
    ... )
    >>> cmd = catgt.build_command()
    """
    
    def __init__(
        self,
        basepath: str,
        run: str,
        gate: Optional[int] = None,
        trigger: Optional[int] = None,
        **options: Any
    ):
        """Initialize CatGt wrapper with basepath and options."""
        self.basepath = os.path.abspath(basepath)
        self.run = run
        self.gate = gate
        self.trigger = trigger
        self.options = options
        
    def build_command(self, catgt_path: str = "CatGt") -> str:
        """
        Build the CatGt command line string.
        
        Parameters
        ----------
        catgt_path : str, default="CatGt"
            Path to the CatGt executable
            
        Returns
        -------
        str
            The complete command line string for CatGt
            
        Examples
        --------
        >>> catgt = CatGt("/data", "g0", gate=0, trigger=0)
        >>> cmd = catgt.build_command()
        >>> print(cmd)
        CatGt -dir=/data -run=g0 -g=0 -t=0
        """
        cmd_parts = [catgt_path]
        
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
        """
        Format additional options as command line arguments.
        
        Returns
        -------
        List[str]
            List of formatted option strings
        """
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
    
    def get_command_args(self, catgt_path: str = "CatGt") -> List[str]:
        """
        Get the command and arguments as a list suitable for subprocess.
        
        Parameters
        ----------
        catgt_path : str, default="CatGt"
            Path to the CatGt executable
            
        Returns
        -------
        List[str]
            List of command and arguments
            
        Examples
        --------
        >>> catgt = CatGt("/data", "g0", gate=0)
        >>> args = catgt.get_command_args()
        >>> # Can be used with subprocess.run(args)
        """
        cmd_string = self.build_command(catgt_path)
        return cmd_string.split()
    
    def __repr__(self) -> str:
        """Return a string representation of the CatGt instance."""
        return (
            f"CatGt(basepath='{self.basepath}', run='{self.run}', "
            f"gate={self.gate}, trigger={self.trigger}, "
            f"options={self.options})"
        )
    
    def __str__(self) -> str:
        """Return the command string when converting to string."""
        return self.build_command()
