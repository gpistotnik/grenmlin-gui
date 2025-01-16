import numpy as np 

def solve_model(T,state):
    I1, O3, O2, O1 = state
    dI1 = -I1*0
    dO3 = -O3*0.1+10*(1)/(1+((O2/1.0)**6.0))
    dO2 = -O2*0.1+10*(1)/(1+((O1/1.0)**6.0))
    dO1 = -O1*0.1+10*(((I1/1.0)**2.0))/(1+((O3/1.0)**6.0)+((I1/1.0)**2.0)+((O3/1.0)**6.0)*((I1/1.0)**2.0))
    return np.array([dI1, dO3, dO2, dO1])

def solve_model_steady(state):
    return solve_model(0, state)
