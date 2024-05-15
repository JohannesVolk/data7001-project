import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv('training_data.csv')

def categorize_delay(delay):
    if delay <= 0:
        return "no impact"
    elif 0 < delay <= 300:
        return "minor delay"
    elif 300 < delay <= 900:
        return "moderate delay"
    else:
        return "major delay"
df['severity'] = df['delay'].apply(categorize_delay)

# Feature selection
features = ['rain_dbz', 'delay']
X = df[features]
y = df['severity'] 

# Filling missing rain_dbz values with mean
X.fillna(X.mean(), inplace=True)
  
plt.scatter(X['rain_dbz'], y)
plt.xlabel('Rain Intensity (rain_dbz)')
plt.ylabel('Delay Severity')
plt.title('Impact of Rain Intensity on Delay Severity')
plt.show()

# Split the Data into Training and Testing Sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate the Model
y_pred = clf.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Visualization of Results
plt.scatter(X_test['rain_dbz'], y_test, color='blue', label='Actual', alpha=0.5)
plt.scatter(X_test['rain_dbz'], y_pred, color='red', label='Predicted', alpha=0.5)
plt.xlabel('Rain Intensity (rain_dbz)')
plt.ylabel('Delay Severity')
plt.legend()
plt.title('Actual vs. Predicted Delay Severity')
plt.show()