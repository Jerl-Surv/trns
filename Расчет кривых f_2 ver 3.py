import os
import matplotlib.pyplot as plt
import pandas as pd

def in_file(Q_acb, P_pv_max, data_base):
    param_file_name = 'Param_Project2_for_' + data_base + '.txt'
    f = open(param_file_name, 'w')
    f.write('0 57 24 57\n')
    f.write('1 1 3 1 57\n')
    f.write("%s\n" % P_pv_max)
    f.write("%s" % Q_acb)
    
    f.close()

def find_f(P_pv, Q_acb, data_base):
    in_file(Q_acb*3.6, P_pv, data_base)
    
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
    f_data = open('data_pv_min.out', 'r')
    hours_number = 0
    E_pv_sum = 0
    for string in f_data: 
        if (string.find('+') >= 0):
            temp = string.split(' ')[4]
            temp1 = temp[:-2]
            E_pv_sum += float(temp1)
            hours_number += 1
                            
    #print(round(E_load_sum/(hours_number-1)/3.6, 2))
    P_pv_min = (hours_number-1)*3.6*200/E_pv_sum
    
    f_data.close()
    return P_pv_min

def bisection(P, Q, f_wanted):
    Q_1 = 0
    Q_2 = Q
    f_new = 1
    while (f_new > 0.9999*f_wanted) or (f_new < 0.999*f_wanted):
        Q_new = (Q_1 + Q_2)/2
        f_new = find_f(P, Q_new, 'WRDC')
        if f_new > 0.9999*f_wanted:
            Q_2 = Q_new
        if f_new < 0.999*f_wanted:
            Q_1 = Q_new
    return Q_new
        
def graph(Q, P, f_wanted):
    for i in range(len(f_wanted)):
        plt.scatter(Q[i], P[i])
    plt.grid(True)
    plt.xlabel(u'Емкость аккумулятора, кДж')
    plt.ylabel(u'Пиковая мощность фэп, кДж/ч')
    plt.legend()
    plt.show()
    
def graph_df_f(fdf, f):
    df = []
    ddf = []
    for i in range(len(f)):
        df_arr = []
        df_mid_sum = 0
        for j in range(len(fdf[i])):
            df_arr.append(abs(f[i] - fdf[i][j]))
            df_mid_sum += df_arr[j] 
        df.append(df_mid_sum/len(fdf[i]))
        ddf.append(max(df_arr))
    plt.scatter(f, df)
    plt.errorbar(f, df, yerr = ddf, fmt='.-')
    plt.grid(True)
    plt.xlabel(u'f')
    plt.ylabel(u'df')
    plt.legend()
    plt.show()
    
def find_array_f(n, k, P_pv_arr, Q_max, data_base):
    
    Q_arr = [i for i in range(5, Q_max + 1, Q_max // k)]
    
    f = open('Доля покрытия нагрузки ' + data_base + '.csv', 'w')
    f_arr = []
    
    f.write(";")
    for i in range(n):    
        f.write("%s;" % round(P_pv_arr[i], 2))
    f.write('\n')
        
    for i in range(k):
        section = []
        f.write("%s;" % Q_arr[i])
        f_1=False
        for j in range(n):
            if(f_1==False):
                section.append(round(find_f(P_pv_arr[j], Q_arr[i], data_base),3))
                if(section[j]==1.0):
                    f_1=True
            else:
                section.append(1.0)
            f.write("%s;" % round(section[j], 3))
        f_arr.append(section)
        f.write('\n')
    
    

    f.close()    
    return f_arr

def main():
    print('Start')
    Q = 2000 #емкость аккумулятора
    Q_min = 100
    Q_last = []
    P_pv_nom = 200 #пиковая мощность фэп в Ваттах
    P_pv_arr = []
    f_wanted = [1.0, 0.95, 0.9, 0.85]
    n = 36
    k = 32 
    f_in_nasa = [[0] * n for i in range(k)]
    f_in_wrdc = [[0] * n for i in range(k)]
    delta_f = [[0] * n for i in range(k)]
    
    os.system('C:\Trnsys17\Exe\TRNExe.exe C:\Trnsys17\MyProjects\Project2\Project5.dck /h')
    P_pv_min = find_P_pv_min()  
    P_pv_arr = []
    for i in range(n):
        P_pv_arr.append((0.4+0.2*i)*P_pv_min)
#        f_arr.append(find_f(P_pv_arr[i],1000))    
    
    f = open('Относительная погрешность f.csv', 'w')
    f.write(";")
        
    f_in_nasa = find_array_f(n, k, P_pv_arr, Q, 'NASA')
    f_in_wrdc = find_array_f(n, k, P_pv_arr, Q, 'WRDC')
    for i in range(n):    
        f.write("%s;" % round(P_pv_arr[i], 2))
    f.write('\n')
    
    Q_arr = [i for i in range(5, Q + 1, Q // k)]
    
    for i in range(k):
        f.write("%s;" % Q_arr[i])
        for j in range(n):
            delta_f[i][j] = (f_in_nasa[i][j] - f_in_wrdc[i][j])/f_in_wrdc[i][j]
            f.write("%s;" % round(delta_f[i][j], 3))
        f.write('\n')

    f.close()
    
    print('Finish!')
    
    
    '''
    dots_number = 5
    
    Q_arr = [[0] * dots_number for i in range(len(f_wanted))]
    P_pv_arr = [[0] * dots_number for i in range(len(f_wanted))]
    
    for i in range(len(f_wanted)):
        if f_wanted[i] < 1:
            result = open('Result_file_for_f_0_' + str(f_wanted[i]*100) + '.txt', 'w')
        else:
            result = open('Result_file_for_f_1_0.txt', 'w')  
        result.write('Мощность_ФЭМ,_Вт Емкость_АКБ,_Вт_ч Доля_покрытия')
        result.close()
        
        
    for i in range(dots_number):
        for j in range(len(f_wanted)):
            P_pv_arr[j][i] = ( (1+0.2*i)*P_pv_min*f_wanted[j] )
            if f_wanted[j] < 1:
                result = open('Result_file_for_f_0_' + str(f_wanted[j]*100) + '.txt', 'a')
            else:
                result = open('Result_file_for_f_1_0.txt', 'a')
            
            result.write("%s " % round(P_pv_arr[j][i], 4))
                
            if i == 0:
                Q_arr[j][i] = ( bisection(P_pv_arr[j][i], Q, f_wanted[j]) )
                print('Расчет ', j)
                Q = Q_arr[j][i]
                Q_last.append(Q)
                f_in_nasa.append([])
            else:
                Q_arr[j][i] = ( bisection(P_pv_arr[j][i], Q_last[j], f_wanted[j]) )
                Q_last[j] = Q_arr[j][i]
                
            
            result.write("%s " % round(Q_arr[j][i], 4))
            #f_in_nasa[j].append(find_f(P_pv_arr[j][i], Q_arr[j][i], 'NASA'))
            result.write("%s\n" % round(find_f(P_pv_arr[j][i], Q_arr[j][i], 'NASA'), 4))
            
            result.close()
  

    graph(Q_arr, P_pv_arr, f_wanted)
    #graph_df_f(f_in_nasa, f_wanted)
      
'''
    
main()



