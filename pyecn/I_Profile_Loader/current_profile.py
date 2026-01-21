"""Utilities for preparing external current profiles for PyECN."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np


@dataclass(frozen=True)
class ProfileData:
    """Container for time-current profile data.
    
    Attributes:
        times_s: Time points in seconds
        currents_a: Current values in amperes (positive=discharge, negative=charge)
    """
    times_s: np.ndarray
    currents_a: np.ndarray


def _parse_float(value: str | None, field_name: str, row_index: int) -> float:
    """Parse a string value to float with detailed error reporting.
    
    Args:
        value: String value to parse
        field_name: Name of the CSV column being parsed
        row_index: Row number for error messages (1-indexed)
    
    Returns:
        Parsed float value
    
    Raises:
        ValueError: If value cannot be converted to float
    """
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Row {row_index}: {field_name} is not numeric: {value}") from exc


def load_profile_csv(path: Path) -> ProfileData:
    """Load and validate a current profile from CSV file.
    
    Expected CSV format:
        - Header row with columns: t_s, I_A
        - t_s: time in seconds (must be monotonically non-decreasing)
        - I_A: current in amperes (positive=discharge, negative=charge)
    
    Args:
        path: Path to CSV file
    
    Returns:
        ProfileData containing validated time and current arrays
    
    Raises:
        FileNotFoundError: If CSV file does not exist
        ValueError: If CSV is malformed, missing required columns, contains
                   non-numeric values, has non-monotonic time, or is empty
    """
    if not path.exists():
        raise FileNotFoundError(f"Profile CSV not found: {path}")

    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row")
        
        # Check for required columns
        required = {"t_s", "I_A"}
        missing = required.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")

        times: List[float] = []
        currents: List[float] = []
        for row_index, row in enumerate(reader, start=2):
            t_value = _parse_float(row.get("t_s"), "t_s", row_index)
            i_value = _parse_float(row.get("I_A"), "I_A", row_index)
            times.append(t_value)
            currents.append(i_value)

    if not times:
        raise ValueError("CSV contains no data rows")

    times_arr = np.asarray(times, dtype=float)
    currents_arr = np.asarray(currents, dtype=float)

    # Check for NaN or infinity values
    if np.any(~np.isfinite(times_arr)) or np.any(~np.isfinite(currents_arr)):
        raise ValueError("CSV contains non-finite numeric values")

    # Verify time monotonicity (allow equal times for piecewise-constant profiles)
    if np.any(np.diff(times_arr) < 0):
        raise ValueError("t_s must be monotonically non-decreasing")

    return ProfileData(times_s=times_arr, currents_a=currents_arr)


def load_current_profile(path: Path, dt: float) -> np.ndarray:
    """Load CSV profile and interpolate to solver time steps.
    
    Reads a current profile from CSV, determines simulation end time from the
    profile data, and returns current values interpolated at uniform time steps.
    
    Args:
        path: Path to CSV profile file
        dt: Time step size in seconds (from solver configuration)
    
    Returns:
        Array of current values at each time step
    
    Raises:
        FileNotFoundError: If profile file does not exist
        ValueError: If profile is invalid or interpolation fails
    """
    profile = load_profile_csv(path)
    t_end = profile.times_s[-1]
    time_grid = build_time_grid(dt, t_end)
    return interpolate_profile(profile, time_grid)


def build_time_grid(dt: float, t_end: float) -> np.ndarray:
    """Generate uniform time grid for solver integration.
    
    Creates an array of time points from 0 to t_end with spacing dt.
    The grid may extend slightly beyond t_end to ensure complete coverage.
    
    Args:
        dt: Time step size in seconds
        t_end: Final time in seconds
    
    Returns:
        Array of time points
    
    Raises:
        ValueError: If dt or t_end are not positive
    """
    if dt <= 0:
        raise ValueError("dt must be positive")
    if t_end <= 0:
        raise ValueError("t_end must be positive")
    steps = int(np.floor(t_end / dt))
    return np.arange(0.0, steps * dt + dt, dt)


def interpolate_profile(profile: ProfileData, time_grid: np.ndarray) -> np.ndarray:
    """Interpolate current profile onto solver time grid.
    
    Uses linear interpolation between profile data points. Handles
    piecewise-constant profiles (duplicate time values) correctly.
    
    Args:
        profile: Profile data containing time and current arrays
        time_grid: Target time points for interpolation
    
    Returns:
        Interpolated current values at each time grid point
    
    Raises:
        ValueError: If time_grid is empty or extends outside profile range
    """
    if time_grid.size == 0:
        raise ValueError("time_grid must not be empty")

    if time_grid[0] < profile.times_s[0]:
        raise ValueError("time_grid starts before profile t_s range")
    if time_grid[-1] > profile.times_s[-1]:
        raise ValueError("time_grid ends after profile t_s range")

    return np.interp(time_grid, profile.times_s, profile.currents_a)