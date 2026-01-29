"""
Contains tests for grpc ai service
"""

import json
import logging
import os
import sys
from concurrent import futures
from pathlib import Path

import cv2
import grpc
import grpc_service as grpc_service
import grpcservice_pb2 as grpcservice_pb2
import grpcservice_pb2_grpc as grpcservice_pb2_grpc
import numpy as np
import pytest
from grpcservice_pb2_grpc import add_GrpcServiceServicer_to_server
from ultralytics import YOLO

logging.basicConfig(
    format=(
        "%(asctime)s [%(levelname)s](%(threadName)-9s %(thread)d) %(name)s: %(message)s"
    ),
    level=logging.DEBUG,
)
log = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(stream_handler)

os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
CONFIG = Path("config.json")
TEMPLATE = Path("config_template.json")

try:
    with open(CONFIG, "r") as f:
        config = json.load(f)
except FileNotFoundError as e:
    log.error(f"config file not found. Error: {e}")
    try:
        with open("config.json", "w") as config_file:
            config_file.write(TEMPLATE.read_text())
        with open("config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        log.error("Failed to create config from template")
        raise e

send_message_length = config["test_send_message_length"]
receive_message_length = config["test_receive_message_length"]

TEST_MODEL_BASE_PATH = Path(os.path.dirname(os.path.realpath(__file__)))


@pytest.fixture(scope="session")
def grpc_server():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=os.cpu_count()),
        options=[
            ("grpc.max_send_message_length", send_message_length),
            ("grpc.max_receive_message_length", receive_message_length),
        ],
    )
    add_GrpcServiceServicer_to_server(
        grpc_service.GrpcService(TEST_MODEL_BASE_PATH), server
    )
    port = server.add_insecure_port("localhost:0")
    server.start()
    log.info(f"gRPC test server started on port {port}")
    yield port

    server.stop(grace=None)


@pytest.fixture(scope="session")
def grpc_client(grpc_server):
    port = grpc_server
    grpc_channel = grpc.insecure_channel(
        f"localhost:{port}",
        options=[
            ("grpc.max_send_message_length", send_message_length),
            (
                "grpc.max_receive_message_length",
                receive_message_length,
            ),
        ],
    )
    log.info(f"Grpc client created on port {port}")
    stub = grpcservice_pb2_grpc.GrpcServiceStub(grpc_channel)
    yield stub


def test_load_models():
    # Generate onnx files
    pt_files = list(TEST_MODEL_BASE_PATH.rglob("*.pt"))
    log.debug(f"Found {len(pt_files)} model files.")
    for model_file in pt_files:
        log.debug(f"Found model file: {model_file} with UUID: {model_file.parent.name}")
        model = YOLO(model_file)
        model.export(opset=16, imgsz=640, format="onnx", half=False)

    handlers = grpc_service.GrpcService.load_model_handlers(TEST_MODEL_BASE_PATH)
    assert len(handlers) != 0


def test_find_model_handler():
    handlers = grpc_service.GrpcService.load_model_handlers(TEST_MODEL_BASE_PATH)
    for uuid in handlers.keys():
        assert grpc_service.GrpcService.find_model_handler(handlers, uuid) is not None


def test_load_model_info(grpc_client):
    stub = grpc_client
    model_uuid = "uuid_2"

    request = grpcservice_pb2.ModelInfoRequest(model_uuid=model_uuid)
    response = stub.GetModelInfo(request)
    assert response.modelAuthor == "Ultralytics"
    assert (
        response.output_names[0] == "output0" and response.output_names[1] == "output1"
    )
    assert response.input_name == "images"


# Test if infer is run
def test_infer(grpc_client):
    stub = grpc_client
    image_path = str(Path("TEST/data/dogs.jpg"))
    img = cv2.imread(image_path)
    img = cv2.resize(img, (640, 640))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)
    img = img.transpose(0, 3, 1, 2)

    uuid_list = get_test_uuids()
    for uuid in uuid_list:
        run_request = grpcservice_pb2.RunRequest(
            input=grpc_service.ndarray_to_proto(img), model_uuid=uuid
        )
        response = stub.Run(run_request)
        result = grpc_service.proto_to_ndarraylist(response.output)
        assert len(result) > 0


def test_proto_to_ndarray():

    # Create a sample ndarray
    original_array = np.random.rand(2, 3).astype(np.float32)

    # Convert to proto
    array_proto = grpcservice_pb2.NDArray(
        shape=original_array.shape,
        dtype=str(original_array.dtype),
        data=original_array.tobytes(),
    )

    # Convert back to ndarray
    converted_array = grpc_service.proto_to_ndarray(array_proto)

    # Check if the original and converted arrays are the same
    assert np.array_equal(original_array, converted_array), "Arrays do not match"


def test_ndarray_to_proto():

    # Create a sample ndarray
    original_array = np.random.rand(4, 5).astype(np.float32)

    # Convert to proto
    array_proto = grpc_service.ndarray_to_proto(original_array)

    # Convert back to ndarray
    converted_array = grpc_service.proto_to_ndarray(array_proto)

    # Check if the original and converted arrays are the same
    assert np.array_equal(original_array, converted_array), "Arrays do not match"


def test_ndarraylist_to_proto():

    # Create a list of sample ndarrays
    original_arrays = [np.random.rand(2, 2).astype(np.float32) for _ in range(3)]

    # Convert to proto
    arraylist_proto = grpc_service.ndarraylist_to_proto(original_arrays)

    # Convert back to list of ndarrays
    converted_arrays = []
    for arr_proto in arraylist_proto.arr:
        converted_arrays.append(
            np.frombuffer(arr_proto.data, dtype=np.dtype(arr_proto.dtype)).reshape(
                arr_proto.shape
            )
        )

    # Check if the original and converted arrays are the same
    for original, converted in zip(original_arrays, converted_arrays):
        assert np.array_equal(original, converted), "Arrays do not match"


def test_proto_to_ndarraylist():

    # Create a list of sample ndarrays
    original_arrays = [np.random.rand(3, 3).astype(np.float32) for _ in range(2)]

    # Convert to proto
    arraylist_proto = grpcservice_pb2.NDArrayList()
    for arr in original_arrays:
        arr_proto = grpcservice_pb2.NDArray(
            shape=arr.shape,
            dtype=str(arr.dtype),
            data=arr.tobytes(),
        )
        arraylist_proto.arr.append(arr_proto)

    # Convert back to list of ndarrays
    converted_arrays = grpc_service.proto_to_ndarraylist(arraylist_proto)

    # Check if the original and converted arrays are the same
    for original, converted in zip(original_arrays, converted_arrays):
        assert np.array_equal(original, converted), "Arrays do not match"


def get_test_uuids():
    pt_files = list(Path("TEST/data/").rglob("*.pt"))
    log.debug(f"Found {len(pt_files)} model files.")
    uuid_list = []
    for model_file in pt_files:
        uuid_list.append(model_file.parent.name)
    return uuid_list


if __name__ == "__main__":
    try:
        test_proto_to_ndarraylist()
        test_ndarraylist_to_proto()
        test_ndarray_to_proto()
        test_proto_to_ndarray()
        test_infer()
        test_load_model_info()
        test_find_model_handler()
        test_load_models()

    except KeyboardInterrupt:
        exit(0)
