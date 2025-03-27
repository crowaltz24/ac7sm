from joystick_manager import JoystickManager
import vgamepad as vg
import keyboard
import time
import sys
import atexit

class AceCombatController:
    def __init__(self):
        self.manager = JoystickManager()
        self.running = True
        self.gamepad = vg.VX360Gamepad()
        
        # kill switch key if configured
        self.kill_key = self.manager.config.get('kill_switch', {}).get('key')
        if self.kill_key:
            keyboard.on_press_key(self.kill_key, self.handle_kill_switch)
        
        # get bindings
        self.bindings = self.manager.config.get('bindings', {})
        self.controls = self.manager.config.get('controls', {})
        self.disabled_axes = set()
        self.active_combos = set()
        self.debug = False  # run python ace_combat.py --debug
    
    def handle_kill_switch(self, _):
        print("\nKill switch activated, exiting...")
        self.running = False
    
    def process_axis(self, inputs):
        if self.debug:
            print("\rControls:", end=' ')
            print(f"Roll: {inputs.get('roll', 0):>5.2f}", end=' ')
            print(f"Pitch: {inputs.get('pitch', 0):>5.2f}", end=' ')
            print(f"Yaw: {inputs.get('yaw', 0):>5.2f}", end=' ')
            print(f"Throttle: {inputs.get('throttle', 0):>5.2f}", end=' ')
            print(f"Camera: {inputs.get('hat_x', 0):>4.1f}/{inputs.get('hat_y', 0):<4.1f}", end='')

        # basic
        self.gamepad.left_joystick_float(
            inputs.get('roll', 0), 
            -inputs.get('pitch', 0)
        )
        
        # hat for camera
        self.gamepad.right_joystick_float(
            inputs.get('hat_x', 0),
            inputs.get('hat_y', 0)
        )
        
        # rudder (funny story actually, this took me forever because I totally forgot the rudder is BINARY in this STUPID game)
        rudder = inputs.get('yaw', 0)
        if abs(rudder) > 0.3:
            if rudder > 0:
                self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
            else:
                self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
            self.gamepad.update()
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
            self.gamepad.update()

        # FIXED throttle
        if 'throttle' not in self.disabled_axes:
            throttle = inputs.get('throttle', 0)
            if throttle < 0:
                self.gamepad.right_trigger_float(-throttle)
                self.gamepad.left_trigger_float(0)
            elif throttle > 0:
                self.gamepad.left_trigger_float(throttle)
                self.gamepad.right_trigger_float(0)
            else:
                self.gamepad.right_trigger_float(0)
                self.gamepad.left_trigger_float(0)

        self.process_buttons()
        self.gamepad.update()

    def process_buttons(self):
        standard_buttons = self.bindings.get('standard', {})
        combos = self.bindings.get('combos', {})

        # XUSB button value map
        XUSB_MAP = {
            'XUSB_GAMEPAD_A': 0x1000,
            'XUSB_GAMEPAD_B': 0x2000,
            'XUSB_GAMEPAD_X': 0x4000,
            'XUSB_GAMEPAD_Y': 0x8000,
            'XUSB_GAMEPAD_START': 0x0010,
            'XUSB_GAMEPAD_BACK': 0x0020,
            'XUSB_GAMEPAD_LEFT_THUMB': 0x0040,
            'XUSB_GAMEPAD_RIGHT_THUMB': 0x0080,
            'XUSB_GAMEPAD_LEFT_SHOULDER': 0x0100,
            'XUSB_GAMEPAD_RIGHT_SHOULDER': 0x0200,
        }

        # standard buttons
        for action, binding in standard_buttons.items():
            try:
                xusb_name = binding.get('xusb')
                button_id = binding.get('button')
                if button_id is not None and xusb_name in XUSB_MAP:
                    if self.manager.is_button_pressed(button_id):
                        self.gamepad.press_button(XUSB_MAP[xusb_name])
                    else:
                        self.gamepad.release_button(XUSB_MAP[xusb_name])
            except Exception as e:
                print(f"Warning: Invalid button mapping for {action}: {e}")
        
        # combos 
        for combo_name, combo in combos.items():
            try:
                trigger = combo.get('trigger')
                if trigger is not None and self.manager.is_button_pressed(trigger):
                    self.active_combos.add(combo_name)
                    self.disabled_axes.update(combo.get('disable_axes', []))
                    
                    for xusb_name in combo.get('xusb', []):
                        if xusb_name in XUSB_MAP:
                            self.gamepad.press_button(XUSB_MAP[xusb_name])
                    
                    if combo.get('analog'):
                        # both triggers for high-g turn
                        self.gamepad.left_trigger_float(1.0)
                        self.gamepad.right_trigger_float(1.0)
                else:
                    for xusb_name in combo.get('xusb', []):
                        if xusb_name in XUSB_MAP:
                            self.gamepad.release_button(XUSB_MAP[xusb_name])
                    self.active_combos.discard(combo_name)
                    for axis in combo.get('disable_axes', []):
                        self.disabled_axes.discard(axis)
            except Exception as e:
                print(f"Warning: Invalid combo mapping for {combo_name}: {e}")

    def cleanup(self):
        if self.kill_key:
            keyboard.unhook_all()
        # reset v controller
        self.gamepad.reset()
        self.gamepad.update()

def main():
    try:
        controller = AceCombatController()
        kill_button = controller.manager.config.get('kill_switch', {}).get('button')
        
        print("Virtual Xbox controller initialized for Ace Combat 7")
        if kill_button is not None:
            print(f"Joystick kill switch: Button {kill_button}")
        if controller.kill_key is not None:
            print(f"Keyboard kill switch: '{controller.kill_key}' key")
        if kill_button is None and controller.kill_key is None:
            print("No kill switches configured. Use Ctrl+C to exit.")
        
        print("Use --debug flag to show control values")
        if len(sys.argv) > 1 and sys.argv[1] == '--debug':
            controller.debug = True
        
        # cleanup
        atexit.register(controller.cleanup)
        
        while controller.running:
            inputs = controller.manager.get_processed_input()
            controller.process_axis(inputs)
            
            # kill switch check
            if kill_button is not None and controller.manager.is_button_pressed(kill_button):
                print("\nJoystick kill switch activated, exiting...")
                break
                
            time.sleep(0.01)
            
    except RuntimeError as e:
        print(f"Error: {e}")
    finally:
        controller.cleanup()

if __name__ == "__main__":
    main()