"""Example Python client for vllm.entrypoints.api_server"""

import argparse
import json
from typing import Iterable, List, Generator
# from typing import Generator, Literal, Iterable, Dict
from torch.utils.data import Dataset, DataLoader, Subset
import numpy as np

import requests, time
import httpx, asyncio
from typing import AsyncGenerator


async def post_http_request(prompt: str, api_url: str, n: int = 1):
    with open("prompt_type", 'a') as f:
        f.write(f"{prompt}: {type(prompt)}")
    headers = {"User-Agent": "Test Client"}
    pload = {
        "prompt": prompt,
        "n": n,
        "use_beam_search": False,
        "temperature": 1.0,  # modify to 1.0 for more diverse input
        "max_tokens": 1024,
    }
    async with httpx.AsyncClient(timeout=50.0) as client:
        await client.post(api_url, headers=headers, json=pload)


class CustomDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        sample = self.data[index]
        return sample["human"]
    

def dataloader(input_file: str) -> Generator[str, None, None]:
    """Yields a tuple of whether this is a warmup run and the input prompt."""
    data = json.load(open(input_file, "r"))
    custom_dataset = CustomDataset(data)
    # subset_dataset = Subset(custom_dataset, indices=range(20))
    data_loader = DataLoader(custom_dataset, batch_size=1, shuffle=False)
    for prompt in data_loader:
        yield prompt[0]


async def main(args, api_url, n):
    # data_iter = iter(dataloader(args.input_file))
    from helper import process_MMLU
    prompts = process_MMLU("MMLU_test")

    period = 60
    send_request_duration = period * 0.7  
    start_time = time.time()

    # for prompt in data_iter:
    for prompt in prompts:
        if time.time() - start_time < send_request_duration:
            poisson_delay = np.random.poisson(10 * args.delay / 1.4)  # 使用调整后的lambda值
            if 0.2 <= poisson_delay <= 50:
                asyncio.create_task(post_http_request(prompt[0], api_url, n))
                with open("delay.txt", 'a') as f:
                    f.write(f"poisson_delay:{poisson_delay / 10}\n")
                await asyncio.sleep(poisson_delay / 10)
        
        else:
            remaining_time = period - (time.time() - start_time)
            if remaining_time < period*0.3 and remaining_time > 0:
                await asyncio.sleep(remaining_time)
                start_time = time.time()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--input-file", type=str, default="extracted_file.json")
    # parser.add_argument("--prompt", type=str, default="San Francisco is a")
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--delay", type=float, default=0.1)
    args = parser.parse_args()
    # prompt = args.prompt
    api_url = f"http://{args.host}:{args.port}/generate"
    n = args.n
    asyncio.run(main(args, api_url, n))
