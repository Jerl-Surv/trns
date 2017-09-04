import os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import minimize

def in_file(Q_acb, P_pv_max, angle, data_base):
    param_file_name = 'Param_Project2_for_' + data_base + '.txt'
    f = open(param_file_name, 'w')
    f.write('0 ' + str(angle) + ' 24 ' + str(angle) + '\n')
    f.write('1 1 3 1 ' + str(angle) + '\n')
    f.write("%s\n" % P_pv_max)
    f.write("%s" % Q_acb)
    
    f.close()

def find_f(P_pv, Q_acb, angle, data_base):
    in_file(Q_acb, P_pv, angle, data_base)
    
    if (data_base == 'NASA'):
        os.system('C:\Trnsys17\Exe\TRNExe.exe C:\Trnsys17\MyProjects\Project2\Project2_for_NASA.dck /h')
    else:
        os.system('C:\Trnsys17\Exe\TRNExe.exe C:\Trnsys17\MyProjects\Project2\Project2_for_WRDC.dck /h')
    
    fixed_df = pd.read_csv('data_' + data_base + '.out', sep='\t', encoding='latin1')
    fixed_df.columns = ['Time', 'Power', 'Nan']
    fixed_df = fixed_df.drop(['Nan'], axis=1)
    fixed_df = fixed_df.drop(0, axis=0)
    fixed_df = fixed_df.rename(index = str, columns = {1: 'Power'})    

    f = float(sum(fixed_df['Power'])) / len(fixed_df['Power']) /3.6
    
    return f
    
def find_P_pv_min():
    fixed_df = pd.read_csv('data_pv_min.out', sep='\t', encoding='latin1')
    fixed_df.columns = ['Time', 'Power', 'Nan']
    fixed_df = fixed_df.drop(['Nan'], axis=1)
    fixed_df = fixed_df.drop(0, axis=0)
    fixed_df = fixed_df.rename(index = str, columns = {1: 'Power'})      

    P_pv_min = float(sum(fixed_df['Power'])) / len(fixed_df['Power'])
    
    return P_pv_min
        
def save_plot(Q_1, Q_2, P, f_wanted):
    for i in range(len(f_wanted)):
        plt.figure(i+1)
        plt.scatter(Q_1[i], P[i], label = 'NASA')
        plt.plot(Q_1[i], P[i], label = 'NASA')
        plt.scatter(Q_2[i], P[i], label = 'WRDC')
        plt.plot(Q_2[i], P[i], label = 'WRDC')
        plt.grid(True)
        plt.xlabel(u'Емкость аккумулятора/Пиковая мощность нагрузки, ч')
        plt.ylabel(u'Пиковая мощность фэп/Пиковая мощность нагрузки')
        plt.legend()
        plt.savefig('For f = ' + str(f_wanted[i]) + '.png')
        
def angle_for_Q_min(f_wanted, data_base, P_pv, Q_start, angle):
    angle_down = angle - 15
    angle_up = angle + 20
    Q_min_find = lambda angle_in: Q_finder(angle_in, data_base = data_base, Q_start = Q_start, P_pv = P_pv, f_wanted = f_wanted)
    print(angle)
    res = minimize(Q_min_find, angle, method = 'SLSQP', bounds = ((angle_down, angle_up),), options={'disp': True, 'ftol': 0.001})
    return [res.x, res.fun]


def Q_finder(angle_in, data_base, Q_start, P_pv, f_wanted):
    res = find_min(angle_in[0], Q_start, P_pv, data_base, f_wanted, 0.0001)           
    Q = res.x[0]
    return Q
        
def find_min(angle_in, Q_start, P_pv_cur, data_b, f_want, error):
    print('Start: ', angle_in)
    delta_fun = lambda Q: min_Q(Q, angle = angle_in, P_pv = P_pv_cur, data_base = data_b, f_wanted = f_want)
    res = minimize(delta_fun, Q_start, method = 'Nelder-Mead', options={'disp': True, 'fatol': error})
    #res = minimize(delta_fun, angle_in, method = 'TNC', bounds = ((0, 90), (0, 2*angle_in[1])), options={'disp': False, 'maxiter': maxit})
    return res
    
def lines_for_different_f(Q, f_wanted, P_pv_min, dots_number):    
 
    Q_arr_nasa = [[0] * dots_number for i in range(len(f_wanted))]
    Q_arr_wrdc = [[0] * dots_number for i in range(len(f_wanted))]
    Q_start_nasa = [[Q] * (dots_number + 1) for i in range(len(f_wanted)+1)]
    Q_start_wrdc = [[Q] * (dots_number + 1) for i in range(len(f_wanted)+1)]
    P_pv_arr = [[0] * dots_number for i in range(len(f_wanted))]
    max_f_difference = [0 for i in range(len(f_wanted))]
    
    for i in range(len(f_wanted)):
        if f_wanted[i] < 1:
            result = open('Result_file_for_f_0_' + str(f_wanted[i]*1000) + '.txt', 'w')
        else:
            result = open('Result_file_for_f_1_0.txt', 'w')  
        result.write('Мощность_ФЭМ, Емкость_АКБ_nasa,_ч, Емкость_АКБ_wrdc,_ч\n')
        result.close()
        
    for i in range(dots_number):
        print('\n dot #', i+1)
        for j in range(len(f_wanted)):
            print('f =', f_wanted[j])
            print('\n')
            P_pv_arr[j][i] = ( (1 + 0.00001*i)*P_pv_min*f_wanted[j] )
            if f_wanted[j] < 1:
                result = open('Result_file_for_f_0_' + str(f_wanted[j]*100) + '.txt', 'a')
            else:
                result = open('Result_file_for_f_1_0.txt', 'a')
            
            angle_in = angle_for_Q_min(f_wanted[j], 'NASA', P_pv_arr[j][i], Q_start_nasa[j][i], 57)
                
            Q_arr_nasa[j][i] = angle_in[1]
            Q_start_nasa[j][i+1] = angle_in[1]
            print('Result NASA: ', angle_in[0], angle_in[1])             
                    
            angle_in = angle_for_Q_min(f_wanted[j], 'WRDC', P_pv_arr[j][i], Q_start_wrdc[j][i], 57)           
            
            Q_arr_wrdc[j][i] = angle_in[1]
            Q_start_wrdc[j][i+1] = angle_in[1] 
            print('Result WRDC: ', angle_in[0], angle_in[1])       
            
            P_pv_arr[j][i] /= 3.6
            Q_arr_nasa[j][i] /= 3.6
            Q_arr_wrdc[j][i] /= 3.6
            print(P_pv_arr[j][i])
            result.write("%s " % round(P_pv_arr[j][i], 4))
            result.write("%s " % round(Q_arr_nasa[j][i], 4))
            result.write("%s \n" % round(Q_arr_wrdc[j][i], 4))
            
            result.close()
            
    print(Q_start_wrdc, Q_start_nasa)
  
    save_plot(Q_arr_nasa, Q_arr_wrdc, P_pv_arr, f_wanted)
        
    print('Finish!')

def min_Q(Q, angle, P_pv, data_base, f_wanted):
    # print(Q[0]) и хз, почему это массив
    return abs(f_wanted - find_f(P_pv, Q[0], angle, data_base))

def main():
    print('Start')
    Q = 130 #емкость аккумулятора в кДж
    #f_wanted = [0.999, 0.995, 0.99, 0.95]
    f_wanted = [0.999]
    number_of_lines = 10
    number_of_columns = 10
    dots_number = 5
    
    os.system('C:\Trnsys17\Exe\TRNExe.exe C:\Trnsys17\MyProjects\Project2\Project5.dck /h')
    P_pv_min = find_P_pv_min()  

    lines_for_different_f(Q, f_wanted, P_pv_min, dots_number)

main()

#def f(x, y):
#    return x**2 + y**2

#def delta_f(x_y):
#    return abs(f(x_y[0], x_y[1]))

#x_y = [-12, 18]

#res = minimize(delta_f, x_y, method = 'SLSQP', bounds = ((-20, 5), (-3, 20)), options={'ftol': 0.02, 'disp': True, 'maxiter': 15})

#print(res.x)












