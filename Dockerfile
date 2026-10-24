# Intel publishes pyrealsense2 Linux wheels for x86_64 only
FROM --platform=linux/amd64 python:3.13-slim

# OpenGL/XCB libraries for OpenCV and the Qt UI, libusb for the RealSense camera
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 libegl1 libfontconfig1 libdbus-1-3 libusb-1.0-0 \
        libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
        libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xinerama0 libxcb-xkb1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir --no-deps \
        -e perception_exactly_this_is_somehow_required -e gqcnn_jeffbranch_adapted

CMD ["python", "dexgripQtUi/main_uic.py"]
