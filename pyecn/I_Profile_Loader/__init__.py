"""Utilities for preparing external current profiles for PyECN."""

# Import core data structures and functions for handling current profile data used in electrochemical simulations.
from pyecn.I_Profile_Loader.current_profile import (
    ProfileData,
    build_time_grid,
    interpolate_profile,
    load_current_profile,
    load_profile_csv
)

# Explicitly define the public API of this module. This ensures that only the intended functions and classes are exposed when using 'from module import *'.
__all__ = [
    "ProfileData",
    "build_time_grid",
    "interpolate_profile",
    "load_current_profile",
    "load_profile_csv"
]