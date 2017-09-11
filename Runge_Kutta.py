# Неявный метод Рунге-Кутты
import numpy as np

def k_find(dt, f_k):
    k_1 = dt*f_k
    k_2 = dt*f_k + k_1*0.5
    k_3 = dt*f_k + k_2*0.5
    k_4 = dt*f_k + k_3*0.5
    
    return [k_1, k_2, k_3, k_4]

def ode_by_RK_bounded(f_array, y_0, min_max_arr, dt):
    y_arr = [y_0]  
    for i in range(1, len(f_array)):
        f_k = f_array[i-1]
        k = k_find(dt, f_k)
        y = y_arr[i-1] + (k[0] + 2*k[1] + 2*k[2] + k[3])/6
        y = max(min_max_arr[0], min(min_max_arr[1], y))
        y_arr.append(y)
    return y_arr
        
    # min_max_arr = [min_f, max_f]

    
f_array = [1/i for i in range(1, 10)]
y_0 = 1
dt = 1

y_arr = ode_by_RK_bounded(f_array, y_0, [-1000, 1000], dt)

print(f_array)
print(y_arr)


    

    
    
    
