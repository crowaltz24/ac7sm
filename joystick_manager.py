import pygame
import json
import math
import time
from typing import Dict, Tuple

class JoystickManager:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        # initialize joystick
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No joystick detected")
            
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        
        self.num_buttons = self.joystick.get_numbuttons()
        self.num_hats = self.joystick.get_numhats()
        
        # load config
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # default if no json
            return {
                'axes': {
                    'x': {'deadzone': 0.1, 'sensitivity': 1.0},
                    'y': {'deadzone': 0.1, 'sensitivity': 1.0},
                    'twist': {'deadzone': 0.2, 'sensitivity': 1.2},
                    'throttle': {'deadzone': 0.05, 'sensitivity': 1}
                },
                'axis_mapping': {
                    'roll': {'source': 'x', 'scale': 1.0},
                    'pitch': {'source': 'y', 'scale': 1.0},
                    'yaw': {'source': 'twist', 'scale': 1.0},
                    'throttle': {'source': 'throttle', 'scale': 1.0}
                }
            }
    
    def apply_deadzone(self, value: float, deadzone: float) -> float:
        if abs(value) < deadzone:
            return 0
        
        # normalization after deadzone
        sign = 1 if value > 0 else -1
        normalized = (abs(value) - deadzone) / (1 - deadzone)
        return sign * normalized
        
    def get_processed_input(self) -> Dict[str, float]:
        pygame.event.pump()
        processed = {}
        raw_axes = {}
        
        # hat values
        if self.num_hats > 0:
            hat = self.joystick.get_hat(0)
            raw_axes['hat_x'] = float(hat[0])
            raw_axes['hat_y'] = float(hat[1])
        
        # processing raw values
        for axis_name, settings in self.config['axes'].items():
            if axis_name.startswith('hat_'):
                continue  # HAT AXES ARE PREPROCESSED
            if isinstance(self.config['axis_mapping'].get(axis_name), int):
                axis_id = self.config['axis_mapping'][axis_name]
            elif isinstance(self.config['axis_mapping'].get(axis_name), dict):
                axis_id = self.config['axis_mapping'][axis_name].get('source', axis_name)
            else:
                continue
                
            try:
                raw_value = self.joystick.get_axis(axis_id)
                value = self.apply_deadzone(raw_value, settings['deadzone'])
                value = value * settings['sensitivity']
                value = max(-1.0, min(1.0, value))
                raw_axes[axis_name] = value
                processed[axis_name] = value
            except Exception as e:
                print(f"Warning: Error processing axis {axis_name}: {e}")
                
        # processes mapped controls
        for control, mapping in self.config['axis_mapping'].items():
            if isinstance(mapping, dict):
                source = mapping.get('source', '')
                if source in raw_axes:
                    processed[control] = raw_axes[source] * mapping.get('scale', 1.0)
        
        return processed

    def is_button_pressed(self, button_id: int) -> bool:
        pygame.event.pump()
        if button_id is None:
            return False
        if not isinstance(button_id, int):
            return False
        if button_id < 0 or button_id >= self.num_buttons:
            return False
        return self.joystick.get_button(button_id)

    def save_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)
