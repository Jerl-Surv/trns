# Жизнь - боль. Но мы справимся.
import math
import numpy as np

def parameters():
    params = {}
    B = np.array([n*360/365 for n in range(365)])
    # склонение (массив длиной 365)
    delta = 0.006918 - 0.399912*np.cos(B) + 0.070257*np.sin(B) - 0.006758*np.cos(2*B) + 0.000907*np.sin(2*B) - 0.002679*np.cos(3*B) + 0.00148*np.sin(3*B)
    params['delta'] = delta # массив 365
    # часовой угол
    omega_day = np.array([( 15 * i * math.pi / 180 - math.pi) for i in range(24)]) # массив 24
    omega_year = np.array([omega_day for i in range(365)]) # массив 24*365
    #params['omega'] = np.ravel(omega_year) # массив для года
    #params['omega 1'] = np.ravel(omega_year)
    params['omega'] = omega_day # массив для дня 24
    params['omega 1'] = omega_day # массив 24    
    omega_day_2 = np.array([( ((i + 1) * 15 * math.pi) / 180 - math.pi ) for i in range(24)]) # массив 24
    omega_year_2 = np.array([omega_day_2 for i in range(365)]) # массив 24*365
    #params['omega 2'] = np.ravel(omega_year_2)
    params['omega 2'] = np.ravel(omega_day_2) # массив 24
    return params

def k_t(r_data, years, lattitude, params): # индекс ясности
    G_sc = 1367 # солнечная постоянная, Вт/м^2
    # phi - широта местности (рад.)
    phi = lattitude*math.pi/180 
    theta_z = np.array([ [( math.cos(phi)*math.cos(params['delta'][i])*math.cos(params['omega'][j]) + math.sin(phi)*math.sin(params['delta'][i]) ) 
                          for j in range(24)] for i in range(365)] ) # массив 365*24
    # заатмосферное излучение
    G_cash = np.ravel(np.array([[G_sc*(1 + 0.033*(math.cos(360*n/365))) for i in range(24)] for n in range(365)])) # массив 365*24
    G_0 = G_cash*np.cos(np.ravel(theta_z))
    kt = np.array([r_data[i]/G_0 for i in range(years)])
    return kt
    
def diffuse_radiation_on_horiz(r_data, years, k_t):
    diff_rad = np.ones((years, 365*24))   
    
    for i in range(years):
        for j in range(365*24):
            if ((k_t[i][j] >= 0) and (k_t[i][j] <= 0.35)):
                res = 1 - 0.249 * k_t[i][j]
            if ((k_t[i][j] > 0.35) and (k_t[i][j] <= 0.75)):
                res = 1.557 - 1.84 * k_t[i][j]
            if (k_t[i][j] > 0.75):
                res = 0.177         
            diff_rad[i][j] = res*r_data[i][j]
    
    return diff_rad
 
def R_b(angle, lattitude, params): # отношение потока излучения, падающего на наклонную поверхность, к потоку излучения падающего на горизонтальную поверхность
    # beta - угол наклона плоскости солнечной батареи
    beta = angle
    # gamma - азимутальный угол плоскости 
    gamma = 0
    # phi - широта местности (рад.)
    phi = lattitude*math.pi/180
    R_b = []
    
    a1 = np.cos(params['delta']) * math.cos(phi) * math.cos(beta) + np.cos(params['delta']) * math.sin(phi) * math.sin(beta) * math.cos(gamma) # массив 365
    b1 = np.cos(params['delta']) * math.sin(beta) * math.sin(gamma) # массив 365 заполненный нулями
    c1 = np.sin(params['delta']) * math.sin(phi) * math.cos(beta) - np.sin(params['delta']) * math.cos(phi) * math.sin(beta) * math.cos(gamma) # массив 365
    # дополнительные переменные (равные тангенсу часовых углов восхода и заката на наклонной плосксти)
    y1 = (-b1 + np.sqrt(np.absolute(b1**2 - c1**2 + a1**2))) / (c1 - a1) # массив 365
    # проверить, действительно ли можно модуль ставить
    y2 = (-b1 - np.sqrt(np.absolute(b1**2 - c1**2 + a1**2))) / (c1 - a1) # массив 365
    
    omega_t_sunrise = 2 * np.arctan(y1) # массив 365
    omega_t_sunset = 2 * np.arctan(y2) # массив 365
    
    for i in range(365):
        if (omega_t_sunrise[i] > omega_t_sunset[i]):
            omega_t_sunrise[i], omega_t_sunset[i] = omega_t_sunset[i], omega_t_sunrise[i]

    # часовые углы восхода и заката на горизонтальной плоскости
    omega_h_sunset = abs(np.arccos(-(math.sin(phi) * np.sin(params['delta'])) / (math.cos(phi) * np.cos(params['delta']))))
    omega_h_sunrise = -omega_h_sunset

    # ограничение часовых углов восхода и заката на наклонной плоскости
    for i in range(365):
        if (omega_t_sunrise[i] < omega_h_sunrise[i]):
            omega_t_sunrise[i] = omega_h_sunrise[i]

        if (omega_t_sunset[i] > omega_h_sunset[i]):
            omega_t_sunset[i] = omega_h_sunset[i]
    
    # определение часовых углов начала и конца каждого часа     
    omega_h1 = params['omega 1'] # массив 24
    omega_h2 = params['omega 2'] # массив 24
    omega_t1 = params['omega 1'] # массив 24
    omega_t2 = params['omega 1'] # массив 24  
    omega_lag = (2.5 * math.pi) / 180

    for i in range(365):
        for j in range(24):
            # если рассматриваемый час приходится на светлое время суток
            if ((omega_t2[j] > (omega_t_sunrise[j] + omega_lag)) and (omega_t1[j] < (omega_t_sunset[j] - omega_lag))):
                # если на данный час приходится восход
                if (omega_t1[j] < (omega_t_sunrise[j] + omega_lag)):
                    omega_t1[j] = omega_t_sunrise[j] + omega_lag
                    omega_h1[j] = omega_t_sunrise[j] + omega_lag
                # если на данный час приходится закат
                if (omega_t2[j] > omega_t_sunset[j] - omega_lag):
                    omega_t2[j] = omega_t_sunset[j] - omega_lag
                    omega_h2[j] = omega_t_sunset[j] - omega_lag
                    # отношение потока излучения, падающего на наклонную поверхность,
                    # к потоку излучения падающего на горизонтальную поверхность
                    # R_b1 величина для промежуточных вычислений
                    R_b1 = c1[i] * (omega_t2[j] - omega_t1[j]) + a1[i] * (math.sin(omega_t2[j]) - math.sin(omega_t1[j])) + b1[i] * (math.cos(omega_t2[j]) + math.cos(omega_t1[j]))
                    R_b_cash = ( R_b1 / (math.cos(phi) * math.cos(params['delta'][i]) * (math.sin(omega_h2[j]) - math.sin(omega_h1[j])) 
                                       + math.sin(phi) * math.sin(params['delta'][i]) * (omega_h2[j] - omega_h1[j])) )
            else:
                R_b_cash = 0
            R_b.append(R_b_cash)
    R_b = np.array(R_b)
    return np.array(R_b) # массив 365*24
    
def sum_radiation(ratiation_data, angle, station_data):
    #station_data --> [latitude, longitude]
    params = parameters()
    coef = (1 + math.cos(angle))*0.5
    r_data = np.array(ratiation_data)
    years = int( ( r_data.shape[0] )/(365*24) )
    out_year = r_data.shape[0] - years*365*24
    for i in range(out_year):
        r_data = np.delete(r_data, -1, 0)
    r_data = np.reshape(r_data, (years, 365*24))
    kt = k_t(r_data, years, station_data[0], params)
    dif_rad_hor = np.array(diffuse_radiation_on_horiz(r_data, years, kt)) # diff_rad = np.ones((years, 365*24))
    dif_rad_angl = dif_rad_hor*coef
    beam_rad_hor = np.array(r_data - dif_rad_hor)
    beam_rad_angl = np.array([R_b(angle, station_data[0], params)*beam_rad_hor[i] for i in range(years)])
    sum_rad_angle = dif_rad_angl + beam_rad_angl
    return np.ravel(sum_rad_angle)












