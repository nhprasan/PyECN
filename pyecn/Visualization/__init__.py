# -*- coding: utf-8 -*-
"""Visualization helpers for PyECN."""

# Import live plotting callback for thermal simulation monitoring
from pyecn.Visualization.live_plot import on_step

# Expose hook function as public API
__all__ = ["on_step"]