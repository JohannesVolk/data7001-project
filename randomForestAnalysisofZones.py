import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

df = pd.read_csv('training_data.csv')  

# Convert non-integer values to NaN
df['zone_id'] = pd.to_numeric(df['zone_id'], errors='coerce') 
# Drop rows with NaN in zone_id column 
df.dropna(subset=['zone_id'], inplace=True)  

# Convert zone_id back to integer type
df['zone_id'] = df['zone_id'].astype(int)

# Feature selection
X = df[['zone_id']]
y = df['delay']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Regression model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# Visualize delay patterns across zones
plt.figure(figsize=(10, 6))
sns.boxplot(x='zone_id', y='delay', data=df)
plt.xlabel('Zone ID')
plt.ylabel('Delay')
plt.title('Delay Patterns Across Zones')
plt.xticks(rotation=45)
plt.show()

# Rank zones based on delay predictions
zone_delay_ranking = pd.DataFrame({'Zone_ID': X_test['zone_id'], 'Predicted_Delay': y_pred})
zone_delay_ranking = zone_delay_ranking.groupby('Zone_ID')['Predicted_Delay'].mean().reset_index()
zone_delay_ranking = zone_delay_ranking.sort_values(by='Predicted_Delay', ascending=False)

# Visualize ranked zones
plt.figure(figsize=(10, 6))
sns.barplot(x='Zone_ID', y='Predicted_Delay', data=zone_delay_ranking)
plt.xlabel('Zone ID')
plt.ylabel('Average Predicted Delay')
plt.title('Ranked Zones by Average Predicted Delay')
plt.xticks(rotation=45)
plt.show()
