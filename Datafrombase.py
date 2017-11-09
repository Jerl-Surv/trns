import math
import os
from datetime import datetime, date, time
import numpy as np

import psycopg2
import util_pg_ver2

def switch_start_simulation_time(moment):
    Minutes = float(str(datetime.time(moment))[3:5])
    Hour = float(str(datetime.time(moment))[0:2])
    Day = float(str(datetime.date(moment))[8:])
    Month = float(str(datetime.date(moment))[5:7])
	
    days_in_month = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    days_from_year_start_to_curr_month = 0
    for i in range(int(Month)):
        if i != 0:
            days_from_year_start_to_curr_month += days_in_month[i]
	
    start_simulation_time = (days_from_year_start_to_curr_month + Day - 1)*24 + Hour + round(Minutes/60, 8)# в часах
	
    #file_name = 'C:\Trnsys17\MyProjects\Project\Project_' + stantion + '.dck'
	
    f = open(r'C:\Trnsys17\MyProjects\Project\Start_simulation_file.txt', 'w')
    f.write(str(start_simulation_time))
    f.close()

def CheckPass(CurMoment, PrevMoment):
        answer = False
        CurMinutes = float(str(datetime.time(CurMoment))[3:5])
        PrevMinutes = float(str(datetime.time(PrevMoment))[3:5])

        CurHour = float(str(datetime.time(CurMoment))[0:2])
        PrevHour = float(str(datetime.time(PrevMoment))[0:2])

        CurDay = float(str(datetime.date(CurMoment))[8:])
        PrevDay = float(str(datetime.date(PrevMoment))[8:])

        CurMonth = float(str(datetime.date(CurMoment))[5:7])
        PrevMonth = float(str(datetime.date(PrevMoment))[5:7])

        CurYear = float(str(datetime.date(CurMoment))[0:4])
        PrevYear = float(str(datetime.date(PrevMoment))[0:4])

        day_in_month = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        #print('Data: ', CurMoment, ', current interval: ', 24*60*CurDay - 24*60*PrevDay + 60*CurHour - 60*PrevHour + CurMinutes - PrevMinutes, '\n')
        if (24*60*CurDay - 24*60*PrevDay + 60*CurHour - 60*PrevHour + CurMinutes - PrevMinutes) == 2:
                answer = True
        if (CurDay == 1) and (PrevDay == day_in_month[PrevMonth]) and (CurHour == 0) and (PrevHour == 23) and ((60 - PrevMinutes + CurMinutes) == 2):
                if (CurYear == PrevYear) and (CurMonth == PrevMonth + 1):		
                        answer = True
                if (CurYear == PrevYear + 1) and (CurMonth == 1) and (PrevMonth == 12):
                        answer = True
        if (CurMonth == 2) and (CurDay == 29):
                answer = True

        return answer

try:
        conn = util_pg_ver2.get_conn(psycopg2)
        print("Meteo has connected...")
except:
        print("It is unable to connect to the database")
cur = conn.cursor()

stantion_dataframe = {12: 'Astrahan', 18: 'Vladivostok', 20: 'Gorno-Altaisk', 14: 'Mahachkala', 8: 'Ufa', 1: 'S-Peterburg', 16: 'Yakutsk'}
stantion_id_array = stantion_dataframe.keys()

for i, id_st in enumerate(stantion_id_array):
        cur.execute('SELECT weather."DateTime", weather.intensity, weather.temperature FROM public.weather WHERE weather.fromflash = 1 AND weather."ServerId" = %s ORDER BY weather."DateTime" ASC;'%(id_st))
    
        f = open(r'C:\Trnsys17\MyProjects\Project\Data_' + stantion_dataframe[id_st] + '.txt', 'w')
        line_cash = 0
        trnsys_start_comand = 'C:\Trnsys17\Exe\TRNExe.exe C:\Trnsys17\MyProjects\Project\Project_' + stantion_dataframe[id_st] + '.dck /h'
        r_file = open(r'C:\Trnsys17\MyProjects\Project\result_file_' + stantion_dataframe[id_st] + '.txt', 'w')
        r_file.close()
        for idx, line in enumerate(cur): # line[0] - дата, line[1] -  интенсивность излучения, line[2] = температура
                if (idx != 0):
                        if line[0] != line_cash:
                                if (CheckPass(line[0], line_cash) == False): # дыра в измерениях
                                        f.close()
                                        os.system(trnsys_start_comand)
                                        r_c_file = open(r'C:\Trnsys17\MyProjects\Project\result_cash_file_' + stantion_dataframe[id_st] + '.out', 'r')
                                        r_file = open(r'C:\Trnsys17\MyProjects\Project\result_file_' + stantion_dataframe[id_st] + '.txt', 'a')
                                        for string in r_c_file:
                                            r_file.write(str(string) + '\n')
                                        r_c_file.close()
                                        r_file.close()
                                        print('Line #', idx, ', date ', line[0])
                                        switch_start_simulation_time(line[0])
                                        f = open(stantion_dataframe[id_st] + '.txt', 'w')
                                f.write(str(line[1]) + '\t' + str(float(line[2]) + 273.0) + '\n')
                else:
                    switch_start_simulation_time(line[0])

                line_cash = line[0]
        f.close()
        os.system('C:\Trnsys17\Exe\TRNExe.exe C:\Trnsys17\MyProjects\Project2\Project2_for_NASA.dck /h')
        print(stantion_dataframe[id_st] + ' file has generated')

conn.close()

