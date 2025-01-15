import numpy as np 

def solve_model(T,state):
    I2, I1, O1 = state
    dI2 = -I2*0
    dI1 = -I1*0
    dO1 = -O1*0.1+10*(1)/(1+((I2/5.0)**1.0))+10*(((I1/5.0)**1.0))/(1+((I1/5.0)**1.0))
    return np.array([dI2, dI1, dO1])

def solve_model_steady(state):
    return solve_model(0, state)
