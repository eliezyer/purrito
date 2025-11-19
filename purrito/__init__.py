"""
Purrito - A Python wrapper for CatGt
"""

from .catgt import CatGt_wrapper

# Backwards-compatible public name
CatGt = CatGt_wrapper

__version__ = "0.1.0"
__all__ = ["CatGt", "CatGt_wrapper"]
