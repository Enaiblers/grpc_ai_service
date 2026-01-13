# grpc_ai_service



- To generate files from the .proto file run:  
    ```
    python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. grpcservice.proto
    ```  
  **Warning**: If you do this changes made to solve imports issues will be lost. See file: [grpcservice_pb2_grpc](grpcservice_pb2_grpc.py) for further info.  
  Any changes you make yourself to grpcservice_pb2_grpc.py, grpcservice_pb2.py and grpcservice_pb2.pyi will also be lost.   
    

