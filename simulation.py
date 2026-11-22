"""
simulation.py: Time-based discrete-event intersection simulation engine.
"""

import numpy as np

from four_way_stop import FourWayStopManager
from intersection import Intersection
from roundabout import RoundaboutManager
from traffic_lights import TrafficLightController


class SimulationEngine:
    def __init__(self, system_type: str, traffic_data: dict, settings: dict, duration_minutes: float):
        self.system_type = system_type
        self.traffic_data = traffic_data
        self.settings = settings
        self.duration_minutes = duration_minutes
        self.max_simulation_time = duration_minutes * 60.0
        
        self.intersection = Intersection()
        self.time = 0.0
        self.dt = 0.5
        
        if system_type in ['fixed', 'sensor', 'hybrid']:
            self.controller = TrafficLightController(system_type, settings)
        elif system_type == 'roundabout':
            self.roundabout = RoundaboutManager(settings)
            self.rng = np.random.default_rng(settings.get('seed', 42))
        elif system_type == 'four_way_stop':
            self.stop_manager = FourWayStopManager(settings)
            
        self.arrival_pointers = {dir_name: 0 for dir_name in traffic_data}
        self.all_vehicles = []
        for q in traffic_data.values():
            self.all_vehicles.extend(q)

    def run(self) -> dict:
        drain_time = 300.0
        max_time = self.max_simulation_time + drain_time
        
        while self.time < max_time:
            for direction, vehicles in self.traffic_data.items():
                ptr = self.arrival_pointers[direction]
                while ptr < len(vehicles) and vehicles[ptr].arrival_time <= self.time:
                    veh = vehicles[ptr]
                    self.intersection.add_vehicle(veh)
                    self.arrival_pointers[direction] += 1
                    ptr += 1
                self.arrival_pointers[direction] = ptr

            total_arrived = sum(self.arrival_pointers.values())
            total_departed = len(self.intersection.departed)
            if total_arrived >= len(self.all_vehicles) and total_departed >= len(self.all_vehicles):
                break

            if self.system_type in ['fixed', 'sensor', 'hybrid']:
                permissions = self.controller.update(self.dt, self.intersection.queues, self.time)
            elif self.system_type == 'roundabout':
                permissions = {'N': False, 'S': False, 'E': False, 'W': False}
                for direction in ['N', 'S', 'E', 'W']:
                    if self.roundabout.can_enter(direction, self.intersection.queues, self.rng):
                        permissions[direction] = True
            elif self.system_type == 'four_way_stop':
                permissions = self.stop_manager.update(self.dt, self.intersection.queues)

            for direction, permitted in permissions.items():
                q = self.intersection.queues[direction]
                if permitted and len(q) > 0:
                    veh = q.pop(0)
                    veh.entry_time = self.time
                    veh.waiting_time = veh.entry_time - veh.arrival_time
                    veh.exit_time = veh.entry_time + 2.0
                    veh.status = 'departed'
                    self.intersection.departed.append(veh)
                    
                    if self.system_type == 'roundabout':
                        self.roundabout.process_entry()

            if self.system_type == 'roundabout' and self.rng.random() < 0.3 * self.dt:
                    self.roundabout.process_exit()

            for direction, q in self.intersection.queues.items():
                for veh in q:
                    veh.waiting_time = self.time - veh.arrival_time

            self.time += self.dt

        return self.calculate_statistics()

    def calculate_statistics(self) -> dict:
        departed_vehicles = self.intersection.departed
        total_generated = len(self.all_vehicles)
        total_processed = len(departed_vehicles)
        waiting_times = [v.waiting_time for v in departed_vehicles]
        unfinished_count = total_generated - total_processed
        
        if len(waiting_times) > 0:
            avg_wait = float(np.mean(waiting_times))
            median_wait = float(np.median(waiting_times))
            p95_wait = float(np.percentile(waiting_times, 95))
            max_wait = float(np.max(waiting_times))
            total_delay = float(np.sum(waiting_times))
        else:
            avg_wait = 0.0
            median_wait = 0.0
            p95_wait = 0.0
            max_wait = 0.0
            total_delay = 0.0
            
        success_rate = (total_processed / total_generated * 100.0) if total_generated > 0 else 100.0
        throughput = total_processed / self.duration_minutes if self.duration_minutes > 0 else 0.0
        
        return {
            "system_type": self.system_type,
            "total_generated": total_generated,
            "total_processed": total_processed,
            "unfinished_vehicles": unfinished_count,
            "average_waiting_time": avg_wait,
            "median_waiting_time": median_wait,
            "p95_waiting_time": p95_wait,
            "maximum_waiting_time": max_wait,
            "total_accumulated_delay": total_delay,
            "success_rate": success_rate,
            "throughput_vehicles_per_min": throughput
        }