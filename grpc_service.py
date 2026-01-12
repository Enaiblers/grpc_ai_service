from pathlib import Path
import numpy as np

if __name__ == "grpc_service":
    from ai_model_handler import AIModelHandler
    import grpcservice_pb2,  grpcservice_pb2_grpc
else:
    # Add your custom import paths here
    from AI.grpc_ai_service.ai_model_handler import AIModelHandler
    import AI.grpc_ai_service.grpcservice_pb2 as grpcservice_pb2, AI.grpc_ai_service.grpcservice_pb2_grpc as grpcservice_pb2_grpc


class GrpcService(grpcservice_pb2_grpc.GrpcServiceServicer):
    
    def __init__(self):
        print(__name__)
        super().__init__()
        self.model_handlers = {1 : AIModelHandler(1),
                               2 : AIModelHandler(2)}
        boundary_model_path = Path("/home/slidemanager/david/boundary.onnx")
        boundary_model_path.resolve()
        object_detector_model_path = Path("/media/m2ssd/exported_models/yolov8_230629/detector.onnx")   
        object_detector_model_path.resolve()

        self.model_handlers[1].load_model(boundary_model_path)
        self.model_handlers[2].load_model(object_detector_model_path) 
        
    def Run(self, request, context):

        model_handler = None
        for x in self.model_handlers : 
            if self.model_handlers[x]._handler_id == request.model_id :
                model_handler = self.model_handlers[x]

        input_tensor = proto_to_ndarray(request.input)
        input_feed = { model_handler.input_name : input_tensor }
    
        result = model_handler.run(None,input_feed) 
        return grpcservice_pb2.RunResponse(
            output_names= model_handler.output_names,
            output=ndarraylist_to_proto(result)
            )
    
    def GetModelInfo(self, request, context):
        model_handler = None
        for x in self.model_handlers : 
            if self.model_handlers[x]._handler_id == request.model_id :
                model_handler = self.model_handlers[x]

        inputs = model_handler._model.get_inputs()
        return grpcservice_pb2.ModelInfoResponse(
            input_names=model_handler.input_name,
            output_names=model_handler.output_names,
            modelAuthor=model_handler._model_author,
            input_channels=inputs[0].shape[1],
            input_height=inputs[0].shape[2],
            input_width=inputs[0].shape[3]
        )

# --- gRPC helpers ---
def ndarray_to_proto(arr: np.ndarray) -> grpcservice_pb2.NDArray:
    return grpcservice_pb2.NDArray(
        data=arr.tobytes(),
        shape=arr.shape,
        dtype=str(arr.dtype)
    )

def proto_to_ndarray(proto: grpcservice_pb2.NDArray) -> np.ndarray:
    return np.frombuffer(
        proto.data,
        dtype=np.dtype(proto.dtype)
    ).reshape(proto.shape)

def ndarraylist_to_proto(nplist: list[np.ndarray]) -> grpcservice_pb2.NDArrayList:
    protolist = grpcservice_pb2.NDArrayList()
    for arr in nplist :
        protolist.arr.add(
            data=arr.tobytes(),
            shape=arr.shape,
            dtype=str(arr.dtype)
        )
    return protolist

def proto_to_ndarraylist(proto: grpcservice_pb2.NDArrayList) -> list[np.ndarray]:
    ndarray_list = []
    for a in proto.arr :
        ndarray_list.append(np.frombuffer(
        a.data,
        dtype=np.dtype(a.dtype)
    ).reshape(a.shape))
    return ndarray_list