import logging

import numpy as np
from grpc import StatusCode

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


class GrpcStatusUnavailableError(Exception):
    pass


class GrpcService(grpcservice_pb2_grpc.GrpcServiceServicer):
    def __init__(self, model_base_path):
        super().__init__()
        self._model_base_path = model_base_path
        self._model_handlers = self.load_model_handlers(model_base_path)

    def Run(self, request, context):
        model_handler = self.find_model_handler(
            self._model_handlers, request.model_uuid
        )
        if model_handler is None:
            context.abort(
                StatusCode.NOT_FOUND,
                f"model_handler with uuid {request.model_uuid} could not be found",
            )
        input_tensor = proto_to_ndarray(request.input)
        input_feed = {model_handler.input_name: input_tensor}

        log.debug(f"Running inference with model_uuid: {model_handler._model_uuid}")
        result = model_handler.run(None, input_feed)
        return grpcservice_pb2.RunResponse(
            output_names=model_handler.output_names, output=ndarraylist_to_proto(result)
        )

    def GetModelInfo(self, request, context):
        model_handler = self.find_model_handler(
            self._model_handlers, request.model_uuid
        )
        if model_handler is None:
            context.abort(
                StatusCode.NOT_FOUND,
                f"model_handler with uuid {request.model_uuid} could not be found",
            )
        inputs = model_handler._model.get_inputs()
        return grpcservice_pb2.ModelInfoResponse(
            input_name=model_handler.input_name,
            output_names=model_handler.output_names,
            modelAuthor=model_handler._model_author,
            input_channels=inputs[0].shape[1],
            input_height=inputs[0].shape[2],
            input_width=inputs[0].shape[3],
        )

    @staticmethod
    def load_model_handlers(model_base_path):
        onnx_files = list(model_base_path.rglob("*.onnx"))
        log.debug(f"Found {len(onnx_files)} model files.")
        model_handlers = {}
        for path in onnx_files:
            uuid = path.parent.name
            log.debug(f"Found model file: {path} with UUID: {path.parent.name}")
            model_handlers[uuid] = GrpcService.create_and_load_handler(uuid, path)
        return model_handlers

    @staticmethod
    def find_model_handler(model_handler_list, uuid) -> AIModelHandler:
        for x in model_handler_list:
            if model_handler_list[x]._model_uuid == uuid:
                model_handler = model_handler_list[x]
                return model_handler

    @staticmethod
    def create_and_load_handler(model_uuid, path) -> AIModelHandler:
        handler = AIModelHandler(model_uuid=model_uuid)
        handler.load_model(path)
        return handler

    @property
    def model_handlers(self):
        return self._model_handlers


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
