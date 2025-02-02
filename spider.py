import pandas as pd

df_parquet = pd.read_parquet("validation-00000-of-00001.parquet", engine="pyarrow")
print(df_parquet.head())