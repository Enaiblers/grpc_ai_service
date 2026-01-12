import grpc
import os
import logging
from concurrent import futures
import grpcservice_pb2_grpc 
from grpc_service import GrpcService

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=os.cpu_count()),
                         options=[
        ('grpc.max_send_message_length', 10 * 1024 * 1024),   
        ('grpc.max_receive_message_length', 10 * 1024 * 1024) 
    ])
    grpcservice_pb2_grpc .add_GrpcServiceServicer_to_server(GrpcService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    log.info("GRPC server running")
    server.wait_for_termination()

if __name__ == "__main__" :
    serve()