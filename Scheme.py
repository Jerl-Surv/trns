def count_params():
    push

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

def file_generator():
    push

def for_angle():
    push
    
def pv_simple(P_pv_max, radiation):
    return P_pv_max*radiation/1000
    
def controler_simple(P_load_max, P_pv, Q_acb):
    if (P_load_max <= P_pv):
        battery_simple.input_energy(Q_acb, P_bat, dt)
    else:
        battery_simple.output_energy(Q_acb, P_bat, dt)
    '''
        if (P_load_max <= P_pv){
        P_load_out = P_load_max;
        P_bat = std::min (P_bat_out_max, P_pv - P_load_max);
    }
    else{
        if(P_bat_in_max > (P_load_max - P_pv)){
            P_bat = P_pv - P_load_max;
        }
        else{
            P_bat = -P_bat_in_max;
        }
        P_load_out = -P_bat + P_pv;
    }

    if (P_load_out < 1E-99){
        P_load_out = 0;
    }
    
    
    //		 Рвыхнагр
			xout[0]=P_load_out;
//		 Pакк
			xout[1]=P_bat;
    '''
    
class battery_simple:
    # разобраться с ооп
    def input_energy(Q_acb, P_bat, dt):
        push
    
    def output_energy(Q_acb, P_bat, dt):
        push
    '''
    //		 Енактек
			xout[0]=t;
//		 Рвхмах
			xout[1]=(E_bat_max - t*E_bat_max)/dt;
//		 Рвыхмах
			xout[2]=t*E_bat_max/dt;

        dtdt = P_bat/E_bat_max;
        
        double &dtdt,  // the array containing the derivatives of T which are evaluated
        double &t,     // the array containing the dependent variables for which the derivatives are evaluated
    '''

def read_data():
    nasa_data = pd.read_csv('data_sum_r_NASA.txt', sep='\t', encoding='latin1')
    nasa_data.columns = ['NASA'] 
    wrdc_data = pd.read_csv('data_sum_r_WRDC.txt', sep='\t', encoding='latin1')
    wrdc_data.columns = ['WRDC']     
    nasa_and_wrdc_data = nasa_data.merge(wrdc_data, 'left', on='NASA')
    return nasa_and_wrdc_data

def P_pv_for_max():
    push
             
def scheme(P_load_max, Q_acb, angle):
    # разобраться с передачей в файл данных
    nasa_and_wrdc_data = read_data()
    radiation = for_angle(nasa_and_wrdc_data, angle)
    P_pv = pv_simple(P_pv_max, radiation)
    P_load = controler_simple(P_load_max, P_pv, Q_acb)
    return P_load




    