"""
traffic_lights.py: Implements Fixed-Time, Sensor-Controlled, and Hybrid traffic control systems.
"""

class TrafficLightController:
    def __init__(self, system_type: str, settings: dict):
        self.system_type = system_type
        self.settings = settings
        self.current_phase = 0
        self.phase_timer = 0.0
        
        self.cycle_length = settings.get('cycle_length', 60.0)
        self.ns_green = settings.get('ns_green', 25.0)
        self.ew_green = settings.get('ew_green', 25.0)
        self.yellow_time = settings.get('yellow_time', 4.0)
        self.all_red_time = settings.get('all_red_time', 2.0)
        
        self.min_green = settings.get('min_green', 10.0)
        self.max_green = settings.get('max_green', 50.0)
        self.responsiveness = settings.get('responsiveness', 1.0)

    def update(self, dt: float, queues: dict, current_time: float) -> dict:
        self.phase_timer += dt
        
        if self.system_type == 'fixed':
            t1 = self.ns_green
            t2 = t1 + self.yellow_time
            t3 = t2 + self.all_red_time
            t4 = t3 + self.ew_green
            t5 = t4 + self.yellow_time
            total_cycle = t5 + self.all_red_time
            
            cycle_time = self.phase_timer % total_cycle
            
            if cycle_time < t1:
                self.current_phase = 0
            elif cycle_time < t2:
                self.current_phase = 1
            elif cycle_time < t3:
                self.current_phase = 2
            elif cycle_time < t4:
                self.current_phase = 3
            elif cycle_time < t5:
                self.current_phase = 4
            else:
                self.current_phase = 5

        elif self.system_type == 'sensor':
            ns_waiting = len(queues['N']) + len(queues['S']) > 0
            ew_waiting = len(queues['E']) + len(queues['W']) > 0
            
            if self.current_phase == 0:
                if (self.phase_timer >= self.max_green) or (not ns_waiting and ew_waiting and self.phase_timer >= self.min_green):
                    self.current_phase = 1
                    self.phase_timer = 0.0
            elif self.current_phase == 1:
                if self.phase_timer >= self.yellow_time:
                    self.current_phase = 2
                    self.phase_timer = 0.0
            elif self.current_phase == 2:
                if self.phase_timer >= self.all_red_time:
                    self.current_phase = 3
                    self.phase_timer = 0.0
            elif self.current_phase == 3:
                if (self.phase_timer >= self.max_green) or (not ew_waiting and ns_waiting and self.phase_timer >= self.min_green):
                    self.current_phase = 4
                    self.phase_timer = 0.0
            elif self.current_phase == 4:
                if self.phase_timer >= self.yellow_time:
                    self.current_phase = 5
                    self.phase_timer = 0.0
            elif self.current_phase == 5:
                if self.phase_timer >= self.all_red_time:
                    self.current_phase = 0
                    self.phase_timer = 0.0

        elif self.system_type == 'hybrid':
            ns_waiting = len(queues['N']) + len(queues['S'])
            ew_waiting = len(queues['E']) + len(queues['W'])
            
            target_ns = self.ns_green + (ns_waiting - ew_waiting) * self.responsiveness * 1.5
            target_ns = max(self.min_green, min(self.max_green, target_ns))
            
            t1 = target_ns
            t2 = t1 + self.yellow_time
            t3 = t2 + self.all_red_time
            target_ew = self.ew_green + (ew_waiting - ns_waiting) * self.responsiveness * 1.5
            target_ew = max(self.min_green, min(self.max_green, target_ew))
            t4 = t3 + target_ew
            t5 = t4 + self.yellow_time
            total_cycle = t5 + self.all_red_time
            
            cycle_time = self.phase_timer % total_cycle
            
            if cycle_time < t1:
                self.current_phase = 0
            elif cycle_time < t2:
                self.current_phase = 1
            elif cycle_time < t3:
                self.current_phase = 2
            elif cycle_time < t4:
                self.current_phase = 3
            elif cycle_time < t5:
                self.current_phase = 4
            else:
                self.current_phase = 5

        ns_green_active = (self.current_phase == 0)
        ew_green_active = (self.current_phase == 3)
        
        return {
            'N': ns_green_active,
            'S': ns_green_active,
            'E': ew_green_active,
            'W': ew_green_active
        }