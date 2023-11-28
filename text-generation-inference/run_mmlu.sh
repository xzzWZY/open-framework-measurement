#!/bin/bash
model=meta-llama/Llama-2-13b-chat-hf
token=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
# Step 1: Run docker in background
docker run --gpus all --shm-size 1g -e HUGGING_FACE_HUB_TOKEN=$token -p 8080:80 -v $volume:/data ghcr.io/huggingface/text-generation-inference:1.1.0 --model-id $model > tgi_server_log.txt &
DOCKER_PID=$!

python3 server_monitor.py --out-file server-metric-9.txt &
monitor_pid=$!

sleep 50
# Step 2: Run python script
python3 tgi_mmlu.py --sleep-time 0.9 --period 60 &
client_pid=$!

wait $client_pid
sleep 60

mv tgi_server_log.txt tgi_server_mmlu_9.txt

# Step 4: Rename log files
mv response_log.txt tgi_response_mmlu_9.txt
