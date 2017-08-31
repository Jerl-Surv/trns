import os
import matplotlib
import matplotlib.pyplot as plt
import math
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import minimize_scalar
from scipy.integrate import odeint
import Angle_solver as ang_slv
import Scheme as shm

params = ang_slv.parameters()

def input_radiation_files_generator():
    push
    
def in_file(Q_acb, P_pv_max, angle, data_base):
    param_file_name = 'Param_Project2_for_' + data_base + '.txt'
    f = open(param_file_name, 'w')
    f.write('0 ' + str(angle) + ' 24 ' + str(angle) + '\n')
    f.write('1 1 3 1 ' + str(angle) + '\n')
    f.write("%s\n" % P_pv_max)
    f.write("%s" % Q_acb)
    
    f.close()

def find_f(P_pv, Q_acb, angle, data_base, station_name):
    global params
    # in_file(Q_acb, P_pv, angle, data_base)
    
    # запуск схемы
    shm.main_scheme(P_pv, Q_acb, angle, params, station_name)
    
    fixed_df = pd.read_csv('data_' + data_base + '.out', sep='\t', encoding='latin1')
    fixed_df.columns = ['Time', 'Power', 'Nan']
    fixed_df = fixed_df.drop(['Nan'], axis=1)
    #fixed_df = fixed_df.drop(0, axis=0)
    fixed_df = fixed_df.rename(index = str, columns = {1: 'Power'})    

    f = float(sum(fixed_df['Power'])) / len(fixed_df['Power']) /3.6
    
    return f
    
def find_P_pv_min(station_name, angl_params):
    power = shm.P_pv_min_scheme(200, shm.data_for_station(station_name)[0], angl_params, station_name)    
    P_pv_min = [float(sum(power['NASA'])) / len(power['NASA']), float(sum(power['WRDC'])) / len(power['WRDC'])]
    
    return P_pv_min
        
def save_plot(Q_1, Q_2, P, f_wanted):
    for i in range(len(f_wanted)):
        plt.figure(i+1)
        plt.scatter(Q_1[i], P[i], label = 'NASA')
        plt.plot(Q_1[i], P[i], label = 'NASA')
        #Q_fit_1 = least_squares(fun_rosenbrock, x0_rosenbrock)
        #plt.plot(Q_fit_1.x, P[i], label='fitted model NASA')
        plt.scatter(Q_2[i], P[i], label = 'WRDC')
        plt.plot(Q_2[i], P[i], label = 'WRDC')
        #Q_fit_2 = least_squares(fun_rosenbrock, x0_rosenbrock)
        #plt.plot(Q_fit_2.x, P[i], label='fitted model WRDC')
        plt.grid(True)
        plt.xlabel(u'Емкость аккумулятора/Пиковая мощность нагрузки, ч')
        plt.ylabel(u'Пиковая мощность фэп/Пиковая мощность нагрузки')
        plt.legend()
        plt.savefig('For f = ' + str(f_wanted[i]) + '.png')
        
def find_min(angle_in, P_pv_cur, data_b, f_want, maxit, station_name):
    print('Start: ', angle_in[1])
    delta_fun = lambda angle_Q: min_angle_and_Q(angle_Q, P_pv = P_pv_cur, data_base = data_b, f_wanted = f_want, station_name = station_name)
    res = minimize(delta_fun, angle_in, method = 'Nelder-Mead', options={'disp': False, 'maxiter': maxit})
    #res = minimize(delta_fun, angle_in, method = 'TNC', bounds = ((0, 90), (0, 2*angle_in[1])), options={'disp': False, 'maxiter': maxit})
    return res
    
def lines_for_different_f(Q, f_wanted, P_pv_min, dots_number, lattitude, station_name):    
 
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
            #  if (i != 0 and P_pv_arr[j][i])
            print(i, j, P_pv_min, f_wanted[j])
            P_pv_arr[j][i] = ( (1 + 0.00001*i)*P_pv_min[j]*f_wanted[j] )
            if f_wanted[j] < 1:
                result = open('Result_file_for_f_0_' + str(f_wanted[j]*100) + '.txt', 'a')
            else:
                result = open('Result_file_for_f_1_0.txt', 'a')
            
            angle_in = [57, 0.8*Q_start_nasa[j][i]*f_wanted[j]]
            res = find_min(angle_in, P_pv_arr[j][i], 'NASA', f_wanted[j], 10, station_name)           
            
            count_error_1 = False
            count_error_2 = False
            if np.all(res.fun > 0.01 and i != 0 and count_error_1 == False):
                angle_in = [57, 0.2*Q_start_nasa[j][i]*f_wanted[j]]
                res = find_min(angle_in, P_pv_arr[j][i], 'NASA', f_wanted[j], 20, station_name)
                count_error_2 = True
            if np.all(res.fun > 0.001 and i != 0 and count_error_1 == False):
                angle_in = [57, 0.05*Q_start_nasa[j][i]*f_wanted[j]]
                res = find_min(angle_in, P_pv_arr[j][i], 'NASA', f_wanted[j], 30, station_name)
                count_error_1 = True            
            
            Q_arr_nasa[j][i] = res.x[1]
            Q_start_nasa[j][i+1] = res.x[1]
            print('Result NASA: ', res.x[0], res.x[1], res.fun)             
            
            angle_in = [57, 0.8*Q_start_wrdc[j][i]*f_wanted[j]]
            res = find_min(angle_in, P_pv_arr[j][i], 'WRDC', f_wanted[j], 10, station_name)
            
            count_error_1 = False
            count_error_2 = False
            if np.all(res.fun > 0.01 and i != 0 and count_error_1 == False):
                angle_in = [57, 0.2*Q_start_wrdc[j][i]*f_wanted[j]]
                res = find_min(angle_in, P_pv_arr[j][i], 'WRDC', f_wanted[j], 20, station_name)
                count_error_2 = True
            if np.all(res.fun > 0.001 and i != 0 and count_error_1 == False):
                angle_in = [57, 0.05*Q_start_wrdc[j][i]*f_wanted[j]]
                res = find_min(angle_in, P_pv_arr[j][i], 'WRDC', f_wanted[j], 30, station_name)
                count_error_1 = True        
            
            Q_arr_wrdc[j][i] = res.x[1]
            Q_start_wrdc[j][i+1] = res.x[1]  
            print('Result WRDC: ', res.x[0], res.x[1], res.fun)       
            
            P_pv_arr[j][i] /= 3.6
            Q_arr_nasa[j][i] /= 3.6
            Q_arr_wrdc[j][i] /= 3.6
            result.write("%s " % round(P_pv_arr[j][i], 4))
            result.write("%s " % round(Q_arr_nasa[j][i], 4))
            result.write("%s \n" % round(Q_arr_wrdc[j][i], 4))
            
            if (max_f_difference[j] < abs(res.fun)):
                max_f_difference[j] = abs(res.fun) 
            result.write("%s \n" % round(max_f_difference[j], 5))
            
            result.close()
            
    print(Q_start_wrdc, Q_start_nasa)
  
    save_plot(Q_arr_nasa, Q_arr_wrdc, P_pv_arr, f_wanted)
        
    print('Finish!')

def min_angle_and_Q(angle_Q, P_pv, data_base, f_wanted, station_name):
    return abs(f_wanted - find_f(P_pv, angle_Q[1], angle_Q[0], data_base, station_name))

def main():
    print('Start')
    Q = 130 #емкость аккумулятора в кДж
    f_wanted = [0.999]
    number_of_lines = 10
    number_of_columns = 10
    dots_number = 15 
    station_name = 'MOSCOW UNIV.'
    station_info = shm.data_for_station(station_name)
    
    # input_radiation_files_generator()
    
    # расчет угловых параметров
    angl_params = ang_slv.parameters()
    
    P_pv_min = find_P_pv_min(station_name, angl_params) # формат вывода (???)

    lines_for_different_f(Q, f_wanted, P_pv_min, dots_number, station_name, ) # разобраться с передачей данных

main()












