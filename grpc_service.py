import logging
from pathlib import Path

import numpy as np

if __name__ == "grpc_service":
    import grpcservice_pb2
    import grpcservice_pb2_grpc
    from ai_model_handler import AIModelHandler
else:
    # Add your custom import paths here
    import AI.grpc_ai_service.grpcservice_pb2 as grpcservice_pb2
    import AI.grpc_ai_service.grpcservice_pb2_grpc as grpcservice_pb2_grpc
    from AI.grpc_ai_service.ai_model_handler import AIModelHandler


log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

MODEL_BASE_PATH = Path("/media/m2ssd/exported_models/grpc_models/")


class GrpcService(grpcservice_pb2_grpc.GrpcServiceServicer):
    def __init__(self):
        super().__init__()
        self.model_handlers = {}

        # TODO: Choose which model file to use if more than one
        onnx_files = list(MODEL_BASE_PATH.rglob("*.onnx"))
        log.info(f"Found {len(onnx_files)} model files.")

        for path in onnx_files:
            uuid = path.parent.name
            log.info(f"Found model file: {path} with UUID: {path.parent.name}")
            self.model_handlers[uuid] = AIModelHandler(model_uuid=uuid)
            self.model_handlers[uuid].load_model(path)

    def Run(self, request, context):

        model_handler = None
        for x in self.model_handlers:
            if self.model_handlers[x]._model_uuid == request.model_uuid:
                model_handler = self.model_handlers[x]

        input_tensor = proto_to_ndarray(request.input)
        input_feed = {model_handler.input_name: input_tensor}

        log.info(f"Running inference with model_uuid: {model_handler._model_uuid}")
        result = model_handler.run(None, input_feed)

        return grpcservice_pb2.RunResponse(
            output_names=model_handler.output_names, output=ndarraylist_to_proto(result)
        )

    def GetModelInfo(self, request, context):
        model_handler = None
        for x in self.model_handlers:
            if self.model_handlers[x]._model_uuid == request.model_uuid:
                model_handler = self.model_handlers[x]
                log.info(
                    f"Model info request for model_uuid: {request.model_uuid} found."
                )

        inputs = model_handler._model.get_inputs()
        return grpcservice_pb2.ModelInfoResponse(
            input_names=model_handler.input_name,
            output_names=model_handler.output_names,
            modelAuthor=model_handler._model_author,
            input_channels=inputs[0].shape[1],
            input_height=inputs[0].shape[2],
            input_width=inputs[0].shape[3],
        )


# --- gRPC helpers ---
def ndarray_to_proto(arr: np.ndarray) -> grpcservice_pb2.NDArray:
    return grpcservice_pb2.NDArray(
        data=arr.tobytes(), shape=arr.shape, dtype=str(arr.dtype)
    )


def proto_to_ndarray(proto: grpcservice_pb2.NDArray) -> np.ndarray:
    return np.frombuffer(proto.data, dtype=np.dtype(proto.dtype)).reshape(proto.shape)


def ndarraylist_to_proto(nplist: list[np.ndarray]) -> grpcservice_pb2.NDArrayList:
    protolist = grpcservice_pb2.NDArrayList()
    for arr in nplist:
        protolist.arr.add(data=arr.tobytes(), shape=arr.shape, dtype=str(arr.dtype))
    return protolist


def proto_to_ndarraylist(proto: grpcservice_pb2.NDArrayList) -> list[np.ndarray]:
    ndarray_list = []
    for a in proto.arr:
        ndarray_list.append(
            np.frombuffer(a.data, dtype=np.dtype(a.dtype)).reshape(a.shape)
        )
    return ndarray_list
