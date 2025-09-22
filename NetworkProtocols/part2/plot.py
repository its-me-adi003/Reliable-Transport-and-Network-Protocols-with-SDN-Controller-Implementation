# import matplotlib.pyplot as plt


# a = [288,292,291,293,295,1293,1353,1311,1515]
# n_values = list(range(1, 10))

# # Plotting the graph
# plt.plot(n_values, a, marker='o')

# plt.xlabel("Number of clients")
# plt.ylabel("Average runtime per client")
# plt.title("Graph of average values of runtime per client vs n: Number of clients")


# plt.grid(True)
# plt.savefig("plot.png")

# # 1-> 288
# # 5-> 292
# # 9-> 291
# # 13-> 293
# # 17-> 295
# # 21-> 1293
# # 25-> 1353
# # 29-> 1311
# # 33-> 1515

import json
import os
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

# Initialize an empty list to store runtimes for each 'n'
runtimes_for_n = []

# Values of n from 1 to 33 with a gap of 4
n_values = [1, 5, 9, 13, 17, 21, 25, 29, 33]

# Loop through each value of 'n'
for n in n_values:
    # Modify the 'n' value in config.json
    modify_config_n(n)

    # List to store the runtimes for the current 'n'
    n_runtimes = []

    # Run 'make run' 4 times for each 'n'
    for iteration in range(4):
        # Run the 'make run' command and wait for it to finish
        subprocess.run(['make', 'run'])

        # Read the runtime from 'res.txt'
        runtime = read_runtime()
        n_runtimes.append(runtime)

    # Add the runtimes for the current 'n' to the list
    runtimes_for_n.append(n_runtimes)

# Print the matrix of runtimes (for debugging or viewing purposes)
print("Matrix of runtimes (4 runs for each n value):")
for row in runtimes_for_n:
    print(row)

# Calculate the average of the 4 durations for each value of 'n'
average_durations_for_n = [sum(runtimes) / len(runtimes) for runtimes in runtimes_for_n]

# Print the average durations for each 'n' value
print("\nAverage durations for each n value:")
for i, avg in zip(n_values, average_durations_for_n):
    print(f"n = {i}: Average duration = {avg} ms")

# Plotting the graph of average duration vs. n
plt.figure(figsize=(10, 6))
plt.plot(n_values, average_durations_for_n, marker='o', linestyle='-', color='b', label='Average Duration')
plt.title('Average Duration vs. n Values')
plt.xlabel('n Value (Number of Clients)')
plt.ylabel('Average Duration (ms)')
plt.xticks(n_values)  # Ensure x-axis has ticks for each n value
plt.grid(True)
plt.legend()
plt.savefig('plot.png')
