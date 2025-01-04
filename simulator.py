import numpy as np
import importlib
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import pandas as pd
import os 



def generate_bin_vectors(INS_num):
    vects = []
    
    for i in range(2**INS_num):
        b = bin(i)[2:]
        b = '0'*(INS_num - len(b)) + b
        vects.append((list(map(int, list(b)))))
        
    return np.array(vects)

def get_steady(grn, model=False, rep_num=1, INS_def=False, INS_factor=1, eps=10**(-3)):
    if type(model) == bool:
        grn.generate_model()
        model = 'model'
    if type(model) == str:
        # read the model module    
        model_module = importlib.import_module(model.replace(os.sep,'.')) 
        model_module = importlib.reload(model_module) 
        model = model_module.solve_model

    n_INS = len(grn.input_species_names)
    n_RS = len(grn.species_names) - n_INS


    if INS_def:         
        INS = INS_def
    else:
        INS = generate_bin_vectors(n_INS) * INS_factor


    STATES = []

    for _ in range(rep_num):
        R0 = np.random.random(n_RS)

        for X0 in INS:
            
            states = get_steady_single(grn, model, X0, plot_on=False, eps=eps, R0=R0)
            STATES.append(states[-1])


    df = pd.DataFrame(STATES)
    df.columns = grn.species_names

    return df


def get_steady_single(grn, IN, model=False, INS_factor=1, plot_on=True, legend=True, eps=10**(-3), R0=False, xlabel='time [a.u.]', ylabel='concentrations [a.u.]'):
    # read the model module    
    
    if type(model) == bool:
        grn.generate_model()
        model = 'model'
    if type(model)==str:
        model_module = importlib.import_module(model.replace(os.sep,'.')) 
        model_module = importlib.reload(model_module) 
        model = model_module.solve_model

    n_INS = len(grn.input_species_names)
    n_RS = len(grn.species_names) - n_INS

    X0 = np.array(IN)*INS_factor
    
    if type(R0)==bool:
        R0 = np.random.random(n_RS)
        
    S0 = np.append(X0,R0)
    states = [S0]

    t_step = 1
    dt = 0.1
    T = np.arange(0, t_step+dt, dt)


    while True:

        sol = solve_ivp(model, [0, t_step], states[-1], dense_output=True, method='LSODA') # gre za stiff problem, uporaba LSODA
        z = sol.sol(T)
        Y = z.T
        
        
        if np.max(np.abs(Y[-2]-Y[-1])) < eps:
            break


        states.append(Y[-1])

    if plot_on:
        plt.plot(states)
        if legend:
            plt.legend(grn.species_names)

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.show()

    return states


def simulate_single(grn, IN, model=False, INS_factor=1, t_end=100, plot_on=True, legend=True, R0=False, xlabel='time [a.u.]', ylabel='concentrations [a.u.]'):
    if type(model) == bool:
        grn.generate_model()
        model = 'model'
    if type(model)==str:        
        # read the model module    
        model_module = importlib.import_module(model.replace(os.sep,'.')) 
        model_module = importlib.reload(model_module) 
        model = model_module.solve_model

    n_INS = len(grn.input_species_names)
    n_RS = len(grn.species_names) - n_INS

    X0 = np.array(IN)*INS_factor
    if type(R0)==bool:
        R0 = np.random.random(n_RS)
        
    S0 = np.append(X0,R0)

    sol = solve_ivp(model, [0, t_end], S0, dense_output=True, method='LSODA') # gre za stiff problem, uporaba LSODA
    T = np.arange(0, t_end+1)
    z = sol.sol(T)
    Y = z.T

    if plot_on:
        plt.plot(T,Y)
        if legend:
            plt.legend(grn.species_names)
        
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        plt.show()

    return T,Y


def simulate_sequence(grn, IN_seq, model=False, INS_factor=1, t_single=100, plot_on=True, legend=True, xlabel='time [a.u.]', ylabel='concentrations [a.u.]'):
    if type(model) == bool:
        grn.generate_model()
        model = 'model'
    if type(model)==str:        
        # read the model module    
        model_module = importlib.import_module(model.replace(os.sep,'.')) 
        model_module = importlib.reload(model_module) 
        model = model_module.solve_model

    n_INS = len(grn.input_species_names)
    n_RS = len(grn.species_names) - n_INS
    R0 = False

    T = False
    Y = False

    for IN in IN_seq:

        X0 = np.array(IN)*INS_factor
        if type(R0)==bool:
            #R0 = np.random.random(n_RS)
            R0 = np.zeros(n_RS)
        else:
            R0 = Y1[-1, -n_RS:]

        T1, Y1 = simulate_single(grn, X0, model, INS_factor=1, t_end=t_single, plot_on=False, R0=R0)

        if type(T) == bool:
            T = T1
            Y = Y1
        else:
            Y = np.concatenate([Y, Y1])
            T = np.append(T, T1+T[-1])

    if plot_on:
        plt.plot(T,Y)
        if legend:
            plt.legend(grn.species_names)

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        plt.show()

    return T,Y