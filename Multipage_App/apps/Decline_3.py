import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pathlib
import datetime
import pyodbc

conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=SVPTG01PMS91\MSSQLSERVER_PMS' + 
';DATABASE=PDMS;UID=pdmsadm;PWD=Card0n2021$06')

df = pd.read_sql_query("SELECT CONVERT(DATE,FECHA) Date, TASA_GAS 'Rate (SCF/d)' FROM CIERRE_DIARIO_POZO WHERE NOMBRE='Perla-7' AND TASA_GAS>0  ORDER BY FECHA",conexion)

# convert date string to Panda datetime format
df['Date'] =  pd.to_datetime(df['Date'], format='%Y-%m-%d') 

df_filter = df[(df['Date'] > '2016-01-01') & (df['Date'] < '2021-10-01')]

raw_q = df['Rate (SCF/d)']

t = df_filter['Date']
q = df_filter['Rate (SCF/d)']

#Define fix variables
total_days = 3000
decline_type = "Hyperbolic"  #Exponential


# display the data
plt.plot(t, q, color='red', label='Production Data')

# subtract one datetime to another datetime
timedelta = [j-i for i, j in zip(t[:-1], t[1:])]
timedelta = np.array(timedelta)
timedelta = timedelta / datetime.timedelta(days=1)

# take cumulative sum over timedeltas
t = np.cumsum(timedelta)
t = np.append(0, t)
t = t.astype(float)

# normalize the time and rate data
t_normalized = t / max(t)
q_normalized = q / max(q)

# function for hyperbolic decline
def hyperbolic(t, qi, di, b):
  return qi / (np.abs((1 + b * di * t))**(1/b))

def exponential(t, qi, di):
    return qi*np.exp(-di*t)

def harmonic(t, qi, di):
    return qi/(1+di*t)

# fitting the data with the hyperbolic function
from scipy.optimize import curve_fit

if (decline_type=="Hyperbolic"):
    popt, pcov = curve_fit(hyperbolic, t_normalized, q_normalized, maxfev=100000)
    qi, di, b = popt
else:
    popt, pcov = curve_fit(exponential, t_normalized, q_normalized, maxfev=100000)
    qi, di = popt
    b = 1


# de-normalize qi and di
qi = qi * max(q)
di = di / max(t)


# function for hyperbolic cumulative production
def cumpro(q_forecast, qi, di, b):
  return (((qi**b) / ((1 - b) * di)) * ((qi ** (1 - b)) - (q_forecast ** (1 - b))))  

# forecast gas rate until 1,500 days
t_forecast = np.arange(total_days)
if (decline_type=="Hyperbolic"):
    q_forecast = hyperbolic(t_forecast, qi, di, b)
else:
    q_forecast = exponential(t_forecast, qi, di, b)

# forecast cumulative production until 1,500 days
Qp_forecast = cumpro(q_forecast, qi, di, b)
Max_Qp_Forecast = max(Qp_forecast)

print('Initial production rate:', np.round(qi, 3), 'MMSCF')
print('Last production rate:', np.round(min(q_forecast), 3), 'MMSCF')
print('Total days: ', total_days)
print('Initial decline rate:', np.round(di, 3), 'SCF/D')
print('Decline coefficient:', np.round(b, 3))
print('Max Qp forecast:', np.round(Max_Qp_Forecast, 3))

# plot the production data with the forecasts (rate and cum. production)

plt.figure(figsize=(15,5))

plt.subplot(1,2,1)
#plt.yscale("log")
#plt.plot(t, raw_q, '.', color='blue', label='Production Data')
#plt.semilogy(t, q, '.', color='red', label='Select Data')
#plt.semilogy(t_forecast, q_forecast, label='Forecast')
plt.plot(t, q, '.', color='red', label='Select Data')
plt.plot(t_forecast, q_forecast, label='Forecast')
plt.title('Resultado Declinacion por Pozo', size=13, pad=15)
plt.xlabel('Dias')
plt.ylabel('Tasa (SCF/d)')
plt.xlim(xmin=0); plt.ylim(ymin=0)
plt.legend()

plt.subplot(1,2,2)
plt.plot(t_forecast, Qp_forecast)
plt.title('Gas Acumulado', size=13, pad=15)
plt.xlabel('Dias')
plt.ylabel('Produccion (SCF)')
plt.xlim(xmin=0); plt.ylim(ymin=0)

plt.show