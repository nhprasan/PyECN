# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
from pathlib import Path


def parse_cli_args() -> argparse.Namespace:
    """Parse command-line arguments for PyECN configuration and overrides.
    
    Returns:
        Parsed argument namespace containing config path and optional overrides
    """
    parser = argparse.ArgumentParser()
    # Accept config as positional argument for convenience
    parser.add_argument("config", nargs="?", help="TOML config file name")
    # Also accept config as named argument to override positional
    parser.add_argument("--config", dest="config_override", help="TOML config file name")
    parser.add_argument("--profile", dest="profile_path", help="External current profile CSV")
    parser.add_argument("--dt", dest="dt", type=float, help="Solver time step (s)")
    parser.add_argument("--t_end", dest="t_end", type=float, help="Simulation end time (s)")
    return parser.parse_args()


def apply_cli_overrides(inputs: dict, args: argparse.Namespace) -> None:
    """Apply command-line argument overrides to configuration dictionary.
    
    Args:
        inputs: Configuration dictionary to modify in-place
        args: Parsed command-line arguments
    """
    if args.profile_path is not None:
        profile_path = Path(args.profile_path)
        # Resolve relative paths by checking current directory first, then fallback to Examples
        if not profile_path.is_absolute():
            candidate = profile_path
            if not candidate.exists():
                fallback = Path("pyecn/Examples/Profiles") / profile_path
                candidate = fallback if fallback.exists() else profile_path
            profile_path = candidate
        inputs["operating_conditions"]["I_ext_fpath"] = str(profile_path)
    
    if args.dt is not None:
        inputs["operating_conditions"]["dt"] = args.dt
    
    if args.t_end is not None:
        inputs["runtime_options"]["t_end"] = args.t_end