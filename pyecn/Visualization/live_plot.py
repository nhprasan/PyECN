# -*- coding: utf-8 -*-
"""Lightweight hook for per-step temperature access and live plotting."""
import matplotlib.pyplot as plt
import numpy as np
import pyecn.parse_inputs as ip

# Maintains figure state across time steps to avoid recreating plots
_FIGURE_STATE = {}

def on_step(part, step: int) -> None:
    """Capture T_record at each time step and visualize in real-time."""
    # Convert temperatures from Kelvin to Celsius for the current step
    temps = part.T_record[:, step] - 273.15
    
    # Get surface node indices - these are the nodes we want to monitor
    outer_ids = getattr(part, "ind0_Geo_surface_4T_4SepFill", [])
    outer_ids = list(outer_ids) if outer_ids is not None else []
    outer_temps = temps[outer_ids] if outer_ids else []
    
    # Only update visualization every 10 steps to reduce overhead
    if not outer_ids or step % 10 != 0:
        return
    
    fig_state = _FIGURE_STATE.get(id(part))
    
    if fig_state is None:
        # First call - set up the figure with two side-by-side plots
        plt.ion()
        
        fig = plt.figure(figsize=(18, 8))
        
        # Left panel: spatial heatmap of surface temperatures
        ax_heat = plt.subplot(1, 2, 1)
        heatmap = ax_heat.imshow([[0]], cmap="coolwarm", origin="lower", aspect="auto")
        cbar = fig.colorbar(heatmap, ax=ax_heat)
        cbar.set_label("Temperature (°C)", rotation=270, labelpad=20)
        ax_heat.set_xlabel("an_4T (circumferential index)")
        ax_heat.set_ylabel("ax_4T (axial index)")
        
        # Right panel: time evolution of surface statistics
        ax_time = plt.subplot(1, 2, 2)
        line_avg, = ax_time.plot([], [], 'b-', linewidth=2, label='Average Surface Temp')
        line_max, = ax_time.plot([], [], 'r-', linewidth=2, label='Maximum Surface Temp')
        ax_time.set_xlabel("Time (s)")
        ax_time.set_ylabel("Temperature (°C)")
        ax_time.set_title("Surface Temperature Evolution")
        ax_time.legend(loc='best')
        ax_time.grid(True, alpha=0.3)
        
        # Store all figure elements and data arrays for future updates
        _FIGURE_STATE[id(part)] = {
            "fig": fig,
            "ax_heat": ax_heat,
            "ax_time": ax_time,
            "heatmap": heatmap,
            "line_avg": line_avg,
            "line_max": line_max,
            "time_data": [],
            "avg_data": [],
            "max_data": [],
        }
        fig_state = _FIGURE_STATE[id(part)]
        
        plt.tight_layout()
        plt.show(block=False)
    
    # Build coordinate mapping from node IDs to 2D grid positions
    ax_vals = np.unique(part.ax_4T[outer_ids])
    an_vals = np.unique(part.an_4T[outer_ids])
    
    ax_index = {val: idx for idx, val in enumerate(ax_vals)}
    an_index = {val: idx for idx, val in enumerate(an_vals)}
    
    # Create 2D array for heatmap and store node IDs for annotation
    heatmap_data = np.full((ax_vals.size, an_vals.size), np.nan)
    node_map = {}
    for node_id, node_temp in zip(outer_ids, outer_temps):
        row = ax_index[part.ax_4T[node_id]]
        col = an_index[part.an_4T[node_id]]
        heatmap_data[row, col] = node_temp
        node_map[(row, col)] = node_id
    
    # Update the heatmap with new temperature data
    heatmap = fig_state["heatmap"]
    heatmap.set_data(heatmap_data)
    
    # Set the coordinate extent so axis labels match actual indices
    heatmap.set_extent([
        an_vals.min() - 0.5, 
        an_vals.max() + 0.5,
        ax_vals.min() - 0.5, 
        ax_vals.max() + 0.5
    ])
    
    # Draw grid lines between cells to clearly separate nodes
    ax_heat = fig_state["ax_heat"]
    ax_heat.set_xticks(an_vals)
    ax_heat.set_yticks(ax_vals)
    ax_heat.set_xticks(np.arange(an_vals.min() - 0.5, ax_vals.max() + 1.5, 1), minor=True)
    ax_heat.set_yticks(np.arange(ax_vals.min() - 0.5, ax_vals.max() + 1.5, 1), minor=True)
    ax_heat.grid(which='minor', color='black', linestyle='-', linewidth=0.5)
    
    # Clear previous text annotations
    for txt in ax_heat.texts:
        txt.remove()
    
    # Label each cell with node ID and temperature value
    for i, ax_val in enumerate(ax_vals):
        for j, an_val in enumerate(an_vals):
            temp_value = heatmap_data[i, j]
            if not np.isnan(temp_value):
                node_id = node_map[(i, j)]
                label_text = f'Node: {node_id}\n{temp_value:.3f}°C'
                ax_heat.text(an_val, ax_val, label_text, 
                       ha='center', va='center', color='black', 
                       fontsize=6, weight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                edgecolor='none', alpha=0.8))
    
    # Lock color scale to 15-80°C range for consistent thermal interpretation
    heatmap.set_clim(15, 80)
    
    current_min = np.nanmin(heatmap_data)
    current_max = np.nanmax(heatmap_data)
    sim_time_s = step * ip.dt
    
    # Update title with current step, simulation time, and temperature range
    ax_heat.set_title(
        f"Outer Surface Temperature (step {step}, t={sim_time_s:.1f}s)\n"
        f"Range: {current_min:.3f}°C - {current_max:.3f}°C"
    )
    
    # Calculate surface-level statistics for time series
    current_time = part.t_record[step]
    current_avg = np.mean(outer_temps)
    current_max_temp = np.max(outer_temps)
    
    fig_state["time_data"].append(current_time)
    fig_state["avg_data"].append(current_avg)
    fig_state["max_data"].append(current_max_temp)
    
    # Update time series lines with accumulated data
    ax_time = fig_state["ax_time"]
    fig_state["line_avg"].set_data(fig_state["time_data"], fig_state["avg_data"])
    fig_state["line_max"].set_data(fig_state["time_data"], fig_state["max_data"])
    
    # Rescale axes to fit all data points
    ax_time.relim()
    ax_time.autoscale_view()
    
    # Readjust layout to prevent title clipping as content changes
    plt.tight_layout()
    
    # Push updates to display
    fig_state["fig"].canvas.draw()
    fig_state["fig"].canvas.flush_events()
    plt.pause(0.01)


def cleanup():
    """Clean up resources and keep final plot visible."""
    _FIGURE_STATE.clear()
    plt.ioff()
    plt.show()