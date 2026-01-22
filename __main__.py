import os
import logging
from concurrent import futures
import signal
from typing import Any
import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
import grpcservice_pb2_grpc
from grpc_service import GrpcService

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

SERVICE_NAME = "grpcservice.GrpcService"


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=os.cpu_count()),
        options=[
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),
        ],
    )
    grpcservice_pb2_grpc.add_GrpcServiceServicer_to_server(GrpcService(), server)
    health_servicer = health.HealthServicer(
        experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=10),
    )
    # Add Health Servicer and set state to SERVING
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set(SERVICE_NAME, health_pb2.HealthCheckResponse.SERVING)

    def handle_sigterm(*_: Any) -> None:
        health_servicer.set(SERVICE_NAME, health_pb2.HealthCheckResponse.NOT_SERVING)
        server.stop(30)

    # Start Server
    server.add_insecure_port("[::]:50051")
    server.start()

    signal.signal(signal.SIGTERM, handle_sigterm)
    log.info("GRPC server running")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
