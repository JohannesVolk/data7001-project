import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

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

# Select relevant features
X = df[['rain_dbz', 'delay']]
y = df['severity']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train an SVM classifier
clf = SVC(kernel='linear')  # You can choose different kernels (e.g., 'rbf', 'poly') as well
clf.fit(X_train, y_train)

# Make predictions
y_pred = clf.predict(X_test)

# Evaluate the model
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Visualization of Results
plt.scatter(X_test['rain_dbz'], y_test, color='blue', label='Actual', alpha=0.5)
plt.scatter(X_test['rain_dbz'], y_pred, color='red', label='Predicted', alpha=0.5)
plt.xlabel('Rain Intensity (rain_dbz)')
plt.ylabel('Delay Severity')
plt.legend()
plt.title('Actual vs. Predicted Delay Severity (SVM)')
plt.show()
