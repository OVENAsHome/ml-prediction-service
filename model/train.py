import pickle

from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

X, y = load_wine(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Dataset: Wine, samples: {len(X)}, features: {X.shape[1]}, classes: 3")
print(f"Test accuracy: {accuracy:.3f}")

with open("model/model.pkl", "wb") as f:
    pickle.dump(model, f)
print("Model trained and saved to model/model.pkl")
