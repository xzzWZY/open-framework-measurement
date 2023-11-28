#!/bin/bash
model=meta-llama/Llama-2-13b-chat-hf
token=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
# Step 1: Run docker in background
docker run --gpus all --shm-size 1g -e HUGGING_FACE_HUB_TOKEN=$token -p 8080:80 -v $volume:/data ghcr.io/huggingface/text-generation-inference:1.1.0 --model-id $model > tgi_server_log.txt &
DOCKER_PID=$!

python server_monitor.py --out-file server-metric-045.txt &
monitor_pid=$!

sleep 50
# Step 2: Run python script
python3 tgi_sharegpt.py --input-file shuffled_6000.json --sleep-time 2.6 --period 60 &
client_pid=$!

wait $client_pid
sleep 60

mv tgi_server_log.txt short_tgi_server_26.txt

# Step 4: Rename log files
mv response_log.txt short_tgi_response_26.txt
