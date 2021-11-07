# importing pandas and numpylibraries
import pandas as pd
import numpy as np

#Link reference
#https://stackoverflow.com/questions/60368528/how-could-i-store-lambda-functions-inside-a-dictionary-in-python
#https://www.geeksforgeeks.org/applying-lambda-functions-to-pandas-dataframe/
#https://towardsdatascience.com/apply-and-lambda-usage-in-pandas-b13a1ea037f7

# creating and initializing a nested list
values_list = [[1.5, 2.5, 10.0], [2.0, 4.5, 5.0], [2.5, 5.2, 8.0],
			[4.5, 5.8, 4.8], [4.0, 6.3, 70], [4.1, 6.4, 9.0],
			[5.1, 2.3, 11.1]]

a = {
    'linear': lambda t: t,
    'easeInQuad': lambda t: t ** 2,
    'easeOutQuad': lambda t: t * (2-t),
    'easeOutQuint': lambda t: 1 + (t - 1) * t * t * t * t,
    'WGR': lambda x: (x['Field_1'] * x['Field_2'] * x['Field_3']),
}

def calculo(campo1,campo2,campo3):
    return campo1*campo2*campo3

# creating a pandas dataframe
df = pd.DataFrame(values_list, columns=['Field_1', 'Field_2', 'Field_3'],
				index=['a', 'b', 'c', 'd', 'e', 'f', 'g'])


# Apply function numpy.square() to square
# the values of 2 rows only i.e. with row
# index name 'b' and 'f' only
df = df.apply(lambda x: np.square(x) if x.name in ['b', 'f'] else x, axis=1)

# Applying lambda function to find product of 3 columns
# i.e 'Field_1', 'Field_2' and 'Field_3'
func = lambda x: (x['Field_1'] * x['Field_2'] * x['Field_3'])

func2 = 'WGR'
#df = df.assign(Product=a[func2])

df['Product'] = df.apply(lambda x: calculo(x['Field_1'], x['Field_2'], x['Field_3']),axis=1)


# printing dataframe
print(df)

