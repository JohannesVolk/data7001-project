import pandas as pd
import numpy as np
import statsmodels.api as sm


df = pd.read_csv('data/test_regression.csv')  # Processed csv(extract the delay time)

#  x & y
x = df[['route_type', 'stop_lon', 'zone_id']]
y = df['delay_min']
print(y)

# Check for missing values or infinite values in x
print(x.isnull().sum())
print(np.isinf(x).sum())
x.dropna(inplace=True)
x.fillna(x.mean(), inplace=True)
x.replace([np.inf, -np.inf], np.nan, inplace=True)

# Add a constant column as an intercept
x = sm.add_constant(x)
# Model
model = sm.OLS(y, x)
results = model.fit()

print(results.summary())
