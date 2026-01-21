"""
Grid Simulator - Realistic Microgrid Physics and State Management
Simulates solar, wind, battery, load dynamics with event injection
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
import random

@dataclass
class GridState:
    """Complete grid state representation"""
    # Generation
    solar_generation: float = 0.0  # kW
    wind_generation: float = 0.0   # kW
    
    # Load
    load_demand: float = 0.0       # kW
    
    # Battery
    battery_soc: float = 0.5       # 0-1
    battery_capacity: float = 1000.0  # kWh
    battery_charge_rate: float = 0.0   # kW
    battery_health: float = 1.0    # 0-1
    
    # Grid
    grid_import: float = 0.0       # kW (positive = import, negative = export)
    grid_frequency: float = 50.0   # Hz
    grid_voltage: float = 1.0      # pu (per unit)
    
    # Metrics
    stability_score: float = 1.0   # 0-1
    energy_cost: float = 0.0       # INR
    
    # Weather
    cloud_cover: float = 0.0       # 0-1
    wind_speed: float = 0.0        # m/s
    temperature: float = 25.0      # Celsius
    
    # Time
    time_of_day: float = 12.0      # 0-24 hours
    day_of_year: int = 1           # 1-365


class MicrogridDigitalTwin:
    """
    High-fidelity digital twin of renewable energy microgrid
    
    Simulates all grid components with realistic physics:
    - Solar PV generation with weather effects
    - Wind turbine power curves
    - Battery energy storage system (BESS)
    - Dynamic load profiles
    - Grid frequency and voltage dynamics
    
    This digital twin serves as the training environment for the RL agent
    and demonstration platform for autonomous grid management.
    """
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        self.state = GridState()
        self.time_step = 0
        self.dt = 0.1  # Time step in hours (6 minutes)
        
        # System parameters
        self.solar_capacity = 500.0  # kW
        self.wind_capacity = 300.0   # kW
        self.battery_max_charge_rate = 200.0  # kW
        self.battery_efficiency = 0.95
        
        # Cost parameters (INR per kWh)
        self.grid_import_cost = 7.0
        self.grid_export_price = 4.0
        self.battery_degradation_cost = 0.5
        
        # Reward function weights (configurable for tuning)
        self.reward_weights = {
            'stability': 100,      # Primary objective: grid stability
            'renewable': 20,       # Encourage renewable utilization
            'battery_health': 10,  # Preserve battery lifetime
            'soc_penalty': -50,    # Avoid extreme SOC levels
            'instability_penalty': -100  # Severe penalty for instability
        }
        
        # Grid stability parameters
        self.frequency_nominal = 50.0  # Hz
        self.voltage_nominal = 1.0     # pu
        
        # Event tracking
        self.active_events = []
        self.event_timers = {}
        
        # Safety violation tracking
        self.safety_violations = {
            'frequency_violations': 0,
            'voltage_violations': 0,
            'soc_violations': 0,
            'total_violations': 0
        }
        
        # Initialize state
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize grid state with realistic values"""
        self.state.time_of_day = 12.0  # Noon
        self.state.day_of_year = random.randint(1, 365)
        
        # Initialize weather
        self.state.cloud_cover = random.uniform(0, 0.3)
        self.state.wind_speed = random.uniform(5, 15)
        self.state.temperature = random.uniform(20, 35)
        
        # Initialize generation
        self._update_solar_generation()
        self._update_wind_generation()
        
        # Initialize load
        self._update_load_demand()
        
        # Initialize battery
        self.state.battery_soc = random.uniform(0.4, 0.6)
        self.state.battery_health = 1.0
        
        # Initialize grid
        self.state.grid_frequency = 50.0
        self.state.grid_voltage = 1.0
        
        # Calculate initial metrics
        self._update_stability_score()
        self._calculate_energy_cost()
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool]:
        """
        Execute one simulation step
        
        Args:
            action: [battery_charge, battery_discharge, load_shift, grid_import_control, curtailment]
                   All values normalized 0-1
        
        Returns:
            next_state: State vector
            reward: Reward signal
            done: Episode termination flag
        """
        # Parse action
        battery_charge_cmd = np.clip(action[0], 0, 1)
        battery_discharge_cmd = np.clip(action[1], 0, 1)
        load_shift_cmd = np.clip(action[2], 0, 1)
        grid_import_cmd = np.clip(action[3], 0, 1)
        curtailment_cmd = np.clip(action[4], 0, 1)
        
        # Update time
        self.time_step += 1
        self.state.time_of_day = (self.state.time_of_day + self.dt) % 24
        
        # Update weather and generation
        self._update_weather()
        self._update_solar_generation()
        self._update_wind_generation()
        self._update_load_demand()
        
        # Process events
        self._process_events()
        
        # Calculate available renewable energy
        available_renewable = self.state.solar_generation + self.state.wind_generation
        
        # Apply curtailment
        curtailed_renewable = available_renewable * (1 - curtailment_cmd * 0.5)
        
        # Calculate energy balance
        net_load = self.state.load_demand
        
        # Apply load shifting (reduce load temporarily)
        shifted_load = net_load * (1 - load_shift_cmd * 0.2)
        
        # Battery operations
        battery_power = 0.0
        
        if battery_charge_cmd > 0.5 and self.state.battery_soc < 0.95:
            # Charge battery from excess renewable
            excess_renewable = max(0, curtailed_renewable - shifted_load)
            charge_power = min(
                excess_renewable,
                battery_charge_cmd * self.battery_max_charge_rate,
                (0.95 - self.state.battery_soc) * self.state.battery_capacity / self.dt
            )
            battery_power = -charge_power  # Negative = charging
            
        elif battery_discharge_cmd > 0.5 and self.state.battery_soc > 0.1:
            # Discharge battery to meet load
            deficit = max(0, shifted_load - curtailed_renewable)
            discharge_power = min(
                deficit,
                battery_discharge_cmd * self.battery_max_charge_rate,
                (self.state.battery_soc - 0.1) * self.state.battery_capacity / self.dt
            )
            battery_power = discharge_power  # Positive = discharging
        
        # Update battery SOC
        energy_change = battery_power * self.dt
        if battery_power < 0:  # Charging
            energy_change *= self.battery_efficiency
        else:  # Discharging
            energy_change /= self.battery_efficiency
        
        self.state.battery_soc = np.clip(
            self.state.battery_soc - energy_change / self.state.battery_capacity,
            0.0, 1.0
        )
        self.state.battery_charge_rate = battery_power
        
        # Battery degradation
        self.state.battery_health *= 0.9999  # Slow degradation
        
        # Calculate grid import/export
        grid_balance = shifted_load - curtailed_renewable - battery_power
        
        # Grid import control
        if grid_import_cmd > 0.5:
            self.state.grid_import = grid_balance
        else:
            self.state.grid_import = max(0, grid_balance)  # No export
        
        # Update grid frequency and voltage based on balance
        self._update_grid_dynamics(grid_balance)
        
        # Update stability score
        self._update_stability_score()
        
        # Calculate cost
        self._calculate_energy_cost()
        
        # Calculate reward
        reward = self._calculate_reward()
        
        # Check termination
        done = self._check_termination()
        
        # Get next state vector
        next_state = self.get_state_vector()
        
        return next_state, reward, done
    
    def _update_weather(self):
        """Update weather conditions with realistic dynamics"""
        # Cloud cover - random walk with tendency to clear
        self.state.cloud_cover = np.clip(
            self.state.cloud_cover + np.random.normal(0, 0.05) - 0.01,
            0.0, 1.0
        )
        
        # Wind speed - random walk
        self.state.wind_speed = np.clip(
            self.state.wind_speed + np.random.normal(0, 1.0),
            0.0, 25.0
        )
        
        # Temperature - daily cycle
        hour_angle = (self.state.time_of_day - 14) * np.pi / 12
        daily_temp = 27 + 8 * np.cos(hour_angle)
        self.state.temperature = daily_temp + np.random.normal(0, 1)
    
    def _update_solar_generation(self):
        """Calculate solar generation based on time and weather"""
        # Solar irradiance model
        hour_angle = (self.state.time_of_day - 12) * np.pi / 12
        
        # Daylight hours (6 AM to 6 PM)
        if 6 <= self.state.time_of_day <= 18:
            # Peak at noon
            base_irradiance = np.cos(hour_angle)
            base_irradiance = max(0, base_irradiance)
            
            # Cloud impact
            cloud_factor = 1 - 0.8 * self.state.cloud_cover
            
            # Seasonal variation
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * self.state.day_of_year / 365)
            
            # Temperature derating (solar panels lose efficiency at high temp)
            temp_factor = 1 - 0.004 * max(0, self.state.temperature - 25)
            
            self.state.solar_generation = (
                self.solar_capacity * 
                base_irradiance * 
                cloud_factor * 
                seasonal_factor * 
                temp_factor
            )
        else:
            self.state.solar_generation = 0.0
    
    def _update_wind_generation(self):
        """Calculate wind generation based on wind speed"""
        # Wind power curve (simplified)
        v = self.state.wind_speed
        
        if v < 3:  # Cut-in speed
            power = 0
        elif v < 12:  # Linear region
            power = (v - 3) / 9
        elif v < 25:  # Rated region
            power = 1.0
        else:  # Cut-out
            power = 0
        
        self.state.wind_generation = self.wind_capacity * power
    
    def _update_load_demand(self):
        """Calculate load demand with daily and random variation"""
        # Daily load pattern
        hour = self.state.time_of_day
        
        # Morning peak (7-9 AM)
        morning_peak = 0.3 * np.exp(-((hour - 8)**2) / 2)
        
        # Evening peak (6-10 PM)
        evening_peak = 0.5 * np.exp(-((hour - 20)**2) / 4)
        
        # Base load
        base_load = 0.4
        
        # Weekend/weekday difference
        day_type_factor = 0.9 if self.state.day_of_year % 7 in [0, 6] else 1.0
        
        # Random variation
        random_factor = 1 + np.random.normal(0, 0.1)
        
        load_factor = (base_load + morning_peak + evening_peak) * day_type_factor * random_factor
        
        # Total load (assuming 800 kW peak)
        self.state.load_demand = 800 * np.clip(load_factor, 0.3, 1.0)
    
    def _update_grid_dynamics(self, power_imbalance: float):
        """Update grid frequency and voltage based on power balance"""
        # Frequency deviation proportional to power imbalance
        # Positive imbalance = deficit = frequency drop
        frequency_deviation = -power_imbalance / 1000.0  # Hz
        
        self.state.grid_frequency = np.clip(
            self.frequency_nominal + frequency_deviation,
            49.0, 51.0
        )
        
        # Voltage affected by reactive power (simplified)
        voltage_deviation = -abs(power_imbalance) / 2000.0
        self.state.grid_voltage = np.clip(
            self.voltage_nominal + voltage_deviation,
            0.9, 1.1
        )
    
    def _update_stability_score(self):
        """Calculate grid stability score (0-1) and track violations"""
        # Frequency stability
        freq_deviation = abs(self.state.grid_frequency - 50.0)
        freq_score = max(0, 1 - freq_deviation / 1.0)  # ±1 Hz tolerance
        
        # Track frequency violations
        if freq_deviation > 0.5:  # Beyond normal operating range
            self.safety_violations['frequency_violations'] += 1
            self.safety_violations['total_violations'] += 1
        
        # Voltage stability
        volt_deviation = abs(self.state.grid_voltage - 1.0)
        volt_score = max(0, 1 - volt_deviation / 0.1)  # ±0.1 pu tolerance
        
        # Track voltage violations
        if volt_deviation > 0.05:  # Beyond normal operating range
            self.safety_violations['voltage_violations'] += 1
            self.safety_violations['total_violations'] += 1
        
        # Battery health
        battery_score = self.state.battery_health
        
        # Track SOC violations
        if self.state.battery_soc < 0.1 or self.state.battery_soc > 0.95:
            self.safety_violations['soc_violations'] += 1
            self.safety_violations['total_violations'] += 1
        
        # Supply-demand balance
        total_generation = (
            self.state.solar_generation + 
            self.state.wind_generation + 
            abs(self.state.battery_charge_rate) +
            max(0, self.state.grid_import)
        )
        balance_ratio = min(total_generation / max(self.state.load_demand, 1), 1.0)
        
        # Combined stability score
        self.state.stability_score = (
            0.3 * freq_score +
            0.3 * volt_score +
            0.2 * battery_score +
            0.2 * balance_ratio
        )
    
    def _calculate_energy_cost(self):
        """Calculate energy cost in INR"""
        # Grid import cost
        import_cost = max(0, self.state.grid_import) * self.grid_import_cost * self.dt
        
        # Grid export revenue (negative cost)
        export_revenue = max(0, -self.state.grid_import) * self.grid_export_price * self.dt
        
        # Battery degradation cost
        battery_cost = abs(self.state.battery_charge_rate) * self.battery_degradation_cost * self.dt
        
        # Total cost
        self.state.energy_cost = import_cost - export_revenue + battery_cost
    
    def _calculate_reward(self) -> float:
        """Calculate RL reward signal using configurable weights"""
        # Stability reward (most important)
        stability_reward = self.reward_weights['stability'] * self.state.stability_score
        
        # Cost penalty
        cost_penalty = -self.state.energy_cost
        
        # Renewable utilization bonus
        renewable_generation = self.state.solar_generation + self.state.wind_generation
        renewable_ratio = min(renewable_generation / max(self.state.load_demand, 1), 1.0)
        renewable_bonus = self.reward_weights['renewable'] * renewable_ratio
        
        # Battery health preservation
        battery_bonus = self.reward_weights['battery_health'] * self.state.battery_health
        
        # Penalty for extreme battery SOC
        if self.state.battery_soc < 0.15 or self.state.battery_soc > 0.95:
            soc_penalty = self.reward_weights['soc_penalty']
        else:
            soc_penalty = 0
        
        # Penalty for grid instability
        if self.state.stability_score < 0.7:
            instability_penalty = self.reward_weights['instability_penalty']
        else:
            instability_penalty = 0
        
        # Total reward
        reward = (
            stability_reward +
            cost_penalty +
            renewable_bonus +
            battery_bonus +
            soc_penalty +
            instability_penalty
        )
        
        return reward
    
    def _check_termination(self) -> bool:
        """Check if episode should terminate"""
        # Terminate on severe instability
        if self.state.stability_score < 0.5:
            return True
        
        # Terminate on battery failure
        if self.state.battery_health < 0.5:
            return True
        
        # Terminate on excessive grid frequency deviation
        if abs(self.state.grid_frequency - 50.0) > 2.0:
            return True
        
        # Normal termination after long episode
        if self.time_step > 1000:
            return True
        
        return False
    
    def inject_event(self, event_type: str):
        """Inject stress test events"""
        if event_type == 'cloud_cover':
            self.state.cloud_cover = 0.9
            self.active_events.append('cloud_cover')
            self.event_timers['cloud_cover'] = 10
            
        elif event_type == 'wind_drop':
            self.state.wind_speed = 1.0
            self.active_events.append('wind_drop')
            self.event_timers['wind_drop'] = 15
            
        elif event_type == 'peak_demand':
            self.state.load_demand *= 1.5
            self.active_events.append('peak_demand')
            self.event_timers['peak_demand'] = 20
            
        elif event_type == 'battery_degradation':
            self.state.battery_health *= 0.8
            self.active_events.append('battery_degradation')
            self.event_timers['battery_degradation'] = 5
    
    def _process_events(self):
        """Process active events and timers"""
        expired_events = []
        
        for event in self.active_events:
            if event in self.event_timers:
                self.event_timers[event] -= 1
                
                if self.event_timers[event] <= 0:
                    expired_events.append(event)
        
        # Remove expired events
        for event in expired_events:
            self.active_events.remove(event)
            del self.event_timers[event]
            
            # Reset conditions
            if event == 'cloud_cover':
                self.state.cloud_cover = 0.2
            elif event == 'wind_drop':
                self.state.wind_speed = 10.0
            # Note: peak_demand and battery_degradation don't auto-reset
    
    def get_state_vector(self, forecast_solar: float = None, forecast_wind: float = None, 
                         forecast_load: float = None) -> np.ndarray:
        """
        Get state as numpy array for RL agent
        
        Now includes forecasted values for predictive control!
        This transforms the agent from reactive to predictive.
        
        Args:
            forecast_solar: Predicted solar generation (optional)
            forecast_wind: Predicted wind generation (optional)  
            forecast_load: Predicted load demand (optional)
        
        Returns:
            State vector with current + predicted values (13 dimensions)
        """
        # Current state (10 dimensions)
        current_state = [
            self.state.solar_generation / self.solar_capacity,
            self.state.wind_generation / self.wind_capacity,
            self.state.load_demand / 1000.0,
            self.state.battery_soc,
            self.state.battery_health,
            self.state.grid_import / 1000.0,
            (self.state.grid_frequency - 50.0) / 2.0,
            self.state.grid_voltage - 1.0,
            self.state.cloud_cover,
            self.state.wind_speed / 25.0
        ]
        
        # Forecasted values (3 dimensions) - enables predictive control
        if forecast_solar is not None and forecast_wind is not None and forecast_load is not None:
            forecast_state = [
                forecast_solar / self.solar_capacity,
                forecast_wind / self.wind_capacity,
                forecast_load / 1000.0
            ]
        else:
            # If no forecast available, use current values (reactive mode)
            forecast_state = [
                self.state.solar_generation / self.solar_capacity,
                self.state.wind_generation / self.wind_capacity,
                self.state.load_demand / 1000.0
            ]
        
        return np.array(current_state + forecast_state, dtype=np.float32)
    
    def reset(self):
        """Reset simulator to initial state"""
        self.time_step = 0
        self.active_events = []
        self.event_timers = {}
        self._initialize_state()
        return self.get_state_vector()
