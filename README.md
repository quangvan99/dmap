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
python3 test.py
```

Output:

- `frame.jpg`: RGB image.
- `frame_depth.jpg`: false-color depth image from 0 to 5 meters.

Camera: Orbbec Astra USB `2bc5:0401`.

### Docker (Ubuntu 22.04)

Install the USB rule on the host first, then reconnect the camera:

```bash
sudo cp orbbec-usb.rules /etc/udev/rules.d/70-orbbec-astra.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Build the Ubuntu 22.04 image and run `test.py` inside Docker:

```bash
./shell.sh build
./shell.sh start
./shell.sh test
./shell.sh show
```

`start` keeps the container running in the background. `test` enters that
running container and executes `python3 test.py`. `show` opens live RGB and
depth windows on the host desktop. Stop it with:

```bash
./shell.sh stop
```

The container mounts the complete current repository at `/app`, including
`test.py`, `openi_sdk`, and the generated image files. The Compose
configuration also mounts `/dev/bus/usb` and `/run/udev` into the container.
It allows USB character devices (`c 189:*`), so reconnecting the camera does
not require changing a bus/device path in the Compose file. The X11 socket is
also mounted for the OpenCV windows opened by `show`; the service shares the
host IPC namespace so GTK's X11 shared-memory rendering works correctly.
