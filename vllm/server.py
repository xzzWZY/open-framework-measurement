import argparse
import json, time, asyncio
import os
import signal
from typing import AsyncGenerator

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse, Response, StreamingResponse
import uvicorn

from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid

TIMEOUT_KEEP_ALIVE = 45  # seconds.
TIMEOUT_TO_PREVENT_DEADLOCK = 1  # seconds.
app = FastAPI()
engine = None

TIMEOUT = 45 
last_request_time = time.time()
total_generate_time = 0

out_file = ""
global_start_time = time.time()

async def shutdown_server():
    global last_request_time
    while True:
        elapsed_time = time.time() - last_request_time
        if elapsed_time > TIMEOUT:
            print("No requests within timeout. Shutting down...")
            os.kill(os.getpid(), signal.SIGTERM)
            break
        await asyncio.sleep(1)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(shutdown_server())


@app.post("/generate")
async def generate(request: Request) -> Response:
    """Generate completion for the request.

    The request should be a JSON object with the following fields:
    - prompt: the prompt to use for the generation.
    - stream: whether to stream the results or not.
    - other fields: the sampling parameters (See `SamplingParams` for details).
    """
    global last_request_time, total_generate_time
    last_request_time = time.time()
    request_dict = await request.json()
    prompt = request_dict.pop("prompt")
    sampling_params = SamplingParams(**request_dict)
    sampling_params.length_penalty = 0.0
    sampling_params.max_tokens = 1024
    request_id = random_uuid()
    print(sampling_params)

    results_generator = engine.generate(prompt, sampling_params, request_id)

    # Non-streaming case
    final_output = None
    async for request_output in results_generator:
        final_output = request_output

    assert final_output is not None
    prompt = final_output.prompt
    text_outputs = [prompt + output.text for output in final_output.outputs]
    ret = {"text": text_outputs}
    global total_generate_time
    total_generate_time = total_generate_time +time.time() - last_request_time
    last_request_time = time.time()
    return JSONResponse(ret)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--out-file", type=str, default="continuous_request")
    parser = AsyncEngineArgs.add_cli_args(parser)
    args = parser.parse_args()

    engine_args = AsyncEngineArgs.from_cli_args(args)
    engine = AsyncLLMEngine.from_engine_args(engine_args)
    
    out_file = args.out_file
    global_start_time = 0
    uvicorn.run(app,
                host=args.host,
                port=args.port,
                log_level="debug",
                timeout_keep_alive=TIMEOUT_KEEP_ALIVE)
    