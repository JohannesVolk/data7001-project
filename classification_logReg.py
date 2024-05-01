import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from util import *
import ast
import os

# Read the data from CSV file into a DataFrame
df = pd.read_csv('output_test/translink/test.csv')  

df['upcoming_stops'] = df['upcoming_stops'].apply(ast.literal_eval)

# Extract the target variable 'arrival_delay' from the 'upcoming_stops' column
df['arrival_delay'] = df['upcoming_stops'].apply(lambda x: x.get('arrival_delay', None))

# Replace missing 'arrival_delay' values with 0
df['arrival_delay'].fillna(0, inplace=True)

# Features: Rainfall intensity (dBZ)
X = df[['rain_dbz']]

# Target variable: 'arrival_delay' extracted from 'upcoming_stops'
y = df['arrival_delay']

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the logistic regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
print("Classification Report:")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
