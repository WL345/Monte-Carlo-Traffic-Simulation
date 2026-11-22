"""
traffic_generator.py: Generates vehicle arrivals using Poisson processes / exponential interarrival times
and assigns randomized vehicle attributes.
"""

import numpy as np

from vehicle import Vehicle


class TrafficGenerator:
    def __init__(
        self, arrival_rates: dict, duration_minutes: float, random_seed: int = 42
    ):
        self.arrival_rates = arrival_rates
        self.duration_minutes = duration_minutes
        self.random_seed = random_seed
        self.rng = np.random.default_rng(random_seed)

    def generate_arrivals(self) -> dict:
        """
        Generates vehicles for each direction using exponential interarrival times.
        Returns a dict mapping direction ('N', 'S', 'E', 'W') to a list of Vehicle objects.
        """
        direction_vehicles = {dir_name: [] for dir_name in self.arrival_rates}
        vehicle_id_counter = 1

        for direction, rate_per_min in self.arrival_rates.items():
            if rate_per_min <= 0:
                continue

            rate_per_sec = rate_per_min / 60.0
            current_time = 0.0

            while current_time < self.duration_minutes * 60.0:
                interarrival = self.rng.exponential(1.0 / rate_per_sec)
                current_time += interarrival

                if current_time > self.duration_minutes * 60.0:
                    break

                desired_speed = float(self.rng.normal(12.0, 2.0))
                desired_speed = max(5.0, min(20.0, desired_speed))

                length = float(self.rng.normal(4.5, 0.8))
                length = max(3.5, min(10.0, length))

                reaction_time = float(self.rng.normal(1.0, 0.2))
                reaction_time = max(0.5, min(2.5, reaction_time))

                veh = Vehicle(
                    vehicle_id=vehicle_id_counter,
                    arrival_time=current_time,
                    direction=direction,
                    desired_speed=desired_speed,
                    length=length,
                    reaction_time=reaction_time,
                )
                direction_vehicles[direction].append(veh)
                vehicle_id_counter += 1

        return direction_vehicles
