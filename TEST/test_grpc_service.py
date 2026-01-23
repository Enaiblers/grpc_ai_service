"""
Contains tests for grpc ai service
"""

import logging
import os
import sys
from concurrent import futures

import grpc
import grpc_service
import grpcservice_pb2
import numpy as np
import pytest
from grpcservice_pb2_grpc import add_GrpcServiceServicer_to_server

logging.basicConfig(
    format=(
        "%(asctime)s [%(levelname)s](%(threadName)-9s %(thread)d) %(name)s: %(message)s"
    ),
    level=logging.DEBUG,
)
log = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(stream_handler)

TEST_MODEL_UUID = "test_model_uuid"


@pytest.fixture(scope="session")
def grpc_server():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=os.cpu_count()),
        options=[
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),
        ],
    )
    add_GrpcServiceServicer_to_server(grpc_service.GrpcService(), server)
    port = server.add_insecure_port("localhost:0")  # 0 = random free port
    server.start()
    print(f"gRPC test server started on port {port}")
    yield port

    server.stop(grace=None)


# def Run(request, context):
#    if request.model_uuid != TEST_MODEL_UUID:
#        log.debug("Model UUID not found")
#        return []
#
#    input = grpc_service.proto_to_ndarray(request.input)
#    output_proto = grpc_service.ndarray_to_proto(input)
#
#    return output_proto
#
# def GetModelInfo(request, context):
#    if request.model_uuid != TEST_MODEL_UUID:
#        log.debug("Model UUID not found")
#        return []
#
#    return [ modelAuthor="Test Author",
#        input_names=["input"],
#        output_names=["output"],
#        input_channels=3,
#        input_height=224,
#        input_width=224
#        ]
#
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


def test_grpc_inference(grpc_server):
    pass
    # port = grpc_server

    # Create a dummy input ndarray
    # img = (np.random.standard_normal([640, 640, 3]) * 255).astype(np.uint8)

    # Convert the input ndarray to proto
    # input_proto = grpc_service.ndarray_to_proto(img)

    # Perform inference

    # Infer detections on all loaded images one by one
    # for n, image in enumerate(image_list):
    #    start_time = monotonic()
    #    detection_boxes = object_detector.infer(image, threshold=0.5)
    #    print(f"detection_boxes: {detection_boxes}")
    #    img = ai_service.draw_on_detections(image.frame, detection_boxes)
    #    img_fname = "detection" + f"_{n}_{model}.jpg"
    #    cv2.imwrite(img_fname, img)
    #    end_time = monotonic()
    #    print("runtime: ", end_time - start_time)


if __name__ == "__main__":
    try:
        test_grpc_inference()
    except KeyboardInterrupt:
        exit(0)


# [DetectedObject(label=33, name='Unknown', bounding_box=[299, 8, 525, 158], confidence=0.7097508907318115, image_id=None, pipeline_id=1)]
