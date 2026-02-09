# gRPC Inference service

## Overview

This repository contains a Python-based gRPC inference service used for running image inference with an ONNX model.

The service is designed as a submodule that integrates into a larger system. Image data is sent to the service via gRPC, unpacked on the server, passed through an ONNX model for inference, and the result are returned to the caller. A health check mechanism is included so the main system can detect when the service is unavailable.

### Quick steps
- Create config file - See instructions further down
- Setup main system
- Run add_grpc_service.sh to install and start service

## Purpose

The purpose of this service is to:

- Encapsulate ONNX image inference behind a gRPC API
- Decouple inference logic from the main application
- Handle image packing and unpacking internally
- Return object detection results
- Provide health status reporting for system monitoring


## gRPC API Overview

### Inference Flow

1. The client sends preprocessed image data via a gRPC request
2. The server unpacks and ONNX inference is run
3. Detected objects are returned via gRPC


### Image Data Handling

- Image data is transmitted as raw bytes
- Packing and unpacking are handled by the service
- Clients do not interact directly with the ONNX runtime


## Health Check

The service exposes a gRPC health check endpoint that reports:

- Whether the server is running or unavailable

The main system uses this endpoint to:

- Detect service downtime
- Prevent inference calls when the service is unavailable


## Service Responsibilities

- Load and manage the ONNX model
- Run inference 
- Provice ONNX model info
- Expose service health status


## Integration as a Submodule

This repository is intended to be used as a submodule within a larger system.

### Prerequisites
#### Model File Structure 
- ONNX models are organized by UUID, with each model stored 
in its own directory. The service uses the UUID to locate and load the correct model at runtime.
- Each folder name must match the model’s UUID
- The ONNX file must reside inside the corresponding UUID folder
```
models/
├── <model_uuid_1>/
│   ├── model.onnx
├── <model_uuid_2>/
    ├── model.onnx
```
### Integration steps
1. Add this repository as a submodule
2. Configure the main system to send inference requests and monitor health (see example_client for an implementation example)
3. Run: 
```
sudo ./add_grpc_service.sh $PWD/__main__.py $USER
```


## Generating files 
- To generate files from the .proto file run:  
    ```
    python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. grpcservice.proto
    ```  
- **Warning**: If you do this changes made to solve imports issues will be lost. See file: [grpcservice_pb2_grpc](grpcservice_pb2_grpc.py) for further info.  
  Any changes you make yourself to grpcservice_pb2_grpc.py, grpcservice_pb2.py and grpcservice_pb2.pyi will also be lost.   
    
## Config file
- Add a config.json in the repo root with the following content (see config_tempalte.json):
```
{
    "model_base_path": "", 
    "service_name": "grpcservice.GrpcService",
    "grpc_service_port" : "",
    "grpc_service_url" : "", 
    "graceful_shutdown_timeout_seconds": 30,
    "max_send_message_length": 10485760, 
    "max_receive_message_length": 10485760
}

```
- The model_base_path is the directory of your model_uuid folders

## Testing
- From project root run: 
```
pytest TEST/test_grpc_ai_service.py
```

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). This is required because the project uses Ultralytics, which is licensed under AGPL-3.0.
See [LICENSE](LICENSE)

### Ultralytics Usage

This project uses Ultralytics (YOLO) for model loading and export.  
Inference at runtime is performed using ONNX Runtime.

### AGPL Network Use Notice

If you run this gRPC service and allow users to interact with it over a network,
you must make the complete corresponding source code of the service available
to those users, as required by Section 13 of the AGPL.

### Model Files

This repository contains `.pt` and `.onnx` model files for testing
and demonstration purposes. Unless otherwise stated, these model files are provided solely as example artifacts for use with this project. They are not intended for production use. Users are responsible for ensuring they have the right to use any model files in their own applications.