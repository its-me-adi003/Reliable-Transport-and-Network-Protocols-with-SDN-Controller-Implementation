import json
import subprocess
import matplotlib.pyplot as plt

# Function to modify the value of 'n' in config.json
def modify_config_n(n_value):
    with open('config.json', 'r') as file:
        config = json.load(file)
    
    # Change the 'n' value
    config['n'] = n_value
    
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

# Function to read runtime from 'res.txt'
def read_runtime():
    with open('res.txt', 'r') as file:
        runtime = file.read().strip()
        return float(runtime)

# Values of n from 1 to 33 with a gap of 4
n_values = [1, 5, 9, 13, 17, 21, 25, 29, 33]

# Initialize empty lists to store average runtimes for RR and FIFO scheduling
average_rr_runtimes = []
average_fifo_runtimes = []

# Function to run a scheduling policy (RR or FIFO) for 4 iterations and return the average runtime
def run_scheduling_policy(command):
    runtimes = []
    for _ in range(4):
        # Run the respective make command and wait for it to finish
        subprocess.run(['make', command])

        # Read the runtime from 'res.txt'
        runtime = read_runtime()
        runtimes.append(runtime)

    # Return the average of the 4 runtimes
    return sum(runtimes) / len(runtimes)

# Loop through each value of 'n' for Round Robin
print("Running Round Robin (RR) scheduling...")
for n in n_values:
    # Modify the 'n' value in config.json
    modify_config_n(n)

    # Run RR scheduling policy 4 times and get the average runtime
    avg_rr_runtime = run_scheduling_policy('run-rr')
    average_rr_runtimes.append(avg_rr_runtime)

# Loop through each value of 'n' for FIFO scheduling
print("Running FIFO scheduling...")
for n in n_values:
    # Modify the 'n' value in config.json
    modify_config_n(n)

    # Run FIFO scheduling policy 4 times and get the average runtime
    avg_fifo_runtime = run_scheduling_policy('run-fifo')
    average_fifo_runtimes.append(avg_fifo_runtime)

# Print the average runtimes for RR and FIFO
print("\nAverage Round Robin (RR) runtimes for each n value:")
for i, avg in zip(n_values, average_rr_runtimes):
    print(f"n = {i}: Average RR duration = {avg} ms")

print("\nAverage FIFO runtimes for each n value:")
for i, avg in zip(n_values, average_fifo_runtimes):
    print(f"n = {i}: Average FIFO duration = {avg} ms")

# Plotting the graph of average duration vs. n for both RR and FIFO
plt.figure(figsize=(10, 6))
plt.plot(n_values, average_rr_runtimes, marker='o', linestyle='-', color='b', label='Round Robin')
plt.plot(n_values, average_fifo_runtimes, marker='s', linestyle='-', color='r', label='FIFO')
plt.title('Comparison of Round Robin vs FIFO Scheduling')
plt.xlabel('n Value (Number of Clients)')
plt.ylabel('Average Duration (ms)')
plt.xticks(n_values)  # Ensure x-axis has ticks for each n value
plt.grid(True)
plt.legend()
plt.savefig('plot_comparison.png')
