"""
vehicle.py: Defines the Vehicle data class for the traffic simulation.
"""

class Vehicle:
    def __init__(self, vehicle_id: int, arrival_time: float, direction: str, 
                 desired_speed: float = 12.0, length: float = 4.5, reaction_time: float = 1.0):
        self.id = vehicle_id
        self.arrival_time = arrival_time
        self.direction = direction  # 'N', 'S', 'E', 'W'
        self.desired_speed = desired_speed
        self.length = length
        self.reaction_time = reaction_time
        
        # State tracking
        self.entry_time = None
        self.exit_time = None
        self.waiting_time = 0.0
        self.queue_position = 0
        self.status = 'queued'  # 'queued', 'crossing', 'departed'

    def to_dict(self):
        return {
            "id": self.id,
            "arrival_time": self.arrival_time,
            "direction": self.direction,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "waiting_time": self.waiting_time,
            "status": self.status
        }