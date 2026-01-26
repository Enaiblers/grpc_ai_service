import json
import logging
import os
import signal
from concurrent import futures
from typing import Any

import grpc
import grpcservice_pb2_grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from grpc_service import GrpcService

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

with open("config.json", "r") as f:
    config = json.load(f)

SERVICE_NAME = config["service_name"]
send_message_length = config["max_send_message_length"]
receive_message_length = config["max_receive_message_length"]


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=os.cpu_count()),
        options=[
            ("grpc.max_send_message_length", send_message_length),
            ("grpc.max_receive_message_length", receive_message_length),
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
