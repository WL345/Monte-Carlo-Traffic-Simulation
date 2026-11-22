"""
monte_carlo.py: Monte Carlo experiment manager with Common Random Numbers and confidence intervals.
"""

import numpy as np

from simulation import SimulationEngine
from traffic_generator import TrafficGenerator


class MonteCarloManager:
    def __init__(self, traffic_scenarios: dict, num_iterations: int = 50, duration_minutes: float = 30.0):
        self.traffic_scenarios = traffic_scenarios
        self.num_iterations = num_iterations
        self.duration_minutes = duration_minutes

    def run_experiment(self, system_type: str, scenario_name: str, settings: dict, base_seed: int = 42) -> dict:
        arrival_rates = self.traffic_scenarios[scenario_name]
        
        trial_avg_waits = []
        trial_max_waits = []
        trial_throughputs = []
        trial_success_rates = []
        trial_delays = []
        
        for i in range(self.num_iterations):
            seed = base_seed + i
            generator = TrafficGenerator(arrival_rates, self.duration_minutes, random_seed=seed)
            traffic_data = generator.generate_arrivals()
            
            trial_settings = settings.copy()
            trial_settings['seed'] = seed
            
            sim = SimulationEngine(system_type, traffic_data, trial_settings, self.duration_minutes)
            stats = sim.run()
            
            trial_avg_waits.append(stats["average_waiting_time"])
            trial_max_waits.append(stats["maximum_waiting_time"])
            trial_throughputs.append(stats["throughput_vehicles_per_min"])
            trial_success_rates.append(stats["success_rate"])
            trial_delays.append(stats["total_accumulated_delay"])
            
        def get_stats_summary(data):
            arr = np.array(data)
            mean = float(np.mean(arr))
            std = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
            median = float(np.median(arr))
            ci_95 = 1.96 * (std / np.sqrt(len(arr))) if len(arr) > 1 else 0.0
            return {
                "mean": mean,
                "std": std,
                "median": median,
                "ci_95": ci_95,
                "min": float(np.min(arr)),
                "max": float(np.max(arr))
            }

        return {
            "system_type": system_type,
            "scenario": scenario_name,
            "iterations": self.num_iterations,
            "average_waiting_time": get_stats_summary(trial_avg_waits),
            "maximum_waiting_time": get_stats_summary(trial_max_waits),
            "throughput": get_stats_summary(trial_throughputs),
            "success_rate": get_stats_summary(trial_success_rates),
            "total_delay": get_stats_summary(trial_delays)
        }