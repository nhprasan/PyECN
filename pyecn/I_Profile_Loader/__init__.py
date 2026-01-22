"""Utilities for preparing external current profiles for PyECN."""

# Import data structures and functions for handling current profile data in electrochemical simulations.
from pyecn.I_Profile_Loader.current_profile import (
    ProfileData,
    build_time_grid,
    interpolate_profile,
    load_current_profile,
    load_profile_csv,
    load_current_profile_with_t_end
)

# Define the public API exposed by this module.
__all__ = [
    "ProfileData",
    "build_time_grid",
    "interpolate_profile",
    "load_current_profile",
    "load_profile_csv",
    "load_current_profile_with_t_end"
]