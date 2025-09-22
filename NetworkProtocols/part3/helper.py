def read_completion_time(file_path):
    """Reads the completion time from the given file."""
    try:
        with open(file_path, 'r') as file:
            # Read the content of the file and strip any surrounding whitespace/newlines
            completion_time = file.read().strip()
            return completion_time
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None

def write_to_file(output_file, content):
    """Writes the content to the output file."""
    with open(output_file, 'w') as file:
        file.write(content)

def main():
    # File paths
    aloha_file = 'res_aloha.txt'
    beb_file = 'res_beb.txt'
    cscd_file = 'res_cscd.txt'
    output_file = 'res.txt'

    # Read completion times from each file
    aloha_time = read_completion_time(aloha_file)
    beb_time = read_completion_time(beb_file)
    cscd_time = read_completion_time(cscd_file)

    # Check if all files were read successfully
    if None not in [aloha_time, beb_time, cscd_time]:
        # Prepare the content as comma-separated values
        result = f"{aloha_time},{beb_time},{cscd_time}"
        # Write the result to res.txt
        write_to_file(output_file, result)
        print(f"Completion times written to {output_file}")
    else:
        print("Error: Unable to read one or more files.")

if __name__ == "__main__":
    main()
