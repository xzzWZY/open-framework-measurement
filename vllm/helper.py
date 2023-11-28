import os, csv
import random

def process_MMLU(directory):
    def get_required_lines_from_csv(file_path):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            lines = list(reader)
            # Sort lines by their length
            lines.sort(key=lambda x: len(' '.join(x)))

            # Select seven evenly distributed lines
            step = len(lines) // 100
            selected_lines = [lines[i * step][:-1] for i in range(100)]  # Exclude last column of each line
            random.shuffle(selected_lines)
            return selected_lines
        
    directory = f"{directory}"
    results = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            selected_lines = get_required_lines_from_csv(file_path)
            results += selected_lines
    return results

# results = process_MMLU("MMLU_test")
# print(f"num of request: {len(results)}")