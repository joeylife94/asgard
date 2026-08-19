package com.heimdall.config;

import io.grpc.ServerInterceptor;
import lombok.extern.slf4j.Slf4j;
import net.devh.boot.grpc.server.interceptor.GrpcGlobalServerInterceptor;
import net.devh.boot.grpc.server.security.authentication.AnonymousAuthenticationReader;
import net.devh.boot.grpc.server.security.authentication.GrpcAuthenticationReader;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * gRPC 서버 설정
 */
@Configuration
@Slf4j
public class GrpcServerConfig {

    /**
     * 현재 구현된 gRPC 서비스가 없으므로 startup 단계에서는 anonymous principal을 명시적으로 제공한다.
     * 실제 gRPC 서비스가 추가되면 해당 서비스의 인증 정책과 함께 교체해야 한다.
     */
    @Bean
    GrpcAuthenticationReader grpcAuthenticationReader() {
        return new AnonymousAuthenticationReader("heimdall-grpc-anonymous");
    }

    /**
     * 전역 gRPC 인터셉터
     * 로깅, 인증, 메트릭 수집 등
     */
    @GrpcGlobalServerInterceptor
    ServerInterceptor loggingInterceptor() {
        return new io.grpc.ServerInterceptor() {
            @Override
            public <ReqT, RespT> io.grpc.ServerCall.Listener<ReqT> interceptCall(
                    io.grpc.ServerCall<ReqT, RespT> call,
                    io.grpc.Metadata headers,
                    io.grpc.ServerCallHandler<ReqT, RespT> next) {
                
                log.debug("gRPC call: method={}, headers={}", 
                        call.getMethodDescriptor().getFullMethodName(), headers);
                
                return next.startCall(call, headers);
            }
        };
    }
}
