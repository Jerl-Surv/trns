# Жизнь - боль. Но мы справимся.

import numpy as np
import math

def parameters(parameter_name):
    params = {}
    B = np.array([(n - 1)*360/365 for n in range(365)])
    # склонение (массив длиной 365)
    delta = 0.006918 - 0.399912*cos(B) + 0.070257*sin(B) - 0.006758*cos(2*B) + 0.000907*sin(2*B) - 0.002679*cos(3*B) + 0.00148*sin(3*B)
    params['delta'] = delta
    # часовой угол, массив для года
    omega_day = np.array([15*i*math.pi/180 for i in range(24)])
    omega_year = np.array([omega_day for i in range(365)])
    params['omega'] = np.ravel(omega_year)
    return params

    '''
    data_in_day[k].H_h - суммарный приход энергии солнечного излучения на горизонтальный участок площадью 1 м^2 за каждые сутки (данные из БД)
n - номер дня в течение года (n=1..366 в случае, если год високосный)
latitude  - географическая широта расчетной точки (град.)

phi - широта местности (рад.)
beta - угол наклона плоскости солнечной батареи
gamma - азимутальный угол плоскости

public class parameters_day
        {
            //часовой угол восход
            public double omega_sunrise = 0;
            //часовой угол заката
            public double omega_sunset = 0;
            //доля энергии излучения, пришиедшей в течение часа, от энергии излучения, пришедшей за сутки
            public double[] r_t = new double[24];
            //приход энергии излучения в течение часа за пределами атмосферы Земли.
            public double[] G0 = new double[24];
        }

        public class parameters_tilted_plane
        {
            //часовой угол восхода на наклонной плосокости
            public double omega_t_sunrise = 0;
            //часовой угол заката на наклонной плоскости
            public double omega_t_sunset = 0;
            //Отношение энергии прямой составляющей излучения, пришедшей на наклонную площадку площадью 1 м^2 в течение часа,
            //к энергии прямой составляющей излучения, пришедшего на горизонтальную площадку площадью 1 м^2 в течение часа
            public double[] R_b = new double[24];

        }

        public class data_in_a_day
        {
            public int year = 1983;
            public int month = 1;
            public int day = 1;
            public int number_day = 0;
            public double H_h = 0;
            public double t_max = 0;
            public double t_min = 0;
            public double E_load = 0;
            public bool data_upload = true;
        }

parameters_day[] param_day = new parameters_day[366];
parameters_tilted_plane[] param_tilted_plane = new parameters_tilted_plane[366];
data_in_a_day[] data_in_day = new data_in_a_day[12000];

    '''
    push
    
def k_t(r_data, years, lattitude): # индекс ясности
    G_sc = 1367 # солнечная постоянная
    # phi - широта местности (рад.)
    phi = lattitude*math.pi/180   
    theta_z = cos(phi)*cos(parameters('delta'))*cos(parameters('omega')) + sin(phi)*sin(parameters('delta'))
    # заатмосферное излучение
    G_0 = G_sc*(1 + 0.033*(cos(360*n/365)))*cos(theta_z)
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
    
    a1 = cos(params['delta']) * cos(phi) * cos(beta) + cos(params['delta']) * sin(phi) * sin(beta) * cos(gamma)
    b1 = cos(params['delta']) * sin(beta) * sin(gamma);
    c1 = sin(params['delta']) * sin(phi) * cos(beta) - sin(params['delta']) * cos(phi) * sin(beta) * cos(gamma);
    # дополнительные переменные (равные тангенсу часовых углов восхода и заката на наклонной плосксти)
    y1 = (-b1 + math.sqrt(b1**2 - c1**2 + a1**2)) / (c1 - a1)
    y2 = (-b1 - math.sqrt(b1**2 - c1**2 + a1**2)) / (c1 - a1)
    
    omega_t_sunrise = 2 * math.atan(y1)
    omega_t_sunset = 2 * math.atan(y2)
    
    if (omega_t_sunrise > omega_t_sunset):
        temp = omega_t_sunrise
        # часовые углы восхода
        omega_t_sunrise = omega_t_sunset
        # заката
        omega_t_sunset = temp

    # часовые углы восхода и заката на горизонтальной плоскости
    omega_h_sunset = abs(math.acos(-(sin(phi) * sin(params['delta'])) / (cos(phi) * cos(params['delta']))))
    omega_h_sunrise = -omega_h_sunset;

    # ограничение часовых углов восхода и заката на наклонной плоскости
    if (omega_t_sunrise < omega_h_sunrise):
        omega_t_sunrise = omega_h_sunrise

    if (omega_t_sunset > omega_h_sunset):
        omega_t_sunset = omega_h_sunset
    
    # определение часовых углов начала и конца каждого часа    
    for i in range(24):
        omega_h1 = ((i * 15) * math.pi) / 180 - math.pi
        omega_h2 = (((i + 1) * 15) * math.pi) / 180 - math.pi
        omega_t1 = ((i * 15) * math.pi) / 180 - math.pi
        omega_t2 = (((i + 1) * 15) * math.pi) / 180 - math.pi
        omega_lag = (2.5 * math.pi) / 180
        # если рассматриваемый час приходится на светлое время суток
        if ((omega_t2 > (omega_t_sunrise + omega_lag)) and (omega_t1 < (omega_t_sunset - omega_lag))):
            # если на данный час приходится восход
            if (omega_t1 < (omega_t_sunrise + omega_lag)):
                omega_t1 = omega_t_sunrise + omega_lag
                omega_h1 = omega_t_sunrise + omega_lag
            # если на данный час приходится закат
            if (omega_t2 > omega_t_sunset - omega_lag):
                omega_t2 = omega_t_sunset - omega_lag
                omega_h2 = omega_t_sunset - omega_lag
                # отношение потока излучения, падающего на наклонную поверхность,
                # к потоку излучения падающего на горизонтальную поверхность
                # R_b1 величина для промежуточных вычислений
                R_b1 = c1 * (omega_t2 - omega_t1) + a1 * (sin(omega_t2) - sin(omega_t1)) + b1 * (cos(omega_t2) + cos(omega_t1))
                param_tilted_plane[n - 1].R_b[i] = R_b1 / (cos(phi) * cos(params['delta']) * (sin(omega_h2) - sin(omega_h1)) + sin(phi) * sin(params['delta']) * (omega_h2 - omega_h1))
            else:
                param_tilted_plane[n - 1].R_b[i] = 0


    return R_b
    '''
    //Расчет отношения потока излучения, падающего на наклонную поверхность,
//к потоку излучения падающего на горизонтальную поверхность
        public void write_param_tilted_plane(double gamma, double beta, double phi, int n)
        {
            //склонение - угловое положение Солнца в солнечный полдень относительно плоскости экватора
            double delta = (Math.PI / 180d) * (23.45d * Math.Sin((2d * Math.PI * (284d + n)) / 365d));
            
            //определение часовых углов рассвета и заката на наклонной плоскости
            //коэффициенты для промежуточных вычислений
            double a1 = Math.Cos(delta) * Math.Cos(phi) * Math.Cos(beta) + Math.Cos(delta) * Math.Sin(phi) * Math.Sin(beta) * Math.Cos(gamma);
            double b1 = Math.Cos(delta) * Math.Sin(beta) * Math.Sin(gamma);
            double c1 = Math.Sin(delta) * Math.Sin(phi) * Math.Cos(beta) - Math.Sin(delta) * Math.Cos(phi) * Math.Sin(beta) * Math.Cos(gamma);
            //дополнительные переменные (равные тангенсу часовых углов восхода и заката на наклонной плосксти)
            double y1 = (-b1 + Math.Sqrt(Math.Pow(b1, 2d) - Math.Pow(c1, 2d) + Math.Pow(a1, 2d))) / (c1 - a1);
            double y2 = (-b1 - Math.Sqrt(Math.Pow(b1, 2d) - Math.Pow(c1, 2d) + Math.Pow(a1, 2d))) / (c1 - a1);
            
            double omega_t_sunrise = 2 * Math.Atan(y1);
            double omega_t_sunset = 2 * Math.Atan(y2);

            if (omega_t_sunrise > omega_t_sunset)
            {
                double temp = omega_t_sunrise;
                //часовые углы
                //восхода
                omega_t_sunrise = omega_t_sunset;
                //заката
                omega_t_sunset = temp;
            }
            
            //часовые углы восхода и заката на горизонтальной плоскости
            double omega_h_sunset = Math.Acos(-(Math.Sin(phi) * Math.Sin(delta)) / (Math.Cos(phi) * Math.Cos(delta)));
            if (omega_h_sunset < 0)
            {
                omega_h_sunset = -omega_h_sunset;
            }
            double omega_h_sunrise = -omega_h_sunset;

            //ограничение часовых углов восхода и заката на наклонной плоскости
            if (omega_t_sunrise < omega_h_sunrise)
            {
                omega_t_sunrise = omega_h_sunrise;
            }
            if (omega_t_sunset > omega_h_sunset)
            {
                omega_t_sunset = omega_h_sunset;
            }

            //массив объектов класса
            //нумерация элементов массива с нуля (указывается элемент n-1)
            //нулевой элемент 1 января
            param_tilted_plane[n - 1].omega_t_sunrise = omega_t_sunrise;
            param_tilted_plane[n - 1].omega_t_sunset = omega_t_sunset;

            //определение часовых углов начала и конца каждого часа
            for (int i = 0; i < 24; i++)
            {
                double omega_h1 = ((i * 15d) * Math.PI) / 180d - Math.PI;
                double omega_h2 = (((i + 1) * 15d) * Math.PI) / 180d - Math.PI;
                double omega_t1 = ((i * 15d) * Math.PI) / 180d - Math.PI;
                double omega_t2 = (((i + 1) * 15d) * Math.PI) / 180d - Math.PI;
                double omega_lag = (2.5 * Math.PI) / 180d;
                //если рассматриваемый час приходится на светлое время суток
                if ((omega_t2 > (omega_t_sunrise + omega_lag)) & (omega_t1 < (omega_t_sunset - omega_lag)))
                {
                    //если на данный час приходится восход
                    if (omega_t1 < (omega_t_sunrise + omega_lag))
                    {
                        omega_t1 = omega_t_sunrise + omega_lag;
                        omega_h1 = omega_t_sunrise + omega_lag;
                    }
                    //если на данный час приходится закат
                    if (omega_t2 > omega_t_sunset - omega_lag)
                    {
                        omega_t2 = omega_t_sunset - omega_lag;
                        omega_h2 = omega_t_sunset - omega_lag;
                    }
                    //отношение потока излучения, падающего на наклонную поверхность,
                    //к потоку излучения падающего на горизонтальную поверхность
                    //R_b1 величина для промежуточных вычислений
                    double R_b1 = c1 * (omega_t2 - omega_t1) + a1 * (Math.Sin(omega_t2) - Math.Sin(omega_t1)) + b1 * (-Math.Cos(omega_t2) + Math.Cos(omega_t1));
                    param_tilted_plane[n - 1].R_b[i] = R_b1 / (Math.Cos(phi) * Math.Cos(delta) * (Math.Sin(omega_h2) - Math.Sin(omega_h1)) + Math.Sin(phi) * Math.Sin(delta) * (omega_h2 - omega_h1));
                }
                else
                {
                    param_tilted_plane[n - 1].R_b[i] = 0;
                }
            }
        }
    '''
    
def sum_radiation(ratiation_data, angle, station_data):
    #station_data --> [latitude, longitude]
    params = params()
    r_data = np.array(ratiation_data)
    years = len(r_data)/365
    r_data = np.reshape(r_data, (years, 365))
    k_t = k_t(r_data, years, station_data[0])
    dif_rad_hor = np.array(diffuse_radiation_on_horiz(r_data[i]))
    dif_rad_angl = dif_rad_hor*coef
    beam_rad_hor = r_data - dif_rad_hor
    beam_rad_angl = np.array([R_b()*beam_rad_hor[i] for i in range(years)])
    sum_rad_angle = dif_rad_angl + beam_rad_angl
    return np.ravel(sum_rad_angle)







