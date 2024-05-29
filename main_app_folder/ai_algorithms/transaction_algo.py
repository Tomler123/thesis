import numpy as np

def hypoFunc(theta, Property):
    tmp = np.transpose(theta)
    m = np.matmul(Property,tmp)
    return m

def CostFunction(theta, X, Y):
    t = (hypoFunc(theta, X) - Y)
    t=np.transpose(t)
    for i in range(len(t)):
        t[i]=float(t[i])*float(t[i])
    return (1 / (2 * len(X))) * t.sum()

def GradDescnet(theta, Y, X, alpha=0.0001, num_iterations=100000, tolerance=1e-5):
    temp = theta.copy()
    prev_cost = float('inf')

    for iteration in range(num_iterations):
        for i in range(len(theta)):
            sum_ = 0
            for j in range(len(Y)):
                vec= np.array(X[j]).flatten()
                sum_ += vec[i] * ((hypoFunc(temp,vec) - Y[j]))
        
            temp[i] = temp[i] - (alpha / len(Y)) * sum_
        
        current_cost = CostFunction(temp, X, Y)

        prev_cost = current_cost

    return temp

def main(X_inp,Y_inp):
    X_inp = np.matrix(X_inp)
    Y_inp = np.matrix(Y_inp)
    Theta = np.loadtxt("theta.txt", delimiter=' ')
    X_inp=np.transpose(X_inp)
    Y = np.array(Y_inp).flatten()
    X = np.hstack((np.ones((len(X_inp), 1)), X_inp))
    Theta = np.array(Theta)
    Theta = GradDescnet(Theta,Y,X)
    ans=np.array(X[-1]).flatten()
    ans[1] =ans[1]+1
    return hypoFunc(Theta, ans)
