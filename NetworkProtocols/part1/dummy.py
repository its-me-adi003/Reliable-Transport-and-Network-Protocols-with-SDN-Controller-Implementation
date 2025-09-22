
import matplotlib.pyplot as plt
arr=[[]for i in range(10)]

arr[0] = [286, 286, 290, 287, 287, 288, 288, 286, 287, 286]
arr[1] = [287, 287, 286, 287, 287, 287, 287, 286, 286, 286]
arr[2] = [287, 286, 289, 288, 287, 286, 290, 287, 286, 289]
arr[3] = [288, 286, 287, 287, 289, 286, 286, 287, 289, 286]
arr[4] = [286, 288, 288, 287, 288, 287, 286, 287, 288, 288]
arr[5] = [287, 288, 286, 287, 286, 287, 286, 289, 286, 287]
arr[6] = [288, 286, 287, 287, 288, 287, 286, 287, 287, 287]
arr[7] = [245, 246, 245, 245, 246, 247, 247, 246, 246, 246]
arr[8] = [247, 246, 246, 245, 247, 245, 247, 249, 246, 249]
arr[9] = [0.3,0.3,0.2,0.3,0.2,0.3,0.3,0.3,0.3,0.2]

a=[]

for i in range(10):
    sum = 0
    for j in range(10):
        sum += arr[i][j]
    a.append(sum/10)
    

p_values = list(range(1, 11))

# Plotting the graph
plt.plot(p_values, a, marker='o')

# Add labels and title
plt.xlabel("p values (1 to 10)")
plt.ylabel("Average of runtime")
plt.title("Graph of average values of runtime vs p values")

# Show the plot
plt.grid(True)
plt.savefig("plot.png")
