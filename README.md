# gRPC Inference service

## Overview

This repository contains a Python-based gRPC inference service used for running image inference with an ONNX model.

The service is designed as a submodule that integrates into a larger system. Image data is sent to the service via gRPC, unpacked on the server, passed through an ONNX model for inference, and the result are returned to the caller. A health check mechanism is included so the main system can detect when the service is unavailable.


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
- Accept and decode image data
- Run inference 
- Expose service health status
- Graceful shutdown


## Integration as a Submodule

This repository is intended to be used as a submodule within a larger system.

Typical integration steps:

1. Add this repository as a submodule
2. Install Python dependencies
  - pip install grpcio
  - pip install grpcio-health-checking
  - pip install protobuf
  - pip install grpcio-tools (for generating files from .proto)
3. Start the gRPC inference server
4. Configure the main system to send inference requests and monitor health

## Generating files 
- To generate files from the .proto file run:  
    ```
    python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. grpcservice.proto
    ```  
- **Warning**: If you do this changes made to solve imports issues will be lost. See file: [grpcservice_pb2_grpc](grpcservice_pb2_grpc.py) for further info.  
  Any changes you make yourself to grpcservice_pb2_grpc.py, grpcservice_pb2.py and grpcservice_pb2.pyi will also be lost.   
    

## Future Improvements

- Extended health diagnostics


## License

Add license information here.
