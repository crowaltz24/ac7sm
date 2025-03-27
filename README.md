# AC7SM - Ace Combat 7 Stick Mapper

A flight stick to virtual controller mapper script designed specifically for Ace Combat 7, which has notoriously poor HOTAS support. This script lets you use your flight stick (tested with Logitech Extreme 3D Pro) properly in the game.

## Features

- Full axis, button and hat switch support
- Configurable deadzones and sensitivities
- Hat switch camera control
- Special control combos like high-g turns
- Controller calibration script and test script
- Real-time input visualization for debugging

## Requirements
Latest version of Python.

Libraries used:
```
pygame
keyboard
vgamepad
```

## Setup

1. Install requirements: 
   ```
   pip install -r requirements.txt
   ```
2. Run calibration: 
   ```
   python calibrate.py
   ```
3. Test your inputs: 
   ```
   python test_inputs.py
   ```
4. Start the controller: 
   ```
   python ace_combat.py
   ```

Use the kill switch key on your keyboard or stick to exit the script.

## Important Notes
Adjust your settings as follows.

### Ace Combat 7 Control Options
- High G Turn Settings: Type A (IMPORTANT)
- Acceleration/Yaw Controls: Type A
- Radar Map/Switch Weapons: Type A
  
Then reconfigure bindings via `calibrate.py` as necessary.

### Disclaimer
This tool has only been tested with:
- Logitech Extreme 3D Pro joystick
- Default button/axis configuration
- Python 3.13
- Windows 11

Other configurations or devices may work but are completely untested. Always test your inputs with `test_inputs.py` after calibration to verify everything is working correctly.

## Configuration

Edit `config.json` to customize:
- Axis deadzones and sensitivities
- Button mappings
- Control combinations
- Kill switch bindings

## Default Controls

- Stick X: Roll
- Stick Y: Pitch
- Twist: Yaw (maps to LB/RB)
- Throttle: Throttle axis
- Hat Switch: Camera control
- Various buttons: Mapped to controller buttons

## Known Issues

- Change view button (RIGHT_THUMB) not working properly
- Does not recognize joystick disconnection

## To Do

- Fix change_view button functionality
- Recognize and account for joystick disconnection
- Add axis curve customization (maybe?)
- Specific support for additional HOTAS devices (Probably not happening)

## Usage Tips

- Recalibrate any time you change your setup
- Use `--debug` flag for real-time input values: `python ace_combat.py --debug`
- Alternatively just use the `test_inputs.py` script provided

## License

MIT