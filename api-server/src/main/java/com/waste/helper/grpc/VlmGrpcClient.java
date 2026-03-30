package com.waste.helper.grpc;

import com.waste.helper.grpc.vlm.*;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import jakarta.annotation.PreDestroy;

@Service
public class VlmGrpcClient {

    private final ManagedChannel channel;
    private final VLMInferenceGrpc.VLMInferenceBlockingStub stub;

    public VlmGrpcClient(
        @Value("${vlm-service.host:vlm-service}") String host,
        @Value("${vlm-service.port:50051}") int port
    ) {
        this.channel = ManagedChannelBuilder
            .forAddress(host, port)
            .usePlaintext()
            .build();
        this.stub = VLMInferenceGrpc.newBlockingStub(channel);
    }

    public AnalyzeResponse analyzeWaste(byte[] imageData, String yoloClass,
                                        float confidence, String regionCode) {
        AnalyzeRequest request = AnalyzeRequest.newBuilder()
            .setImageData(com.google.protobuf.ByteString.copyFrom(imageData))
            .setYoloClass(yoloClass)
            .setConfidence(confidence)
            .setRegionCode(regionCode != null ? regionCode : "")
            .build();

        return stub.analyzeWaste(request);
    }

    @PreDestroy
    public void shutdown() {
        channel.shutdown();
    }
}