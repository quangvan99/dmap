#!/usr/bin/env python3
import os

import cv2
import numpy as np
from primesense import openni2


MAX_DEPTH = 5000
WINDOW_RGB = "RGB - press q or ESC to quit"
WINDOW_DEPTH = "Depth - press q or ESC to quit"
CENTER_COLOR = (0, 255, 255)


def read_rgb_frame(frame):
    raw = bytes(frame.get_buffer_as_uint8())
    expected = frame.width * frame.height * 3
    if len(raw) != expected:
        raise RuntimeError(f"RGB frame không phải RGB24: {len(raw)} bytes")

    rgb = np.frombuffer(raw, dtype=np.uint8).reshape(
        (frame.height, frame.width, 3)
    )
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def read_depth_frame(frame):
    raw = bytes(frame.get_buffer_as_uint16())
    expected = frame.width * frame.height * 2
    if len(raw) != expected:
        raise RuntimeError(f"Depth frame sai kích thước: {len(raw)} bytes")

    depth = np.frombuffer(raw, dtype=np.uint16).reshape(
        (frame.height, frame.width)
    )
    valid = (depth > 0) & (depth < MAX_DEPTH)

    # Hiển thị vật thể gần bằng màu nóng, vật thể xa bằng màu lạnh.
    depth_gray = np.zeros(depth.shape, dtype=np.uint8)
    depth_gray[valid] = (
        255 - (depth[valid].astype(np.uint32) * 255 // MAX_DEPTH)
    ).astype(np.uint8)
    depth_color = cv2.applyColorMap(depth_gray, cv2.COLORMAP_JET)
    depth_color[~valid] = 0

    center_x = frame.width // 2
    center_y = frame.height // 2
    center_depth = int(depth[center_y, center_x])
    center_valid = 0 < center_depth < MAX_DEPTH

    # Đánh dấu pixel đang được đo ở chính giữa ảnh depth.
    cv2.drawMarker(
        depth_color,
        (center_x, center_y),
        CENTER_COLOR,
        cv2.MARKER_CROSS,
        markerSize=24,
        thickness=2,
    )
    if center_valid:
        distance_text = f"Center: {center_depth} mm ({center_depth / 1000:.2f} m)"
    else:
        distance_text = "Center: N/A"
    cv2.putText(
        depth_color,
        distance_text,
        (12, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        CENTER_COLOR,
        2,
        cv2.LINE_AA,
    )
    return depth_color


def main():
    device = color = depth = None
    try:
        sdk = os.getenv("OPENNI2_REDIST", "openi_sdk")
        openni2.initialize(sdk)
        device = openni2.Device.open_any()
        color = device.create_color_stream()
        depth = device.create_depth_stream()
        color.start()
        depth.start()

        # Bỏ qua các frame đầu để camera ổn định trước khi hiển thị.
        for _ in range(10):
            color.read_frame()
            depth.read_frame()

        cv2.namedWindow(WINDOW_RGB, cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow(WINDOW_DEPTH, cv2.WINDOW_AUTOSIZE)
        while True:
            color_frame = color.read_frame()
            depth_frame = depth.read_frame()
            cv2.imshow(WINDOW_RGB, read_rgb_frame(color_frame))
            cv2.imshow(WINDOW_DEPTH, read_depth_frame(depth_frame))

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        try:
            details = str(exc)
        except Exception:
            # Một số OpenNI exception cũ có __str__ lỗi khi camera bận.
            details = "OpenNI trả về lỗi không có nội dung"
        print(f"Lỗi {type(exc).__name__}: {details}", flush=True)
        return 1
    finally:
        cv2.destroyAllWindows()
        for item in (color, depth, device):
            if item is not None:
                try:
                    item.close()
                except Exception:
                    pass
        try:
            openni2.unload()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
