import pandas as pd
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt
import pyodbc

def read_data(query):

    conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=SVPTG01PMS91\MSSQLSERVER_PMS' + 
';DATABASE=PDMS;UID=pdmsadm;PWD=Card0n2021$06')

    df = pd.read_sql_query(query,conexion)

    return dataframe

def hyperbolic_equation(t, qi, b, di):

    return qi/((1.0+b*di*t)**(1.0/b))

def exponential_equation(t, qi, di):

    return qi*np.exp(-di*t)

def remove_nan_and_zeroes_from_columns(df, variable):

    filtered_df = df[(df[variable].notnull()) & (df[variable]>0)]
    return filtered_df

def generate_time_delta_column(df, time_column, date_first_online_column):

    return (df[time_column]-df[date_first_online_column]).dt.days
    
def get_min_or_max_value_in_column_by_group(dataframe, group_by_column, calc_column, calc_type):

    value=dataframe.groupby(group_by_column)[calc_column].transform(calc_type)
    return value

def get_max_initial_production(df, number_first_months, variable_column, date_column):

    #First, sort the data frame from earliest to most recent prod date
    df=df.sort_values(by=date_column)
    #Pull out the first x months of production, where number_first_months is x
    df_beginning_production=df.head(number_first_months)
    #Return the max value in the selected variable column from the newly created 
    #df_beginning_production df
    return df_beginning_production[variable_column].max()

def plot_actual_vs_predicted_by_equations(df, x_variable, y_variables, plot_title):

    #Plot results
    df.plot(x=x_variable, y=y_variables, title=plot_title)
    plt.show()

def main():
    #Read in the monthly oil and gas data
    cadena="SELECT CONVERT(DATE,FECHA) Date, TASA_GAS 'Rate (SCF/d)' FROM CIERRE_DIARIO_POZO WHERE NOMBRE='Perla-10' AND TASA_GAS>0  ORDER BY FECHA"
    dialy_data=read_data(cadena)
    
    #Perform some data cleaning to get the columns as the right data type
    dialy_data['Date']=pd.to_datetime(bakken_data['Date'])
    
    #Declare the desired product that we want to curve fit for--it can either by 'Gas' or 'Oil'
    desired_product_type='Rate (SCF/d)'
    
    #Remove all rows with null values in the desired time series column
    dialy_data=remove_nan_and_zeroes_from_columns(dialy_data, desired_product_type)
    
    #Get the earliest RecordDate for each API Number
    dialy_data['Online_Date']= get_min_or_max_value_in_column_by_group(bakken_data, group_by_column='Date', 
                  calc_column='Date', calc_type='min')
    
    #Generate column for time online delta
    bakken_data['Days_Online']=generate_time_delta_column(bakken_data, time_column='Date', 
                  date_first_online_column='Online_Date')
    
    #Pull data that came online between January and June 2016
    dialy_data_2016=dialy_data[(dialy_data.Online_Date>='2018-01-01') & (dialy_data.Online_Date<='2021-06-01')]
    
    #Get a list of unique API's to loop through--these were randomly selected as examples
    unique_well_APIs_list=[33023013930000.0, 33105039980000.0, 33105039970000.0, 
                           33013018230000.0, 33013018220000.0]
    #Loop through each API, and perform calculations
    for api_number in unique_well_APIs_list:
        #Subset the dataframe by API Number
        production_time_series=bakken_data_2016[bakken_data_2016.API_WELLNO==api_number]
        #Get the highest value of production in the first three months of production, to use as qi value
        qi=get_max_initial_production(production_time_series, 3, desired_product_type, 'ReportDate')
        #Exponential curve fit the data to get best fit equation
        popt_exp, pcov_exp=curve_fit(exponential_equation, production_time_series['Days_Online'], 
                                     production_time_series[desired_product_type],bounds=(0, [qi,20]))
        print('Exponential Fit Curve-fitted Variables: qi='+str(popt_exp[0])+', di='+str(popt_exp[1]))
        #Hyperbolic curve fit the data to get best fit equation
        popt_hyp, pcov_hyp=curve_fit(hyperbolic_equation, production_time_series['Days_Online'], 
                                     production_time_series[desired_product_type],bounds=(0, [qi,2,20]))
        print('Hyperbolic Fit Curve-fitted Variables: qi='+str(popt_hyp[0])+', b='+str(popt_hyp[1])+', di='+str(popt_hyp[2]))
        #Exponential fit results
        production_time_series.loc[:,'Exponential_Predicted']=exponential_equation(production_time_series['Days_Online'], 
                                  *popt_exp)
        #Hyperbolic fit results
        production_time_series.loc[:,'Hyperbolic_Predicted']=hyperbolic_equation(production_time_series['Days_Online'], 
                                  *popt_hyp)
        #Declare the x- and y- variables that we want to plot against each other
        y_variables=[desired_product_type, "Hyperbolic_Predicted", "Exponential_Predicted"]
        x_variable='Days_Online'
        #Create the plot title
        plot_title=desired_product_type+' Production for Well API '+str(api_number)
        #Plot the data to visualize the equation fit
        plot_actual_vs_predicted_by_equations(production_time_series, x_variable, y_variables, plot_title)
                
if __name__== "__main__":
    main()