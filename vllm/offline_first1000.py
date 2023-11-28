from vllm import LLM, SamplingParams
import argparse
import json
from typing import Iterable, List, Generator
# from typing import Generator, Literal, Iterable, Dict
from torch.utils.data import Dataset, DataLoader, Subset

import requests, time
import httpx, asyncio
from typing import AsyncGenerator

input_file = "extracted_file.json"

# Sample prompts.
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
    subset_dataset = Subset(custom_dataset, indices=range(200))
    data_loader = DataLoader(subset_dataset, batch_size=1, shuffle=False)
    for prompt in data_loader:
        yield prompt[0]

# Create a sampling params object.
sampling_params = SamplingParams(temperature=0.0, top_p=1.0, use_beam_search=False, max_tokens=1024, length_penalty=1.0)
print(sampling_params)
# Create an LLM.
llm = LLM(model="facebook/opt-13B", swap_space=25)
# Generate texts from the prompts. The output is a list of RequestOutput objects
# that contain the prompt, generated text, and other information.
print("before generate")
all_outputs = []

for i in range(20):
    data_iter = iter(dataloader(input_file))
    prompts = []
    for prompt in data_iter:
        prompts.append(prompt)
        if (len(prompts)) >= 50:
            break
    outputs = llm.generate(prompts, sampling_params)
    
    # Store the outputs in the list as dictionaries.
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        all_outputs.append({
            "human": prompt,
            "opt": generated_text
        })

# Write the list of dictionaries to a JSON file
with open('opt_output.json', 'w') as outfile:
    json.dump(all_outputs, outfile, indent=4)
        