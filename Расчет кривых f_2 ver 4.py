import os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import minimize

def in_file(Q_acb, P_pv_max, angle, data_base):
    param_file_name = 'Param_Project2_for_' + data_base + '.txt'
    f = open(param_file_name, 'w')
    f.write('0 57 24 ' + str(angle) + '\n')
    f.write('1 1 3 1 ' + str(angle) + '\n')
    f.write("%s\n" % P_pv_max)
    f.write("%s" % Q_acb)
    
    f.close()

def find_f(P_pv, Q_acb, angle, data_base):
    in_file(Q_acb*3.6, P_pv, angle, data_base)
    
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

    P_pv_min = len(fixed_df['Power']) * 3.6 * 200 / float(sum(fixed_df['Power']))
    
    return P_pv_min
        
def graph(Q, P, f_wanted):
    for i in range(len(f_wanted)):
        plt.plot(Q[i], P[i])
        plt.grid(True)
        plt.xlabel(u'Емкость аккумулятора, кДж')
        plt.ylabel(u'Пиковая мощность фэп, кДж/ч')
        plt.legend()
        plt.savefig('For f = ' + str(f_wanted) + '.png')
    
def plot_df(Q_arr, P_pv_arr, delta):    
    matplotlib.rcParams['xtick.direction'] = 'out'
    matplotlib.rcParams['ytick.direction'] = 'out'
    
    x = Q_arr
    y = P_pv_arr
    Z = delta
    f_f = False
              
    X, Y = np.meshgrid(x, y)
    
    plt.figure()
    CS = plt.contour(X, Y, Z)
    plt.clabel(CS, inline=1, fontsize=10)
    plt.title('Greed for delta')
    
    plt.savefig('Greed for delta.png')   

def lines_for_different_f(Q, f_wanted, P_pv_min, dots_number):    
    Q_last = []
    P_pv_arr = []   
    
    Q_arr = [[0] * dots_number for i in range(len(f_wanted))]
    Q_start = [Q for i in range(len(f_wanted))]
    P_pv_arr = [[0] * dots_number for i in range(len(f_wanted))]
    
    for i in range(len(f_wanted)):
        if f_wanted[i] < 1:
            result = open('Result_file_for_f_0_' + str(f_wanted[i]*100) + '.txt', 'w')
        else:
            result = open('Result_file_for_f_1_0.txt', 'w')  
        result.write('Мощность_ФЭМ,_Вт Емкость_АКБ,_Вт_ч Доля_покрытия')
        result.close()
        
        
    for i in range(dots_number):
        print('dot #: ', i)
        for j in range(len(f_wanted)):
            angle_in = [57, Q_start[j]]
            print('f = ', j)
            print('\n')
            P_pv_arr[j][i] = ( (1+0.1*i)*P_pv_min*f_wanted[j] )
            if f_wanted[j] < 1:
                result = open('Result_file_for_f_0_' + str(f_wanted[j]*100) + '.txt', 'a')
            else:
                result = open('Result_file_for_f_1_0.txt', 'a')
            
            result.write("%s " % round(P_pv_arr[j][i], 4))
                
            #if i == 0:
                #Q_arr[j][i] = ( bisection(P_pv_arr[j][i], Q, f_wanted[j]) )
                #print('Расчет ', j)
                #Q = Q_arr[j][i]
                #Q_last.append(Q)
            #else:
                #Q_arr[j][i] = ( bisection(P_pv_arr[j][i], Q_last[j], f_wanted[j]) )
                #Q_last[j] = Q_arr[j][i]
            
            delta_fun = lambda angle_Q: min_angle_and_Q(angle_Q, P_pv = P_pv_arr[j][i], data_base = 'NASA', f_wanted = f_wanted[j])
            res = minimize(delta_fun, angle_in, method = 'COBYLA', bounds = ((0, 180), (0.2*Q, Q)), options={'disp': True, 'maxiter': 5})
            Q_arr[j][i] = res.x[1]
            print('Result: ', res.x[1])    
            
            result.write("%s " % round(Q_arr[j][i], 4))
            
            result.close()
            Q_start[j] = res.x[1]
        
  
    graph(Q_arr, P_pv_arr, f_wanted)
        
    print('Finish!')

def min_angle_and_Q(angle_Q, P_pv, data_base, f_wanted):
    return f_wanted - find_f(P_pv, angle_Q[1], angle_Q[0], data_base)


def delta(angle, P_pv, Q_acb):
    return (find_f(P_pv, Q_acb, angle, 'NASA') - find_f(P_pv, Q_acb, angle, 'WRDC'))/find_f(P_pv, Q_acb, angle, 'WRDC')

def grid_for_df(Q, P_pv_min, number_of_lines, number_of_columns):

    delta_f = [[0] * number_of_lines for i in range(number_of_columns)]
    
    print('Start grid\n')
    
    P_pv_arr = []
    for i in range(number_of_lines):
        P_pv_arr.append((0.001+0.001*i)*P_pv_min)

    f = open('Относительная погрешность f.csv', 'w')
    f.write(";")

    for i in range(number_of_lines):    
        f.write("%s;" % round(P_pv_arr[i], 2))
    f.write('\n')
    
    Q_arr = [i for i in range(10, Q + 1, Q // number_of_columns)]
    
    for i in range(number_of_columns):
        print('column #', i)
        f.write("%s;" % Q_arr[i])
        angle_in = 57
        f_1 = False
        for j in range(number_of_lines):
            print('line #', j)
            print('\n')            
            if (f_1 == True):
                delta_f[i][j] = 0
            else:
                delta_fun = lambda angle: delta(angle, P_pv = P_pv_arr[j], Q_acb = Q_arr[i])
                res = minimize(delta_fun, angle_in, method = 'COBYLA', bounds = (0, 180), options={'disp': True, 'maxiter': 3})
                #callback, **options
                delta_f[i][j] = res.fun
                if (delta_f[i][j] == 0):
                    f_1 = True
                print(type(delta_f[i][j]))
                #delta(P_pv, Q_acb, angle)
                print('Finish angle is: ', res.x, '\n')
            f.write("%s;" % round(delta_f[i][j], 3))
        f.write('\n')  

    f.close()
    
    plot_df(Q_arr, P_pv_arr, delta_f)
    
    print('Finish!')

def main():
    print('Start')
    Q = 30 #емкость аккумулятора
    P_pv_nom = 200 #пиковая мощность фэп в Ваттах
    f_wanted = [1.0, 0.9]
    number_of_lines = 10
    number_of_columns = 10
    dots_number = 8
    
    os.system('C:\Trnsys17\Exe\TRNExe.exe C:\Trnsys17\MyProjects\Project2\Project5.dck /h')
    P_pv_min = find_P_pv_min()  

    lines_for_different_f(Q, f_wanted, P_pv_min, dots_number)
    
    #grid_for_df(Q, P_pv_min, number_of_lines, number_of_columns)
    
main()











