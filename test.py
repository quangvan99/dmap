#!/usr/bin/env python3
import os

from PIL import Image
from primesense import openni2

MAX_DEPTH = 5000
SDK = "openi_sdk"
STOPS = (
    (0.00, (255, 0, 0)),
    (0.25, (255, 255, 0)),
    (0.50, (0, 255, 0)),
    (0.75, (0, 0, 255)),
    (1.00, (0, 0, 0)),
)


def save_rgb(raw, width, height, path):
    if len(raw) != width * height * 3:
        raise RuntimeError(f"RGB frame không phải RGB24: {len(raw)} bytes")
    Image.frombytes("RGB", (width, height), raw).save(path, "JPEG", quality=95)


def depth_to_rgb(raw, width, height):
    if len(raw) != width * height * 2:
        raise RuntimeError(f"Depth frame sai kích thước: {len(raw)} bytes")

    result = bytearray(width * height * 3)
    for i, depth in enumerate(memoryview(raw).cast("H")):
        if not depth or depth >= MAX_DEPTH:
            continue
        value = depth / MAX_DEPTH
        for n in range(len(STOPS) - 1):
            left, c1 = STOPS[n]
            right, c2 = STOPS[n + 1]
            if value < right:
                ratio = (value - left) / (right - left)
                color = tuple(int(c1[k] * (1 - ratio) + c2[k] * ratio)
                              for k in range(3))
                result[i * 3:i * 3 + 3] = bytes(color)
                break
    return bytes(result)


def main():
    device = color = depth = color_frame = depth_frame = None
    error = None
    try:
        sdk = os.getenv("OPENNI2_REDIST") or str(SDK)
        openni2.initialize(sdk)
        device = openni2.Device.open_any()
        color = device.create_color_stream()
        depth = device.create_depth_stream()
        color.start()
        depth.start()

        for _ in range(10):
            color.read_frame()
            depth.read_frame()

        color_frame = color.read_frame()
        depth_frame = depth.read_frame()
        save_rgb(bytes(color_frame.get_buffer_as_uint8()),
                 color_frame.width, color_frame.height, "frame.jpg")
        depth_rgb = depth_to_rgb(bytes(depth_frame.get_buffer_as_uint16()),
                                 depth_frame.width, depth_frame.height)
        save_rgb(depth_rgb, depth_frame.width, depth_frame.height,
                 "frame_depth.jpg")
    except Exception as exc:
        error = exc
    finally:
        for item in (color_frame, depth_frame, color, depth, device):
            if item is not None:
                try:
                    item.close()
                except Exception:
                    pass

    if error:
        print(f"Lỗi: {error}")
        os._exit(1)
    print("Đã lưu frame.jpg và frame_depth.jpg", flush=True)
    os._exit(0)


if __name__ == "__main__":
    main()
