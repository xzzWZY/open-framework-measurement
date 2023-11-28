# LLM open-framework inference measuremrnt

## Framework:

1. vLLM
2. text-generation-inference
3. TensorRT-LLM
4. Deepspeed-mii

## Metrics:

### Client side

1. Token latency
    1. Avg latency
    2. Variance
2. Pause time
    1. Total pause time
    2. Pause ratio: pause time / end-to-end inference time
3. Time to first token
    1. Prefilling time
    2. Queuing time

### Server side

1. Memory
2. Memory IO
3. Compute 
4. Energy

## Model:

- Llama v2
    - 13B