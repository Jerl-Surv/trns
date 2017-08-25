# Жизнь - боль. Но мы справимся.
import math
import numpy as np

def parameters():
    params = {}
    B = np.array([[n*360/365 for i in range(24)] for n in range(365)])
    # склонение (массив длиной 365)
    delta = 0.006918 - 0.399912*np.cos(B) + 0.070257*np.sin(B) - 0.006758*np.cos(2*B) + 0.000907*np.sin(2*B) - 0.002679*np.cos(3*B) + 0.00148*np.sin(3*B)
    params['delta'] = np.ravel(delta) # массив для года
    # часовой угол
    omega_day = np.array([( 15 * i * math.pi / 180 - math.pi) for i in range(24)]) # массив для дня
    omega_year = np.array([omega_day for i in range(365)]) # массив для года
    params['omega'] = np.ravel(omega_year) # массив для года
    params['omega 1'] = np.ravel(omega_year)
    omega_day_2 = np.array([( ((i + 1) * 15 * math.pi) / 180 - math.pi ) for i in range(24)]) # массив для дня
    omega_year_2 = np.array([omega_day_2 for i in range(365)]) # массив для года
    params['omega 2'] = np.ravel(omega_year_2)
    return params

def k_t(r_data, years, lattitude): # индекс ясности
    G_sc = 1367 # солнечная постоянная
    # phi - широта местности (рад.)
    phi = lattitude*math.pi/180   
    theta_z = math.cos(phi)*math.cos(parameters('delta'))*math.cos(parameters('omega')) + math.sin(phi)*math.sin(parameters('delta'))
    # заатмосферное излучение
    G_0 = G_sc*(1 + 0.033*(math.cos(360*n/365)))*math.cos(theta_z)
    kt = np.array([r_data[i]/G_0 for i in range(years)])
    return kt
    
def diffuse_radiation_on_horiz(r_data, years, k_t):
    diff_rad = np.ones((years, 365))   
    
    for i in range(years):
        for j in range(365):
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
    
    a1 = math.cos(params['delta']) * math.cos(phi) * math.cos(beta) + math.cos(params['delta']) * math.sin(phi) * math.sin(beta) * math.cos(gamma) # массив для года
    b1 = math.cos(params['delta']) * math.sin(beta) * math.sin(gamma) # 0
    c1 = math.sin(params['delta']) * math.sin(phi) * math.cos(beta) - math.sin(params['delta']) * math.cos(phi) * math.sin(beta) * math.cos(gamma) # массив для года
    # дополнительные переменные (равные тангенсу часовых углов восхода и заката на наклонной плосксти)
    y1 = (-b1 + math.sqrt(b1**2 - c1**2 + a1**2)) / (c1 - a1) # массив для года
    y2 = (-b1 - math.sqrt(b1**2 - c1**2 + a1**2)) / (c1 - a1) # массив для года
    
    omega_t_sunrise = 2 * math.atan(y1) # массив для года
    omega_t_sunset = 2 * math.atan(y2) # массив для года
    
    for i in range(365):
        if (omega_t_sunrise > omega_t_sunset):
            omega_t_sunrise[i], omega_t_sunset[i] = omega_t_sunset[i], omega_t_sunrise[i]

    # часовые углы восхода и заката на горизонтальной плоскости
    omega_h_sunset = abs(math.acos(-(math.sin(phi) * math.sin(params['delta'])) / (math.cos(phi) * math.cos(params['delta']))))
    omega_h_sunrise = -omega_h_sunset

    # ограничение часовых углов восхода и заката на наклонной плоскости
    if (omega_t_sunrise < omega_h_sunrise):
        omega_t_sunrise = omega_h_sunrise

    if (omega_t_sunset > omega_h_sunset):
        omega_t_sunset = omega_h_sunset
    
    # определение часовых углов начала и конца каждого часа     
    omega_h1 = params['omega 1'] # массив для года
    omega_h2 = params['omega 2'] # массив для года
    omega_t1 = params['omega 1'] # массив для года
    omega_t2 = params['omega 1'] # массив для года    

    for i in range(24*365):
        omega_lag = (2.5 * math.pi) / 180
        # если рассматриваемый час приходится на светлое время суток
        if ((omega_t2[i] > (omega_t_sunrise[i] + omega_lag)) and (omega_t1[i] < (omega_t_sunset[i] - omega_lag))):
            # если на данный час приходится восход
            if (omega_t1[i] < (omega_t_sunrise[i] + omega_lag)):
                omega_t1[i] = omega_t_sunrise[i] + omega_lag
                omega_h1[i] = omega_t_sunrise[i] + omega_lag
            # если на данный час приходится закат
            if (omega_t2[i] > omega_t_sunset[i] - omega_lag):
                omega_t2[i] = omega_t_sunset[i] - omega_lag
                omega_h2[i] = omega_t_sunset[i] - omega_lag
                # отношение потока излучения, падающего на наклонную поверхность,
                # к потоку излучения падающего на горизонтальную поверхность
                # R_b1 величина для промежуточных вычислений
                R_b1 = c1 * (omega_t2[i] - omega_t1[i]) + a1 * (math.sin(omega_t2[i]) - math.sin(omega_t1[i])) + b1 * (math.cos(omega_t2[i]) + math.cos(omega_t1[i]))
                R_b[i] = R_b1 / (math.cos(phi) * math.cos(params['delta']) * (math.sin(omega_h2) - math.sin(omega_h1)) + math.sin(phi) * math.sin(params['delta']) * (omega_h2 - omega_h1))
            else:
                R_b[i] = 0

    return R_b
    
def sum_radiation(ratiation_data, angle, station_data):
    #station_data --> [latitude, longitude]
    params = parameters()
    r_data = np.array(ratiation_data)
    years = np.len(r_data)/365
    r_data = np.reshape(r_data, (years, 365))
    k_t = k_t(r_data, years, station_data[0])
    dif_rad_hor = np.array(diffuse_radiation_on_horiz(r_data[i]))
    dif_rad_angl = dif_rad_hor*coef
    beam_rad_hor = r_data - dif_rad_hor
    beam_rad_angl = np.array([R_b()*beam_rad_hor[i] for i in range(years)])
    sum_rad_angle = dif_rad_angl + beam_rad_angl
    return np.ravel(sum_rad_angle)











