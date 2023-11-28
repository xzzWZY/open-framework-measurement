import json
import random

def sort_and_select_json(input_file_path, output_file_path, select_count=6000):
    # Load JSON data from the file
    with open(input_file_path, 'r') as file:
        data = json.load(file)

    filtered_data = [item for item in data if 'human' in item]

    # Sort the data by the length of the 'human' string
    sorted_data = sorted(filtered_data, key=lambda x: len(x['human']))

    # Select evenly spaced items from the sorted data
    step = len(sorted_data) // select_count
    selected_data = sorted_data[::step] if step > 0 else sorted_data

    # Shuffle the selected data
    random.shuffle(selected_data)

    # Save the selected data to a new JSON file
    with open(output_file_path, 'w') as file:
        json.dump(selected_data, file, indent=4)

# Example usage
input_file = 'extracted_file.json'
output_file = 'shuffled_6000.json'
sort_and_select_json(input_file, output_file)
