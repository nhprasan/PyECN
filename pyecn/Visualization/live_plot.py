# -*- coding: utf-8 -*-
"""Lightweight hook for per-step temperature access and live plotting."""
import matplotlib.pyplot as plt
import numpy as np

# Maintains figure state across time steps to avoid recreating plots
_FIGURE_STATE = {}

def on_step(part, step: int) -> None:
    """Capture T_record at each time step and visualize in real-time."""
    # Extract current step temperatures and convert K to °C
    temps = part.T_record[:, step] - 273.15
    outer_ids = getattr(part, "ind0_Geo_surface_4T_4SepFill", [])
    outer_ids = list(outer_ids) if outer_ids is not None else []
    outer_temps = temps[outer_ids] if outer_ids else []
    
    # Skip visualization if no data or not at update interval
    if not outer_ids or step % 10 != 0:
        return
    
    fig_state = _FIGURE_STATE.get(id(part))
    
    # Initialize figure on first call
    if fig_state is None:
        plt.ion()
        
        fig, ax = plt.subplots(figsize=(12, 8))
        heatmap = ax.imshow([[0]], cmap="coolwarm", origin="lower", aspect="auto")
        cbar = fig.colorbar(heatmap, ax=ax)
        cbar.set_label("Temperature (°C)", rotation=270, labelpad=20)
        ax.set_xlabel("an_4T (circumferential index)")
        ax.set_ylabel("ax_4T (axial index)")
        
        _FIGURE_STATE[id(part)] = {
            "fig": fig,
            "ax": ax,
            "heatmap": heatmap,
            "vmin": None,
            "vmax": None,
        }
        fig_state = _FIGURE_STATE[id(part)]
        
        plt.show(block=False)
    
    # Map node IDs to 2D grid coordinates
    ax_vals = np.unique(part.ax_4T[outer_ids])
    an_vals = np.unique(part.an_4T[outer_ids])
    
    ax_index = {val: idx for idx, val in enumerate(ax_vals)}
    an_index = {val: idx for idx, val in enumerate(an_vals)}
    
    # Populate 2D temperature array and track node IDs
    heatmap_data = np.full((ax_vals.size, an_vals.size), np.nan)
    node_map = {}
    for node_id, node_temp in zip(outer_ids, outer_temps):
        row = ax_index[part.ax_4T[node_id]]
        col = an_index[part.an_4T[node_id]]
        heatmap_data[row, col] = node_temp
        node_map[(row, col)] = node_id
    
    # Update heatmap data and coordinate extent
    heatmap = fig_state["heatmap"]
    heatmap.set_data(heatmap_data)
    
    heatmap.set_extent([
        an_vals.min() - 0.5, 
        an_vals.max() + 0.5,
        ax_vals.min() - 0.5, 
        ax_vals.max() + 0.5
    ])
    
    # Configure grid lines at cell boundaries
    ax = fig_state["ax"]
    ax.set_xticks(an_vals)
    ax.set_yticks(ax_vals)
    ax.set_xticks(np.arange(an_vals.min() - 0.5, an_vals.max() + 1.5, 1), minor=True)
    ax.set_yticks(np.arange(ax_vals.min() - 0.5, ax_vals.max() + 1.5, 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=0.5)
    ax.tick_params(which='minor', size=0)
    
    # Remove old annotations before adding new ones
    for txt in ax.texts:
        txt.remove()
    
    # Annotate each cell with node ID and temperature
    for i, ax_val in enumerate(ax_vals):
        for j, an_val in enumerate(an_vals):
            temp_value = heatmap_data[i, j]
            if not np.isnan(temp_value):
                node_id = node_map.get((i, j), -1)
                label_text = f'Node: {node_id}\n{temp_value:.3f}°C'
                ax.text(an_val, ax_val, label_text, 
                       ha='center', va='center', color='black', 
                       fontsize=6, weight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                edgecolor='none', alpha=0.8))
    
    # Track min/max across all time steps for consistent color scaling
    current_min = np.nanmin(heatmap_data)
    current_max = np.nanmax(heatmap_data)
    
    if fig_state["vmin"] is None or fig_state["vmax"] is None:
        fig_state["vmin"] = current_min
        fig_state["vmax"] = current_max
    else:
        fig_state["vmin"] = min(fig_state["vmin"], current_min)
        fig_state["vmax"] = max(fig_state["vmax"], current_max)
    
    heatmap.set_clim(fig_state["vmin"], fig_state["vmax"])
    
    # Update title with current step and temperature range
    fig_state["ax"].set_title(
        f"Outer Surface Temperature (step {step})\n"
        f"Range: {current_min:.3f}°C - {current_max:.3f}°C"
    )
    
    # Force figure refresh for real-time update
    fig_state["fig"].canvas.draw()
    fig_state["fig"].canvas.flush_events()
    plt.pause(0.01)


def cleanup():
    """Call this at the end of simulation to keep figure open."""
    if _FIGURE_STATE:
        plt.ioff()
        plt.show()