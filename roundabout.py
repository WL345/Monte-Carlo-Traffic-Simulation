"""
roundabout.py: Implements roundabout circulating traffic and gap-acceptance logic.
"""

class RoundaboutManager:
    def __init__(self, settings: dict):
        self.critical_gap = settings.get('critical_gap', 3.0)
        self.follow_up_headway = settings.get('follow_up_headway', 2.0)
        self.circulating_vehicles = 0
        self.max_capacity = settings.get('max_capacity', 15)
        self.service_time = settings.get('service_time', 2.0)

    def can_enter(self, direction: str, queues: dict, rng) -> bool:
        if len(queues[direction]) == 0:
            return False
        if self.circulating_vehicles >= self.max_capacity:
            return False
        congestion_factor = self.circulating_vehicles / float(self.max_capacity)
        acceptance_prob = max(0.1, 1.0 - (congestion_factor * 0.8))
        return rng.random() < acceptance_prob

    def process_entry(self):
        self.circulating_vehicles += 1

    def process_exit(self):
        if self.circulating_vehicles > 0:
            self.circulating_vehicles -= 1