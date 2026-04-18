import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle
import numpy as np

print("Training model...")

data = pd.read_csv("train.csv")

# basic features
X = data[['GrLivArea','BedroomAbvGr','FullBath','GarageCars']]
y = data['SalePrice']

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X,y)

pickle.dump(model, open("model.pkl","wb"))

# stats for range
stats = {
    "mean": float(np.mean(y)),
    "std": float(np.std(y))
}

pickle.dump(stats, open("stats.pkl","wb"))

print("Model Ready ✅")