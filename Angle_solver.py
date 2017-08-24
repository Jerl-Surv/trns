# Жизнь - боль. Но мы справимся.

import numpy as np

def parameters():
    push
    
def diffuse_radiation_on_horiz():
    push
    '''
    //расчет энергии рассеянной составляющей излучения пришедшей на горизонтальную площадку площадью 1 м^2
        public double G_d_horizon(double G_horizon, double k_t)
        {
            //расчет доли интенсивности рассеяного излучения от суммарной интенсивности излучения
            //переменная для интенсивности рассеяного излучения
            double G_d = 0;
            //переменная для расчета доли интенсивности рассеяного излучения от суммарной интенсивности излучения
            double res = 0;
            //для различных значиений коэффициента ясности доли интенсивности рассеяного излучения
            if ((k_t >= 0) & (k_t <= 0.35))
            {
                res = 1 - 0.249 * k_t;
            }
            if ((k_t > 0.35) & (k_t <= 0.75))
            {
                res = 1.557 - 1.84 * k_t;
            }
            if (k_t > 0.75)
            {
                res = 0.177;
            }
            //интенсивность рассеяного излучения
            G_d = res * G_horizon;
            return G_d;
        }
    '''
 
def R_b():
    push
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
    dif_rad_hor = np.array([diffuse_radiation_on_horiz(r_data[i]) for i in range(years)])
    dif_rad_angl = dif_rad_hor*coef
    beam_rad_hor = r_data - dif_rad_hor
    beam_rad_angl = np.array([R_b()*beam_rad_hor[i] for i in range(years)])
    sum_rad_angle = dif_rad_angl + beam_rad_angl
    return np.ravel(sum_rad_angle)




