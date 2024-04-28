import sys
import numpy as np
import csv




def hypoFunc(theta, Property):
    tmp = np.transpose(theta)
    m = np.matmul(Property,tmp)
    return m


def CostFunction(theta, X, Y):
    t = (hypoFunc(theta, np.transpose(X)) - Y)
    t=np.transpose(t)
    for i in range(len(t)):
        t[i]=float(t[i])*float(t[i])
    return (1 / (2 * len(X))) * t.sum()


def GradDescnet(theta, Y, X, alpha=0.0001, num_iterations=100000, tolerance=1e-5):
    temp = theta.copy()
    prev_cost = float('inf')  # Initialize with a large value
    for iteration in range(num_iterations):
        for i in range(len(theta)):
            sum_ = 0
            for j in range(len(Y)):
                sum_ += np.transpose(X)[j][i] * ((hypoFunc(temp, np.transpose(X)[j]) - np.transpose(Y)[j]))
            temp[i] = temp[i] - (alpha / len(Y)) * sum_
        # Calculate current cost function
        current_cost = CostFunction(temp, X, Y)

        # Check for convergence
        # if abs(current_cost - prev_cost) < tolerance:
        #     print(f"Converged at iteration {iteration + 1}")
        #     break

        prev_cost = current_cost

    return temp


def main(trasnactions_matrix,prices):
    f = open("theta.txt", "r")
    theta= f.readline()
   
    Theta=[int(theta)]
    Theta = GradDescnet(Theta,prices,trasnactions_matrix)

    return hypoFunc(Theta,np.transpose(trasnactions_matrix)[len(trasnactions_matrix)-1]+1)
        
if __name__ == "__main__":
    if len(sys.argv) == 3:
        c=main(np.matrix(sys.argv[1]),np.matrix(sys.argv[2]))
        print(c)
    else:
        print("not enough argument given") 
              