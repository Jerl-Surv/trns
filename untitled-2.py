from scipy.integrate import odeint
import pandas as pd
import Angle_solver as ang_slv
import numpy as np
from datetime import datetime, date, time
import os
from scipy.optimize import minimize
from scipy.interpolate import UnivariateSpline

def data_for_station(station_name):
    #Staton name: [latitude, longitude]
    data_frame_stations = ({'ALEXANDROVSKOE': [60.43, 77,87], "ARKHANGEL'SK": [64.58, 40.50], 'CHETYREKH-STOLBOVOI IS.': [70.63, 162.40], 
                            'CHITA': [52.02, 113.33], 'DICKSON IS.': [73.50, 80.40], 'EKATERINBURG': [56.80, 60.63], 'FEDOROV OBS.': [77.72, 104.28], 
                            'IRKUTSK': [52.27, 104.35], 'KHABAROVSK': [48.52, 135.17], 'KOTELNY IS.': [76.00, 137.90], 'KRENKEL OBS.': [80.62, 58.05], 
                            'MIRNY': [-66.55, 93.02], 'MOSCOW / PODMOSKOVNAYA': [55.72, 37.20], 'MOSCOW UNIV.': [55.70, 37.50], 'OIMYAKON': [63.27, 143.15],
                            'NOVOLAZAREVSKAYA': [-70.77, 11.83], 'OKHOTSK': [59.37, 143.20], 'OLENEK': [68.50, 112.43], 'OMSK': [54.93, 73.40],
                            'PETROPAVLOVSK-KAMCHATSKI': [52.97, 158.75], 'SAMARA': [53.25, 50.45], 'ST.PETERSBURG / VOEIKOVO': [59.97, 30.30], 
                            'TURUKHANSK': [65.78, 87.95], 'VANAVARA': [60.33, 102.27], 'VERKHOYANSK': [67.55, 133.38], 'VLADIVOSTOK': [43.12, 131.90], 
                            'VOSTOK': [-78.45, 106.87], 'WRANGEL IS.': [70.98, -178.65], 'YAKUTSK': [62.08, 129.75], 'YUZHNO-SAKHALINSK': [46.92, 142.73]})
    return data_frame_stations[station_name]
    
def pv_simple(P_pv_max, radiation):
    P_pv = {}
    radiation_nasa = np.array(radiation.get('NASA'))
    radiation_wrdc = np.array(radiation.get('WRDC'))
    P_pv['NASA'] = radiation_nasa*P_pv_max/1000
    P_pv['WRDC'] = radiation_wrdc*P_pv_max/1000
    return P_pv
    
def controler_simple(P_load_max, P_pv, Q_acb):
    dt = 1
    E_in_bat_NASA = [Q_acb for i in range(len(P_pv['NASA']) + 1)]
    E_in_bat_WRDC = [Q_acb for i in range(len(P_pv['WRDC']) + 1)]
    P_load = P_pv
    
    # NASA
    P_bat_wanted = [(P_pv['NASA'][i] - P_load_max) for i in range(len(P_pv['NASA']))]
    
    result = open('P_wanted_from_bat_NASA_data.txt', 'w') 
    result.write('P_w_N' + '\n')
    for i in range(100):
        result.write(str(P_bat_wanted[i]) + '\n')    
    
    result.close()
    
    P_from_bat = -1*np.array(battery_simple(Q_acb, P_bat_wanted))
    
    print(np.shape(P_from_bat))
        
    for i in range(len(P_pv['NASA'])): 
        print(P_pv['NASA'][i], P_from_bat[i])
        if (P_load_max <= P_pv['NASA'][i]):
            P_load['NASA'][i] = P_load_max
        else:
            P_from_bat = P_from_bat[i][0]
            P_load['NASA'][i] = min(P_pv['NASA'][i] + P_from_bat[i][0], P_load_max)
            
    # WRDC
    P_bat_wanted = [(P_pv['WRDC'][i] - P_load_max) for i in range(len(P_pv['WRDC']))]
    P_from_bat = - battery_simple(Q_acb, P_bat_wanted)
                
    for i in range(len(P_pv['WRDC'])):        
        if (P_load_max <= P_pv['WRDC'][i]):
            P_load['WRDC'][i] = P_load_max
        else:
            P_from_bat = P_from_bat[i]
            P_load['WRDC'][i] = min(P_pv['WRDC'][i] + P_from_bat, P_load_max) 

    return P_load

def P_in_bat(E, t, P_w, Q_acb):    
    if (int(t) != 0):
        t_spl = [int(t) - 1, int(t), int(t) + 1]
        P_w_spl = [P_w[int(t) - 1], P_w[int(t)], P_w[int(t) + 1]]
    else:
        t_spl = [int(t), int(t) + 1, int(t) + 2]
        P_w_spl = [P_w[int(t)], P_w[int(t) + 1], P_w[int(t) + 2]]            
    
    if (P_w_spl[0] == P_w_spl[1] == P_w_spl[2]):
        smooth_param = 1
    else:
        smooth_param = 2
    spl = UnivariateSpline(t_spl, P_w_spl, k = smooth_param)
    P = spl(t)  
    return P
    
def battery_simple(Q_ac, P_w):
    n = len(P_w)
    P_w = np.array(list(P_w) + [0])
    t_arr = [i for i in range(n)]
    
    chunck_size = 200
    iterations = int(n*0.005)
    last_chunck = n - iterations*chunck_size
    P_from_bat = [[] for i in range(iterations + 1)]
    print('First time of derivative computation\n')
    
    for chunck in range(iterations + 1):
        if (chunck != iterations):
            array_size = chunck_size
        else:
            array_size = last_chunck
            
        P_w_chunck = np.array(list(P_w[array_size*chunck:array_size*(chunck+1)]) + 2*n*[0])
        t_arr_chunck = np.array(list(t_arr[array_size*chunck:array_size*(chunck+1)]))
        E_in_bat_chunck = np.ravel(odeint(P_in_bat, Q_ac, t_arr_chunck, args = (P_w_chunck, Q_ac,))) 
        #print('Sizes: ' + str(len(P_w_chunck) - 2*n) + str(len(t_arr_chunck)) + str(len(E_in_bat_chunck)) + '\n')
        #print(P_w_chunck[:20], t_arr_chunck[:20], E_in_bat_chunck[:20])
        
        for i in range(array_size):
            if (E_in_bat_chunck[i] < 0):
                #print('Less 0, just ' + str(i) + ' \n')
                E_in_bat_chunck = np.hsplit(E_in_bat_chunck, (i,))
                P_w_cash = np.hsplit(P_w_chunck, (i,))[1]
                #t_cash = np.array([(i + j) for j in range(n - i)])
                t_cash = np.hsplit(t_arr_chunck, (i,))[1]
                E_in_bat_cash = np.ravel(odeint(P_in_bat, 0, t_cash, args = (P_w_cash, Q_ac,)))
                E_in_bat_chunck = np.array( list(E_in_bat_chunck[0]) + list(E_in_bat_cash) )           
         
            if (E_in_bat_chunck[i] > Q_ac):
                #print('More max, just ' + str(i) + '\n')
                E_in_bat_chunck = np.hsplit(E_in_bat_chunck, (i,))
                P_w_cash = np.hsplit(P_w, (i,))[1]
                t_cash = np.hsplit(t_arr_chunck, (i,))[1]
                E_in_bat_cash = np.ravel(odeint(P_in_bat, Q_ac, t_cash, args = (P_w_cash, Q_ac,)))
                E_in_bat_chunck = np.array( list(E_in_bat_chunck[0]) + list(E_in_bat_cash) ) 
                
            if (i != 0):
                P_from_bat[chunck].append(E_in_bat_chunck[i] - E_in_bat_chunck[i-1])
        #print(P_from_bat[chunck])
    
    return np.ravel(np.array(P_from_bat))  

def read_data():
    nasa_data = pd.read_csv('data_sum_r_NASA.txt', sep='\t', encoding='latin1')
    nasa_data.columns = ['NASA'] 
    wrdc_data = pd.read_csv('data_sum_r_WRDC.txt', sep='\t', encoding='latin1')
    wrdc_data.columns = ['WRDC']  
    #nasa_and_wrdc_data = pd.join(wrdc_data, nasa_data)
    nasa_and_wrdc_data = pd.merge(wrdc_data, nasa_data, left_index=True, right_index=True)
    #nasa_and_wrdc_data = nasa_data.merge(wrdc_data, 'left', on='NASA')
    #nasa_and_wrdc_data = nasa_data.insert(1, 'WRDC', wrdc_data)
    # на выходе данные в виде двух столбцов с названиями 'NASA' и 'WRDC'
    return nasa_and_wrdc_data

def P_pv_min_scheme(P_load_max, angle, params, station_name):
    radiation = {}
    dt = 1 # данные с шагом в 1 час
    P_pv_max = 100 # Вт, пиковая мощность фэп
    nasa_and_wrdc_data = read_data() # два столбца: 'NASA' и 'WRDC', сырые данные по радиации из баз данных
    # t_array = [i for i in range(len(nasa_and_wrdc_data['NASA']))]
    radiation['NASA'] = ang_slv.sum_radiation(nasa_and_wrdc_data['NASA'], angle, data_for_station(station_name)) #столбец 'NASA'; пересчитанные данные с горизонтали на угол
    radiation['WRDC'] = ang_slv.sum_radiation(nasa_and_wrdc_data['WRDC'], angle, data_for_station(station_name)) #столбец 'WRDC'; пересчитанные данные с горизонтали на угол
    P_pv = pv_simple(P_pv_max, radiation) # два столбца: 'NASA' и 'WRDC'; выходная мощность с фэп
    return P_pv
             
def main_scheme(P_pv_max, Q_acb, angle, params, station_name):
    radiation = {}
    f_step = {}
    dt = 1 # данные с шагом в 1 час
    P_load_max = 1 # Вт, пиковая мощность нагрузки
    nasa_and_wrdc_data = read_data()/3.6 # два столбца: 'NASA' и 'WRDC', сырые данные по радиации из баз данных, в Вт/м^2
    print('Reading data is completed\n')
    # t_array = [i for i in range(len(nasa_and_wrdc_data['NASA']))]
    radiation['NASA'] = ang_slv.sum_radiation(nasa_and_wrdc_data['NASA'], angle, data_for_station(station_name)) #столбец 'NASA'; пересчитанные данные с горизонтали на угол
    radiation['WRDC'] = ang_slv.sum_radiation(nasa_and_wrdc_data['WRDC'], angle, data_for_station(station_name)) #столбец 'WRDC'; пересчитанные данные с горизонтали на угол
    print('Computation from gorisontal is completed\n')
    P_pv = pv_simple(P_pv_max, radiation) # два столбца: 'NASA' и 'WRDC'; выходная мощность с фэп
    print('Computation power from pv is completed\n')
    P_load = controler_simple(P_load_max, P_pv, Q_acb) # два столбца: 'NASA' и 'WRDC'; мощность, поступающая на нагрузку
    print(P_load)
    return P_load

def in_file(Q_acb, P_pv_max, angle, data_base):
    param_file_name = 'Param_Project2_for_' + data_base + '.txt'
    f = open(param_file_name, 'w')
    f.write('0 ' + str(angle) + ' 24 ' + str(angle) + '\n')
    f.write('1 1 3 1 ' + str(angle) + '\n')
    f.write("%s\n" % P_pv_max)
    f.write("%s" % Q_acb)
    
    f.close()

def find_P_load(P_pv, Q_acb, angle, data_base):
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
    
    return fixed_df['Power']

#now_date_0 = float(now_date[0:2])*3600 + float(now_date[3:5])*60 + float(now_date[6:])
# TRNSYS
#P_load_trns_nasa = find_P_load(300, 180*3.6, 57, 'NASA')
#P_load_trns_wrdc = find_P_load(300, 180*3.6, 57, 'WRDC')

#now_date = str(datetime.time(datetime.now()))
#now_date_1 = float(now_date[0:2])*3600 + float(now_date[3:5])*60 + float(now_date[6:])
# Python-scheme

a = np.array([[1, 1, 1], [1, 1, 1]])
print(np.shape(a))


params = ang_slv.parameters()
P_load_sch = main_scheme(300, 180, 57, params, 'MOSCOW UNIV.')

now_date = str(datetime.time(datetime.now()))
now_date_2 = float(now_date[0:2])*3600 + float(now_date[3:5])*60 + float(now_date[6:])

print('Trnsys time: ', (now_date_1 - now_date_0), 'Python-scheme time: ', (now_date_2 - now_date_1))


result = open('Result_file_scheme_and_trnsys.txt', 'w') 
result.write('N_d' + '\t' + 'W_d' + '\t' + 'N_sch' + '\t' + 'W_sch' + '\t' + 'N_trns' + '\t' + 'W_trns' + '\n')
print(P_load_sch)
for i in range(500):
    result.write(str(read_data()['NASA'][i])+ '\t' + str(read_data()['WRDC'][i]) + '\t' + 
                 str(P_load_sch['NASA'][i]) + '\t' + str(P_load_sch['WRDC'][i]) + '\t' + 
                 str(P_load_trns_nasa[i]) + '\t' + str(P_load_trns_wrdc[i]) + '\n')
result.close()


