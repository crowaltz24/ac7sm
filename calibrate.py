import keyboard
import pygame
import json
import time
from joystick_manager import JoystickManager

def wait_for_button_press(joystick, skip_key='s'):
    pygame.event.clear()
    print(f"(Press '{skip_key}' to skip)")
    
    while True:
        pygame.event.pump()
        
        # skip check
        if keyboard.is_pressed(skip_key):
            time.sleep(0.2)
            return None
            
        # joystick buttons
        for i in range(joystick.get_numbuttons()):
            if joystick.get_button(i):
                while joystick.get_button(i):
                    pygame.event.pump()
                    time.sleep(0.1)
                return i
                
        time.sleep(0.1)

def wait_for_axis_movement(joystick, threshold=0.5):
    pygame.event.clear()
    initial_values = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
    print("Move the desired axis...")
    
    while True:
        pygame.event.pump()
        for i in range(joystick.get_numaxes()):
            current = joystick.get_axis(i)
            if abs(current - initial_values[i]) > threshold:
                # Wait for centerng
                time.sleep(0.5)
                return i
        time.sleep(0.1)

def calibrate_axes(manager):
    print("\nAxis Calibration")
    print("----------------")
    
    axes = ["x (Roll)", "y (Pitch)", "twist (Yaw)", "throttle"]
    axis_map = {}
    
    for axis in axes:
        print(f"\nMove the {axis} axis")
        axis_id = wait_for_axis_movement(manager.joystick)
        axis_map[axis.split()[0]] = axis_id
        print(f"Mapped to axis {axis_id}")
    
    return axis_map

def check_button_conflicts(config):
    button_uses = {}
    conflicts = []
    
    # standard bindings
    for action, binding in config['bindings']['standard'].items():
        button = binding.get('button')
        if button is not None:
            if button in button_uses:
                conflicts.append((button, action, button_uses[button]))
            button_uses[button] = action
    
    # combo triggers
    for combo, details in config['bindings']['combos'].items():
        button = details.get('trigger')
        if button is not None:
            if button in button_uses:
                conflicts.append((button, f"combo:{combo}", button_uses[button]))
            button_uses[button] = f"combo:{combo}"
    
    # kill switch
    kill_button = config['kill_switch'].get('button')
    if kill_button is not None:
        if kill_button in button_uses:
            conflicts.append((kill_button, "kill_switch", button_uses[kill_button]))
        button_uses[kill_button] = "kill_switch"
    
    return conflicts

def check_axis_conflicts(config, axis_map):
    axis_uses = {}
    conflicts = []
    
    for axis_name, axis_id in axis_map.items():
        if axis_id in axis_uses:
            conflicts.append((axis_id, axis_name, axis_uses[axis_id]))
        axis_uses[axis_id] = axis_name
    
    return conflicts

def calibrate_hat(joystick):
    print("\nHat Switch Calibration")
    print("---------------------")
    print("Move the hat switch/POV hat in any direction...")
    
    pygame.event.clear()
    found_hat = False
    
    for i in range(joystick.get_numhats()):
        while not found_hat:
            pygame.event.pump()
            hat = joystick.get_hat(i)
            if hat != (0, 0):
                found_hat = True
                print(f"Hat switch detected at index {i}")
                time.sleep(0.5)
                break
            time.sleep(0.1)
    
    return found_hat

def calibrate():
    manager = JoystickManager()
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("Starting calibration...")
    print("Press 's' to skip any binding")
    
    # Calibrate axes
    print("\nFirst, let's calibrate the axes...")
    axis_map = calibrate_axes(manager)
    for axis_name, axis_id in axis_map.items():
        config['axes'][axis_name] = config['axes'].get(axis_name, {})
        config['axis_mapping'][axis_name] = axis_id
    
    # Calibrate hat switch
    print("\nChecking for hat switch...")
    if calibrate_hat(manager.joystick):
        print("Hat switch will be used for camera control")
    else:
        print("No hat switch detected")
    
    # standard buttons
    print("\nNow, let's map the standard buttons...")
    for action, binding in config['bindings']['standard'].items():
        print(f"\nAction: {action}")
        button_id = wait_for_button_press(manager.joystick)
        if button_id is not None:
            binding['button'] = button_id
            print(f"Mapped to button {button_id}")
    
    # combos
    print("\nNow, let's map the combo trigger buttons...")
    for combo_name, combo in config['bindings']['combos'].items():
        print(f"\nCombo: {combo_name}")
        print("Press the button that will trigger this combo")
        button_id = wait_for_button_press(manager.joystick)
        if button_id is not None:
            combo['trigger'] = button_id
            # matches the trigger
            combo['buttons'] = [button_id]
            print(f"Mapped to button {button_id}")
    
    # Kill switch
    print("\nFinally, set the kill switch button...")
    button_id = wait_for_button_press(manager.joystick)
    if button_id is not None:
        config['kill_switch']['button'] = button_id
        print(f"Mapped to button {button_id}")
    
    print("\nCalibration complete!")
    print("\nConfigured combos:")
    for combo_name, combo in config['bindings']['combos'].items():
        print(f"- {combo_name}: Button {combo['trigger']}")
        if combo.get('disable_axes'):
            print(f"  Disables: {', '.join(combo['disable_axes'])}")
    
    # conflicts
    print("\nChecking for conflicts...")
    button_conflicts = check_button_conflicts(config)
    axis_conflicts = check_axis_conflicts(config, axis_map)
    
    if button_conflicts:
        print("\nWARNING: Found button conflicts:")
        for button, action1, action2 in button_conflicts:
            print(f"Button {button} is used by both '{action1}' and '{action2}'!")
    
    if axis_conflicts:
        print("\nWARNING: Found axis conflicts:")
        for axis_id, axis1, axis2 in axis_conflicts:
            print(f"Axis {axis_id} is used by both '{axis1}' and '{axis2}'!")
    
    if not button_conflicts and not axis_conflicts:
        print("No conflicts found.")
    
    # CONFIG SAVE
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    print("\nConfig saved!\nRun test_inputs.py to test your configuration.\nRun ace_combat.py to start the controller.")

if __name__ == "__main__":
    calibrate()
