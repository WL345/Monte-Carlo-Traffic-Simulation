"""
tests.py: Automated test suite validating core simulation correctness.
"""

import unittest

from simulation import SimulationEngine
from traffic_generator import TrafficGenerator


class TestTrafficSimulation(unittest.TestCase):
    
    def test_01_no_vehicles_zero_delay(self):
        rates = {'N': 0, 'S': 0, 'E': 0, 'W': 0}
        generator = TrafficGenerator(rates, duration_minutes=10.0, random_seed=42)
        traffic_data = generator.generate_arrivals()
        sim = SimulationEngine('fixed', traffic_data, {}, duration_minutes=10.0)
        stats = sim.run()
        self.assertEqual(stats["total_generated"], 0)
        self.assertEqual(stats["average_waiting_time"], 0.0)

    def test_02_reproducibility(self):
        rates = {'N': 10, 'S': 10, 'E': 10, 'W': 10}
        gen1 = TrafficGenerator(rates, duration_minutes=5.0, random_seed=123)
        data1 = gen1.generate_arrivals()
        gen2 = TrafficGenerator(rates, duration_minutes=5.0, random_seed=123)
        data2 = gen2.generate_arrivals()
        
        self.assertEqual(len(data1['N']), len(data2['N']))
        for v1, v2 in zip(data1['N'], data2['N']):
            self.assertEqual(v1.arrival_time, v2.arrival_time)

    def test_03_simulation_completion(self):
        rates = {'N': 5, 'S': 5, 'E': 5, 'W': 5}
        generator = TrafficGenerator(rates, duration_minutes=2.0, random_seed=42)
        traffic_data = generator.generate_arrivals()
        sim = SimulationEngine('fixed', traffic_data, {}, duration_minutes=2.0)
        stats = sim.run()
        self.assertEqual(stats["total_generated"], stats["total_processed"])

if __name__ == '__main__':
    unittest.main()