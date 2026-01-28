from pathlib import Path

import cv2
import grpc
import grpc_service as grpc_service
import grpcservice_pb2 as grpcservice_pb2
import grpcservice_pb2_grpc as grpcservice_pb2_grpc
import numpy as np

# Specify grpc message length
send_message_length = 10485760
receive_message_length = 10485760

model_uuid = "model_UUID"  # Example uuid

grpc_channel = grpc.insecure_channel(
    "localhost:50051",
    options=[
        ("grpc.max_send_message_length", send_message_length),
        (
            "grpc.max_receive_message_length",
            receive_message_length,
        ),
    ],
)
print("Grpc client created on port 50051")
stub = grpcservice_pb2_grpc.GrpcServiceStub(grpc_channel)


def get_model_info():
    # Retrieve model info from gRPC service
    request = grpcservice_pb2.ModelInfoRequest(model_uuid=model_uuid)
    response = stub.GetModelInfo(request)
    print(response)


def run_infer():
    image_path = str(Path("TEST/data/dogs.jpg"))
    img = cv2.imread(image_path)
    img = cv2.resize(img, (640, 640))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)
    img = img.transpose(0, 3, 1, 2)
    run_request = grpcservice_pb2.RunRequest(
        input=grpc_service.ndarray_to_proto(img), model_uuid=model_uuid
    )
    response = stub.Run(run_request)
    result = grpc_service.proto_to_ndarraylist(response.output)
    print(result)


if __name__ == "__main__":
    get_model_info()
    run_infer()
