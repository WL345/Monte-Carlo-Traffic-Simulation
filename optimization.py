"""
optimization.py: Parameter optimization engine using separate validation trials.
"""

from monte_carlo import MonteCarloManager


class Optimizer:
    def __init__(self, traffic_scenarios: dict):
        self.traffic_scenarios = traffic_scenarios

    def optimize_system(self, system_type: str, scenario_name: str, base_settings: dict) -> dict:
        # Use a balanced iteration count for optimization search
        mc = MonteCarloManager(self.traffic_scenarios, num_iterations=10, duration_minutes=15.0)
        
        best_settings = base_settings.copy()
        best_score = float('inf')
        tested_configurations = []
        
        if system_type == 'fixed':
            cycle_lengths = [40, 60, 80, 100, 120]
            ns_greens = [15, 25, 35, 45, 60]
            
            for cl in cycle_lengths:
                for nsg in ns_greens:
                    if nsg >= cl - 10:
                        continue
                    settings = base_settings.copy()
                    settings['cycle_length'] = cl
                    settings['ns_green'] = nsg
                    settings['ew_green'] = cl - nsg - 6.0
                    
                    res = mc.run_experiment(system_type, scenario_name, settings, base_seed=999)
                    score = res["average_waiting_time"]["mean"]
                    
                    tested_configurations.append({"settings": settings.copy(), "score": score})
                    if score < best_score:
                        best_score = score
                        best_settings = settings.copy()

        elif system_type == 'sensor':
            min_greens = [5, 10, 15]
            max_greens = [30, 50, 70, 90]
            
            for mg in min_greens:
                for mxg in max_greens:
                    if mg >= mxg:
                        continue
                    settings = base_settings.copy()
                    settings['min_green'] = mg
                    settings['max_green'] = mxg
                    
                    res = mc.run_experiment(system_type, scenario_name, settings, base_seed=999)
                    score = res["average_waiting_time"]["mean"]
                    
                    tested_configurations.append({"settings": settings.copy(), "score": score})
                    if score < best_score:
                        best_score = score
                        best_settings = settings.copy()

        elif system_type == 'hybrid':
            responsiveness_levels = [0.5, 1.0, 2.0, 3.0]
            max_greens = [40, 60, 80]
            
            for resp in responsiveness_levels:
                for mxg in max_greens:
                    settings = base_settings.copy()
                    settings['responsiveness'] = resp
                    settings['max_green'] = mxg
                    
                    res = mc.run_experiment(system_type, scenario_name, settings, base_seed=999)
                    score = res["average_waiting_time"]["mean"]
                    
                    tested_configurations.append({"settings": settings.copy(), "score": score})
                    if score < best_score:
                        best_score = score
                        best_settings = settings.copy()

        else:
            best_settings = base_settings.copy()
            res = mc.run_experiment(system_type, scenario_name, best_settings, base_seed=999)
            best_score = res["average_waiting_time"]["mean"]

        return {
            "system_type": system_type,
            "scenario": scenario_name,
            "best_settings": best_settings,
            "best_average_waiting_time": best_score,
            "tested_configurations_count": len(tested_configurations) if tested_configurations else 1
        }