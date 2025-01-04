import numpy as np 

def solve_model(T,state):
    I1, I2, O1 = state
    dI1 = -I1*0
    dI2 = -I2*0
    dO1 = -O1*0.1+10*(((I2/5)**2))/(1+((I2/5)**2))+10*(((I1/5)**2))/(1+((I1/5)**2))
    return np.array([dI1, dI2, dO1])

def solve_model_steady(state):
    return solve_model(0, state)
