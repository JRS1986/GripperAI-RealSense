# GripperAI-RealSense

A desktop application that streams an **Intel RealSense D400** depth camera and uses
**Dex-Net 4.0 GQ-CNN** policies (UC Berkeley AUTOLAB) to find the best place to pick up an
object. It finds both:

- a **parallel-jaw grasp**: two contact points, a grasp axis and a quality score `Q`
- a **suction grasp**: one contact point and a quality score `Q`

Both results are drawn onto the depth image so you can compare them.

The project started in 2019 as a Python 2 / TensorFlow 1.3 prototype. In 2026 it was ported to
**Python 3.13, TensorFlow 2.21 and PySide6 (Qt 6)**, and all dependencies were updated. The
original pretrained network weights still load unchanged.

## How it works

```
RealSense D435 ──► dexgripQtUi/main_uic.py (Qt UI)
                    │  depth: temporal + spatial filtering, crop to region of interest,
                    │         convert to meters
                    │  writes gqcnn_jeffbranch_adapted/data/own/{depth_0.npy,color_0.png}
                    ▼
        "find best grip" starts two worker processes (same Python environment):
          examples/policy_both.py          → GQ-CNN parallel-jaw policy  (trained_models/GQ2017Paper-Grasp)
          examples/suction_policy_both.py  → GQ-CNN suction policy       (trained_models/GQ-Suction)
                    │  each prints one result line: "q x1 y1 x2 y2 depth" / "q x y depth"
                    ▼
        the UI parses both results and draws them on the captured depth frame
```

The policies use cross-entropy-method (CEM) sampling over grasp candidates, and each candidate
is scored by the GQ-CNN. Planning takes a few seconds per policy on a laptop CPU.

## Requirements

- **Python 3.13.** TensorFlow 2.21 does not ship Python 3.14 wheels yet.
- One of these platforms:
  - macOS on Apple Silicon (installs `pyrealsense2-macosx`)
  - Linux x86_64
  - Windows x86_64

  On Linux ARM, such as a Jetson or Raspberry Pi, Intel publishes no `pyrealsense2` wheels, so
  you have to [build librealsense from source](https://github.com/IntelRealSense/librealsense).
- An Intel RealSense D400-series camera (developed with a D435) to run the live UI. The policies
  also run on recorded frames without a camera.

## Installation

```bash
./install.sh
```

This creates `.venv` with `python3.13`. It installs the pinned dependencies from
`requirements.txt`, then the two vendored packages (`perception`, `gqcnn`) in editable mode.
To use a specific interpreter, for example from pyenv:

```bash
PYTHON=~/.pyenv/versions/3.13.12/bin/python ./install.sh
```

## Usage

With the camera connected:

```bash
./run.sh
```

The UI shows the color stream (left) and the filtered depth stream (right). The blue rectangle
marks the region that gets evaluated. Mount the camera about 50–60 cm above the objects, looking
straight down.

| Button | Action |
|---|---|
| find and evaluate possible grasp positions | runs the parallel-jaw policy (`examples/policy.py`) |
| find and evaluate possible suction positions | runs the suction policy (`examples/suction_policy.py`) |
| **find best grip** | runs both policies in parallel and draws both results with their `Q` values |

### Without a camera

The policies read the last captured frame from `gqcnn_jeffbranch_adapted/data/own/`. A sample
frame is committed there:

```bash
cd gqcnn_jeffbranch_adapted
../.venv/bin/python examples/policy_both.py          # prints: q x1 y1 x2 y2 depth
../.venv/bin/python examples/suction_policy_both.py  # prints: q x y depth
```

To get a visualization window, set `vis: final_grasp: 1` in the matching config.

### Docker

```bash
docker build -t gripperai-realsense .
```

The image is `linux/amd64`, because Intel publishes `pyrealsense2` Linux wheels only for x86_64.

To run a policy on the sample frame:

```bash
docker run --rm -w /app/gqcnn_jeffbranch_adapted gripperai-realsense python examples/policy_both.py
```

The live UI needs an X server and USB access to the camera. For example, on a Linux host:

```bash
docker run --rm --privileged -v /dev/bus/usb:/dev/bus/usb -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix gripperai-realsense
```

## Configuration

| What | Where |
|---|---|
| Parallel-jaw policy: sampling, CEM iterations, gripper width, crop size | `gqcnn_jeffbranch_adapted/cfg/examples/policy_both.yaml` (`policy.yaml` for the single-policy button) |
| Suction policy and object detection (workspace box, area limits) | `gqcnn_jeffbranch_adapted/cfg/examples/suction_policy_both.yaml` (`suction_policy.yaml`) |
| Camera intrinsics used by the policies | `gqcnn_jeffbranch_adapted/data/own/primesense_overhead_ir.intr` |
| RealSense advanced-mode settings (loaded at startup) | `garnichtsoschlechtesetting.json` |
| Region of interest, depth filters, depth scaling | `videoThread.run()` and `preprocess_gq()` in `dexgripQtUi/main_uic.py` |

Useful parameters:

- `sampling/depth_grad_thresh`: the depth-gradient threshold for edge detection. The configs
  use `0.025`, tuned for the D435. The original Dex-Net PrimeSense images need `0.0025`.
- `sampling/max_num_edge_pixels` (default 5000): antipodal sampling needs memory quadratic in
  the number of edge pixels. Noisy frames (many depth holes) are randomly subsampled to this
  size, so the UI doesn't freeze.
- `metric/gqcnn_model`: the model directory, relative to `gqcnn_jeffbranch_adapted/`.

## Repository layout

```
dexgripQtUi/                                 Qt UI (main_uic.py is the entry point)
  main.py, qt_cv_vidstream.py                early camera-stream prototypes
  *.ui, *.cpp, *.h, dexgripQtUi.pro          Qt Creator sources the UI was designed with
gqcnn_jeffbranch_adapted/                    patched fork of berkeleyautomation/gqcnn
  gqcnn/                                     GQ-CNN network, grasp samplers, policies
  examples/*_policy*.py                      scripts the UI launches
  cfg/examples/                              policy configs used by the UI
  data/own/                                  last captured frame + camera calibration
  tools/, ros_nodes/                         upstream training / ROS tooling (not used by the UI)
perception_exactly_this_is_somehow_required/ patched fork of berkeleyautomation/perception
                                             (image classes, sensor drivers, object detector);
                                             the UI depends on these exact patches
trained_models/                              pretrained GQ-CNN weights (parallel-jaw, suction)
garnichtsoschlechtesetting.json              RealSense camera preset
```

## Known limitations

- **Q scores are not calibrated for this camera.** The networks were trained on synthetic
  depth images. The D435 is noisier than the sensors Dex-Net was built for, and its depth
  holes create false edges. A high `Q` can still be a bad grasp: in
  [`DexNet_Fail_exemplary.png`](DexNet_Fail_exemplary.png) the predicted grasp (Q = 0.986)
  straddles the object rim and the table.
- Only the UI's inference path is tested on the new stack. The training code
  (`sgd_optimizer.py`, `tools/training.py`) and the ROS nodes were ported but not run.
- TensorFlow runs the original TF1 graph code through `tf.compat.v1`, so the checkpoints load
  unchanged. A native TF2/Keras rewrite would be the next step if the networks get retrained.
- `autolab-core` is no longer maintained (last release in 2022). It requires
  `ruamel.yaml < 0.18`, so that version is pinned.
- `preprocess_gq()` normalizes the color image so that it comes out black whenever the frame's
  minimum is 0, so the saved `color_0.png` is usually black. The policies use only depth, so
  this doesn't affect the grasp results.

## Credits and licenses

- UI and integration: Dexter Frueh (2019), Jan R. Seyler.
- `gqcnn` and the trained models: © UC Berkeley AUTOLAB, **non-commercial research and
  education license**. See [`gqcnn_jeffbranch_adapted/LICENSE`](gqcnn_jeffbranch_adapted/LICENSE)
  and the Dex-Net papers ([Dex-Net 2.0](https://arxiv.org/abs/1703.09312),
  [Dex-Net 4.0](https://robotics.sciencemag.org/content/4/26/eaau4984)).
- `perception`: © UC Berkeley AUTOLAB, Apache 2.0. See
  [`perception_exactly_this_is_somehow_required/LICENSE`](perception_exactly_this_is_somehow_required/LICENSE).

The Dex-Net code and model license is non-commercial, so it applies to the project as a whole.
