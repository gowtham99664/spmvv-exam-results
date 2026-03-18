FROM docker.io/ollama/ollama:latest

ENV OLLAMA_HOST=http://127.0.0.1:11434

# Bake the model into the image at build time.
# OLLAMA_HOST must use IPv4 — podman build containers lack IPv6 loopback.
RUN /bin/ollama serve & \
    SERVER_PID=$! && \
    echo "Waiting for ollama server..." && \
    for i in $(seq 1 30); do \
        if OLLAMA_HOST=http://127.0.0.1:11434 /bin/ollama list > /dev/null 2>&1; then \
            echo "Server ready (attempt $i)"; break; \
        fi; \
        sleep 2; \
    done && \
    echo "Pulling qwen2.5:3b..." && \
    OLLAMA_HOST=http://127.0.0.1:11434 /bin/ollama pull qwen2.5:3b && \
    echo "Pull complete" && \
    kill $SERVER_PID && \
    wait $SERVER_PID 2>/dev/null; \
    exit 0

EXPOSE 11434
ENTRYPOINT ["/bin/ollama"]
CMD ["serve"]
