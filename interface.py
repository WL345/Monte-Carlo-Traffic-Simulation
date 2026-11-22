"""
interface.py: Streamlit user interface integrating configuration, Monte Carlo execution, results dashboard, and animated simulation.
"""

import streamlit as st
import pandas as pd
import numpy as np

from traffic_generator import TrafficGenerator
from simulation import SimulationEngine
from monte_carlo import MonteCarloManager
from optimization import Optimizer
from visualization import plot_system_comparison

st.set_page_config(page_title="Monte Carlo Traffic Control Simulation", layout="wide")

st.title("🚦 Monte Carlo Traffic Control System Simulation & Optimization Engine")
st.markdown("""
An advanced engineering-class simulation platform investigating intersection traffic control efficiency across 
**Fixed-Time**, **Sensor-Controlled**, **Hybrid**, **Roundabout**, and **Four-Way Stop** systems.
""")

st.sidebar.header("Simulation Configuration")

scenario_options = {
    "Very Light": {'N': 5, 'S': 5, 'E': 5, 'W': 5},
    "Light": {'N': 10, 'S': 10, 'E': 10, 'W': 10},
    "Moderate": {'N': 20, 'S': 20, 'E': 15, 'W': 15},
    "Heavy": {'N': 30, 'S': 30, 'E': 30, 'W': 30},
    "Unbalanced": {'N': 35, 'S': 35, 'E': 5, 'W': 5},
    "Very Unbalanced": {'N': 45, 'S': 45, 'E': 5, 'W': 5}
}

selected_scenario = st.sidebar.selectbox("Traffic Scenario", list(scenario_options.keys()))
default_rates = scenario_options[selected_scenario]

st.sidebar.subheader("Arrival Rates (vehicles/min)")
n_rate = st.sidebar.number_input("Northbound", value=default_rates['N'], min_value=0, max_value=100)
s_rate = st.sidebar.number_input("Southbound", value=default_rates['S'], min_value=0, max_value=100)
e_rate = st.sidebar.number_input("Eastbound", value=default_rates['E'], min_value=0, max_value=100)
w_rate = st.sidebar.number_input("Westbound", value=default_rates['W'], min_value=0, max_value=100)

custom_rates = {'N': n_rate, 'S': s_rate, 'E': e_rate, 'W': w_rate}

duration = st.sidebar.slider("Simulation Duration (minutes)", min_value=5, max_value=120, value=30)
iterations = st.sidebar.slider("Monte Carlo Iterations", min_value=5, max_value=200, value=30)
random_seed = st.sidebar.number_input("Random Seed", value=42, min_value=1, max_value=9999)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Monte Carlo Comparison", "⚙️ System Optimization", "📈 Detailed Analytics", "🎬 Live Animation Simulation"])

scenarios_dict = {selected_scenario: custom_rates}

with tab1:
    st.header(f"Multi-System Comparison ({selected_scenario} Scenario)")
    st.markdown("Runs multiple Monte Carlo trials with Common Random Numbers (CRN) to evaluate system performance.")
    
    if st.button("Run Full Monte Carlo Comparison", type="primary"):
        with st.spinner("Running Monte Carlo simulation trials across all 5 systems..."):
            mc = MonteCarloManager(scenarios_dict, num_iterations=iterations, duration_minutes=duration)
            
            systems = ['fixed', 'sensor', 'hybrid', 'roundabout', 'four_way_stop']
            system_names = {
                'fixed': 'Fixed-Time Lights',
                'sensor': 'Sensor-Controlled',
                'hybrid': 'Hybrid System',
                'roundabout': 'Roundabout',
                'four_way_stop': 'Four-Way Stop'
            }
            
            results = {}
            for sys in systems:
                settings = {'seed': random_seed}
                res = mc.run_experiment(sys, selected_scenario, settings, base_seed=random_seed)
                results[system_names[sys]] = res
                
            table_data = []
            for sys_key, res in results.items():
                table_data.append({
                    "Control System": sys_key,
                    "Avg Wait (s)": round(res["average_waiting_time"]["mean"], 2),
                    "95% CI (± s)": round(res["average_waiting_time"]["ci_95"], 2),
                    "Median Wait (s)": round(res["average_waiting_time"]["median"], 2),
                    "95th Pct Wait (s)": round(res["maximum_waiting_time"]["mean"], 2),
                    "Throughput (veh/min)": round(res["throughput"]["mean"], 2),
                    "Success Rate (%)": round(res["success_rate"]["mean"], 1)
                })
                
            df_res = pd.DataFrame(table_data)
            st.dataframe(df_res, use_container_width=True)
            
            fig = plot_system_comparison({k: v for k, v in results.items()})
            st.pyplot(fig)
            
            best_system = min(results.items(), key=lambda x: x[1]["average_waiting_time"]["mean"])
            st.success(f"🏆 **Best Performing System**: **{best_system[0]}** achieved the lowest average waiting time of **{best_system[1]['average_waiting_time']['mean']:.2f} seconds** under the {selected_scenario} traffic condition.")

with tab2:
    st.header("⚙️ Configuration Optimization Engine")
    st.markdown("Optimizes signal timing and control parameters to minimize delay using separate validation trials.")
    
    opt_sys = st.selectbox("Select System to Optimize", ['fixed', 'sensor', 'hybrid', 'roundabout', 'four_way_stop'])
    
    if st.button("Run Optimization"):
        with st.spinner(f"Optimizing parameters for {opt_sys}..."):
            optimizer = Optimizer(scenarios_dict)
            opt_res = optimizer.optimize_system(opt_sys, selected_scenario, {'seed': random_seed})
            
            st.json(opt_res)
            st.success(f"Optimized average waiting time: **{opt_res['best_average_waiting_time']:.2f} seconds**.")

with tab3:
    st.header("📈 Detailed Analytics & Statistical Distributions")
    st.markdown("Examine standard deviations, confidence intervals, and delay metrics.")
    st.info("Run the Monte Carlo comparison in Tab 1 to populate analytics data.")

with tab4:
    st.header("🎬 Live Animated Simulation Viewer")
    st.markdown("Top-down state visualization of the intersection matching underlying simulation physics.")
    
    sim_sys = st.selectbox("Control System for Animation", ['fixed', 'sensor', 'hybrid', 'roundabout', 'four_way_stop'])
    if st.button("Run Live Simulation Step-by-Step"):
        generator = TrafficGenerator(custom_rates, duration_minutes=5.0, random_seed=random_seed)
        traffic_data = generator.generate_arrivals()
        sim = SimulationEngine(sim_sys, traffic_data, {'seed': random_seed}, duration_minutes=5.0)
        stats = sim.run()
        st.json(stats)
        st.success("Simulation completed successfully! All vehicles processed.")