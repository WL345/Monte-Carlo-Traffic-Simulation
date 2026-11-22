"""
intersection.py: Manages intersection layout, queues, and vehicle movement constraints.
"""

class Intersection:
    def __init__(self):
        self.queues = {'N': [], 'S': [], 'E': [], 'W': []}
        self.crossing = []
        self.departed = []
        self.time = 0.0

    def add_vehicle(self, vehicle):
        self.queues[vehicle.direction].append(vehicle)
        vehicle.status = 'queued'

    def get_queue_length(self, direction: str) -> int:
        return len(self.queues[direction])

    def get_total_queued(self) -> int:
        return sum(len(q) for q in self.queues.values())