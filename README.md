# Sub_Netron

Sub_Netron is an extension of the Netron model viewer that lets you select nodes—either via double-click or by dragging a selection box (with the Shift key held)—and extract a subgraph from an ONNX model.

## Requirements

Make sure you have Python installed. Then, install the required dependencies by running:

```bash
pip install -r requirements.txt
```

## Running the Program
To launch the full Sub_Netron workflow (Netron interface + backend processing), run:
```bash
python run_subnetron.py <path_to_model.onnx>
```
This will:

* Launch the Netron interface in your browser for model inspection.

* Start the backend validation and extraction script.

## Usage

* Shift + Drag to draw a selection box and select nodes in the graph.

* Click the Reset button to unselect all currently highlighted nodes.

* After pressing Validate&Extract, the tool will send the selected node IDs and model path to the backend for validation and extraction.


## Below is the Netron's README
<div align="center">
<img width="400px" height="100px" src="https://github.com/lutzroeder/netron/raw/main/.github/logo-light.svg#gh-light-mode-only">
<img width="400px" height="100px" src="https://github.com/lutzroeder/netron/raw/main/.github/logo-dark.svg#gh-dark-mode-only">
</div>

Netron is a viewer for neural network, deep learning and machine learning models.

Netron supports ONNX, TensorFlow Lite, Core ML, Keras, Caffe, Darknet, PyTorch, TensorFlow.js, Safetensors and NumPy.

Netron has experimental support for TorchScript, TensorFlow, MXNet, OpenVINO, RKNN, ML.NET, ncnn, MNN, PaddlePaddle, GGUF and scikit-learn.

<p align='center'><a href='https://www.lutzroeder.com/ai'><img src='.github/screenshot.png' width='800'></a></p>

## Install

**macOS**: [**Download**](https://github.com/lutzroeder/netron/releases/latest) the `.dmg` file or run `brew install --cask netron`

**Linux**: [**Download**](https://github.com/lutzroeder/netron/releases/latest) the `.AppImage` file or run `snap install netron`

**Windows**: [**Download**](https://github.com/lutzroeder/netron/releases/latest) the `.exe` installer or run `winget install -s winget netron`

**Browser**: [**Start**](https://netron.app) the browser version.

**Python**: Run `pip install netron` and `netron [FILE]` or `netron.start('[FILE]')`.

## Models

Sample model files to download or open using the browser version:

 * **ONNX**: [squeezenet](https://github.com/onnx/models/raw/main/validated/vision/classification/squeezenet/model/squeezenet1.0-3.onnx) [[open](https://netron.app?url=https://github.com/onnx/models/raw/main/validated/vision/classification/squeezenet/model/squeezenet1.0-3.onnx)]
 * **TensorFlow Lite**: [yamnet](https://huggingface.co/thelou1s/yamnet/resolve/main/lite-model_yamnet_tflite_1.tflite) [[open](https://netron.app?url=https://huggingface.co/thelou1s/yamnet/blob/main/lite-model_yamnet_tflite_1.tflite)]
 * **TensorFlow**: [chessbot](https://github.com/srom/chessbot/raw/master/model/chessbot.pb) [[open](https://netron.app?url=https://github.com/srom/chessbot/raw/master/model/chessbot.pb)]
 * **Keras**: [mobilenet](https://github.com/aio-libs/aiohttp-demos/raw/master/demos/imagetagger/tests/data/mobilenet.h5) [[open](https://netron.app?url=https://github.com/aio-libs/aiohttp-demos/raw/master/demos/imagetagger/tests/data/mobilenet.h5)]
 * **TorchScript**: [traced_online_pred_layer](https://github.com/ApolloAuto/apollo/raw/master/modules/prediction/data/traced_online_pred_layer.pt) [[open](https://netron.app?url=https://github.com/ApolloAuto/apollo/raw/master/modules/prediction/data/traced_online_pred_layer.pt)]
 * **Core ML**: [exermote](https://github.com/Lausbert/Exermote/raw/master/ExermoteInference/ExermoteCoreML/ExermoteCoreML/Model/Exermote.mlmodel) [[open](https://netron.app?url=https://github.com/Lausbert/Exermote/raw/master/ExermoteInference/ExermoteCoreML/ExermoteCoreML/Model/Exermote.mlmodel)]
 * **Darknet**: [yolo](https://github.com/AlexeyAB/darknet/raw/master/cfg/yolo.cfg) [[open](https://netron.app?url=https://github.com/AlexeyAB/darknet/raw/master/cfg/yolo.cfg)]
