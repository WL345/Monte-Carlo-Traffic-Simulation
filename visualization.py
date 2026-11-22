"""
visualization.py: Generates comparison charts with confidence intervals.
"""

import matplotlib.pyplot as plt

def plot_system_comparison(results_dict):
    systems = list(results_dict.keys())
    means = [results_dict[sys]["average_waiting_time"]["mean"] for sys in systems]
    cis = [results_dict[sys]["average_waiting_time"]["ci_95"] for sys in systems]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(systems, means, yerr=cis, capsize=5, color=['#2b5c8f', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
    ax.set_ylabel("Average Waiting Time (seconds)")
    ax.set_title("Intersection Control System Comparison (with 95% CI)")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    return fig