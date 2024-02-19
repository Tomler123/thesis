import numpy as np
import sys

def hypothesis(theta, x):
    return np.dot(theta, x)

def cost_function(theta, x, y):
    return (1 / 2) * ((hypothesis(theta, x) - y) ** 2)

def gradient_descent(x, y, alpha=0.0001, num_iterations=10000000, tolerance=1e-5):
    num_features = len(x[0])
    theta = np.zeros(num_features)
    temp = np.zeros(num_features)
    m = len(y)
    
    prev_cost = float('inf')  # Initialize with a large value

    for iteration in range(num_iterations):
        for i in range(num_features):
            sum_gradient = 0
            for j in range(m):
                sum_gradient += (hypothesis(theta, x[j]) - y[j]) * x[j][i]
            temp[i] = theta[i] - (alpha / m) * sum_gradient

        # Calculate current cost function
        current_cost = sum(cost_function(temp, x[j], y[j]) for j in range(m)) / m

        # Check for convergence
        if abs(current_cost - prev_cost) < tolerance:
            print(f"Converged at iteration {iteration + 1}")
            break

        prev_cost = current_cost
        theta = temp.copy()

    return theta




def main(X,Y):
    optimal_theta = gradient_descent(X, Y)
    print("Optimal theta:", optimal_theta)


if __name__=='__main__':
     if(len(sys.argv)==3):
        main(sys.argv[1],sys.argv[2])