import json

# Function to read JSON file and write to a text file
def json_to_text(input_json_file, output_text_file):
    # Read the JSON file
    with open(input_json_file, 'r') as infile:
        data = json.load(infile)

    # Write the key-value pairs to a text file
    with open(output_text_file, 'w') as outfile:
        for key, value in data.items():
            outfile.write(f"{key} {value}\n")

# Specify the input JSON file and output text file
input_json_file = 'config.json'
output_text_file = 'output.txt'

# Convert JSON to space-separated key-value pairs in text file
json_to_text(input_json_file, output_text_file)
