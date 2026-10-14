## Project goal

Capture depth data from the Orbbec Astra, combine it with robot telemetry, and use RTMap to build a map.

## Structure
### Install USB rules

```bash
sudo cp orbbec-usb.rules /etc/udev/rules.d/70-orbbec-astra.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```
Unplug and reconnect the camera.

```bash
python3 -m pip install --user Pillow primesense
```

### Run

```bash
python3 read.py
```

Output:

- `frame.jpg`: RGB image.
- `frame_depth.jpg`: false-color depth image from 0 to 5 meters.

Camera: Orbbec Astra USB `2bc5:0401`.
