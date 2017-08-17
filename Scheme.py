def for_angle():
    # разобраться, как пересчитывать угол
    push
    
def pv_simple():
    # P_out = P_pv_max*radiation/1000
    push
    
def controler_simple():
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
    push
    
class battery_simple:
    # разобраться с ооп
    def input_energy():
        push
    
    def output_energy():
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
    '''
        
def scheme():
    # разобраться с передачей в файл данных
    push
    