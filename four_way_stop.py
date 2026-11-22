"""
four_way_stop.py: Implements Four-Way Stop right-of-way service rules (FIFO).
"""

class FourWayStopManager:
    def __init__(self, settings: dict):
        self.clearance_time = settings.get('clearance_time', 2.5)
        self.current_crossing_vehicle = None
        self.time_in_intersection = 0.0

    def update(self, dt: float, queues: dict) -> dict:
        permissions = {'N': False, 'S': False, 'E': False, 'W': False}
        
        if self.current_crossing_vehicle is not None:
            self.time_in_intersection += dt
            if self.time_in_intersection >= self.clearance_time:
                self.current_crossing_vehicle = None
                self.time_in_intersection = 0.0
                
        if self.current_crossing_vehicle is None:
            oldest_veh = None
            oldest_dir = None
            min_arrival = float('inf')
            
            for direction, q in queues.items():
                if len(q) > 0:
                    veh = q[0]
                    if veh.arrival_time < min_arrival:
                        min_arrival = veh.arrival_time
                        oldest_veh = veh
                        oldest_dir = direction
                        
            if oldest_veh is not None and oldest_dir is not None:
                self.current_crossing_vehicle = oldest_veh
                permissions[oldest_dir] = True
        else:
            permissions[self.current_crossing_vehicle.direction] = True
            
        return permissions