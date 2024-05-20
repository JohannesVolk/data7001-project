import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_curve
import matplotlib.pyplot as plt
from sklearn.preprocessing import label_binarize

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

X = df[['rain_dbz', 'delay']]
y = df['severity']

y_binary = label_binarize(y, classes=['no impact', 'minor delay', 'moderate delay', 'major delay'])

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y_binary, test_size=0.2, random_state=42)

clf = SVC(kernel='rbf') 
clf.fit(X_train, y_train[:, 3])  

# Make predictions
y_scores = clf.decision_function(X_test)

# Compute precision-recall curve
precision, recall, _ = precision_recall_curve(y_test[:, 3], y_scores)

# Plot precision-recall curve
plt.plot(recall, precision, marker='.')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve (SVM with Linear Kernel)')
plt.show()
