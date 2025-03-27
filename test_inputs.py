from joystick_manager import JoystickManager
import pygame
import time
import vgamepad as vg

def format_state(num_axes, num_buttons, joystick, inputs):
    state = "\033[H\n"  # reset
    
    # Main controls
    state += "=== Flight Controls ===\n"
    controls = {
        "Roll (X)": inputs.get('x', 0),
        "Pitch (Y)": inputs.get('y', 0),
        "Yaw": inputs.get('yaw', 0),
        "Throttle": inputs.get('throttle', 0)
    }
    for name, value in controls.items():
        marker = "█" * int((value + 1) * 10)
        state += f"{name:>12}: {value:>6.2f} |{marker:21}|\n"
    
    # Active buttons
    state += "\n=== Active Buttons ===\n"
    active = []
    for i in range(num_buttons):
        if joystick.get_button(i):
            active.append(str(i))
    state += "Pressed: " + (" ".join(active) if active else "None") + " "*20 + "\n"
    
    # # all XUSB buttons
    # state += "\n=== XUSB Button Mappings ===\n"
    # for attr in dir(vg.XUSB_BUTTON):
    #     if attr.startswith('XUSB_GAMEPAD_'):
    #         value = getattr(vg.XUSB_BUTTON, attr)
    #         state += f"{attr[13:]:15}: {value:#06x}\n" 
    
    # clear rest of screen
    state += "\033[J"
    
    # Hat switch
    if joystick.get_numhats() > 0:
        hat = joystick.get_hat(0)
        state += f"\n=== Hat Switch ===\n"
        state += f"X/Y: {hat[0]:>3}/{hat[1]:<3} "
        direction = ""
        if hat[1] > 0: direction += "↑"
        if hat[1] < 0: direction += "↓"
        if hat[0] > 0: direction += "→"
        if hat[0] < 0: direction += "←"
        state += direction if direction else "centered"
    
    return state

def main():
    manager = JoystickManager()
    joystick = manager.joystick
    
    # clear screen once at start
    print("\033[2J")  # clear screen
    print("\033[?25l")  # hide cursor
    
    try:
        while True:
            pygame.event.pump()
            inputs = manager.get_processed_input()
            
            state = format_state(
                joystick.get_numaxes(),
                joystick.get_numbuttons(),
                joystick,
                inputs
            )
            
            print(state)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\033[?25h")  # cursor
        print("\nExiting...")

if __name__ == "__main__":
    main()
