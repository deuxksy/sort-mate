"""gRPC 서버 — VLMInference 서비스 구현."""

import grpc
from concurrent import futures

import vlm_service_pb2
import vlm_service_pb2_grpc

from .vlm_engine import VLMEngine


class VLMInferenceServicer(vlm_service_pb2_grpc.VLMInferenceServicer):
    def __init__(self):
        self.engine = VLMEngine()

    def AnalyzeWaste(self, request, context):
        try:
            result = self.engine.analyze(
                image_bytes=request.image_data,
                yolo_class=request.yolo_class,
                confidence=request.confidence,
                region=request.region_code,
            )

            items = [
                vlm_service_pb2.DisposalItem(label=item["label"], action=item["action"])
                for item in result.get("disposal_method", {}).get("items", [])
            ]

            disposal_method = vlm_service_pb2.DisposalMethod(
                method=result.get("disposal_method", {}).get("method", ""),
                notes=result.get("disposal_method", {}).get("notes", []),
                items=items,
            )

            return vlm_service_pb2.AnalyzeResponse(
                waste_type=result.get("waste_type", ""),
                disposal_method=disposal_method,
                cost_info=result.get("cost_info", ""),
                warnings=result.get("warnings", ""),
                confidence=result.get("confidence", 0.0),
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"VLM inference failed: {str(e)}")
            return vlm_service_pb2.AnalyzeResponse()


def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    vlm_service_pb2_grpc.add_VLMInferenceServicer_to_server(VLMInferenceServicer(), server)
    server.add_insecure_port("[::]:" + str(port))
    server.start()
    print(f"VLM gRPC server started on port {port}")
    server.wait_for_termination()
