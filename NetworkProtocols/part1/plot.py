# import subprocess
# import time

# def run_experiment():
#     times = []

#     for i in range(10):
#         print(f"Iteration {i+1}")

#         # Run the bash script to execute server and client in different terminals
#         subprocess.run(["./run_server_client.sh"])

#         # Wait for the client to finish and gather the time from res.txt
#         time.sleep(5)  # Adjust this based on how long your client takes to finish

#         try:
#             with open('res.txt', 'r') as f:
#                 content = f.read().strip()

#                 # Check if the file is empty
#                 if not content:
#                     raise ValueError("res.txt is empty")

#                 # Convert the content to an integer (time in ms)
#                 time_taken = int(content)
                
#                 # Store the time in the list
#                 times.append(time_taken)
#                 print(f"Iteration {i+1}: {time_taken} ms")

#         except ValueError as e:
#             print(f"Error: {e}")
#             continue  # Skip iteration if error occurs

#     # Print all times
#     print("\nAll times:", times)

# if __name__ == "__main__":
#     run_experiment()

import json
import os
import subprocess
import matplotlib.pyplot as plt
# Function to modify the value of 'p' in config.json
def modify_config_p(p_value):
    with open('config.json', 'r') as file:
        config = json.load(file)
    
    # Change the 'p' value
    config['p'] = p_value
    
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

# Function to read runtime from 'res.txt'
def read_runtime():
    with open('res.txt', 'r') as file:
        runtime = file.read().strip()
        return float(runtime)

# Initialize an empty 10x10 matrix to store runtimes
runtimes_matrix = []

# Loop through each value of 'p' from 1 to 10
for p in range(1, 11):
    # Modify the 'p' value in config.json
    modify_config_p(p)

    # List to store the runtimes for the current 'p'
    p_runtimes = []

    # Run 'make run' 10 times for each 'p'
    for iteration in range(10):
        # Run the 'make run' command and wait for it to finish
        subprocess.run(['make', 'run'])

        # Read the runtime from 'res.txt'
        runtime = read_runtime()
        p_runtimes.append(runtime)

    # Add the runtimes for the current 'p' to the matrix
    runtimes_matrix.append(p_runtimes)

# Print the 10x10 matrix of runtimes
print("10x10 matrix of runtimes (in ms):")
for row in runtimes_matrix:
    print(row)

average_durations = [sum(runtimes) / len(runtimes) for runtimes in runtimes_matrix]

# Print the 10-size array of average durations
print("\nAverage durations for each p value:")
for i, avg in enumerate(average_durations, start=1):
    print(f"p = {i}: Average duration = {avg} ms")

# Plotting the graph of average duration vs. p
p_values = list(range(1, 11))

plt.figure(figsize=(10, 6))
plt.plot(p_values, average_durations, marker='o', linestyle='-', color='b', label='Average Duration')
plt.title('Average Duration vs. p Values')
plt.xlabel('p Value')
plt.ylabel('Average Duration (ms)')
plt.xticks(p_values)  # Ensure x-axis has ticks for each p value
plt.grid(True)
plt.legend()
plt.savefig('plot.png')
