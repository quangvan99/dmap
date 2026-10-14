FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    OPENNI2_REDIST=/app/openi_sdk \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        libudev1 \
        libusb-1.0-0 \
        python3 \
        python3-opencv \
        python3-pip \
    && python3 -m pip install --no-cache-dir Pillow primesense \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
