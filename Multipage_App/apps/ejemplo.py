import pandas as pd
df = pd.read_csv("./datasets/read_data.csv")
print(df[df.TASA_GAS > 0])