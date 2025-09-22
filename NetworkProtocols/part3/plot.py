import subprocess
import json
import matplotlib.pyplot as plt

# Path to the config.json file
CONFIG_FILE = 'config.json'

# Function to read the runtime from the result file
def read_runtime(filename):
    with open(filename, 'r') as file:
        return float(file.read().strip())

# Function to update the value of 'n' in the config.json file
def update_n_in_config(n_value):
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)

    # Update the 'n' value
    config['n'] = n_value

    # Write back the updated config
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

# Function to run the make command and get the average time
def run_algorithm(algorithm, result_file, n_values):
    runtimes = []
    
    for n in n_values:
        n_runtimes = []

        # Update the value of n in the config.json file
        update_n_in_config(n)

        # Run the algorithm 4 times and take the average
        for _ in range(4):
            # Execute the make command to run the specific algorithm
            subprocess.run([f'make', f'run-{algorithm}'], check=True)
            # Read the completion time from the result file
            runtime = read_runtime(result_file)
            n_runtimes.append(runtime)
        
        # Append the average runtime for the current value of n
        avg_runtime = sum(n_runtimes) / len(n_runtimes)
        runtimes.append(avg_runtime)

    return runtimes

# Define the range of n values (1, 5, 9, 13, 17, 21, 25, 29, 33)
n_values = [1, 5, 9, 13, 17, 21, 25, 29, 33]

# Run the algorithms and get the average runtimes
aloha_runtimes = run_algorithm('aloha', 'res_aloha.txt', n_values)
beb_runtimes = run_algorithm('beb', 'res_beb.txt', n_values)
cscd_runtimes = run_algorithm('cscd', 'res_cscd.txt', n_values)

# Plot the results
plt.figure(figsize=(10, 6))

plt.plot(n_values, aloha_runtimes, marker='o', color='blue', label='Slotted Aloha')
plt.plot(n_values, beb_runtimes, marker='x', color='red', label='Binary Exponential Backoff (BEB)')
plt.plot(n_values, cscd_runtimes, marker='s', color='green', label='CSCD')

plt.title('Average Completion Time vs n Values')
plt.xlabel('n Value (Number of Clients)')
plt.ylabel('Average Completion Time (ms)')
plt.xticks(n_values)
plt.grid(True)
plt.legend()
plt.savefig('plot.png')
# plt.show()
