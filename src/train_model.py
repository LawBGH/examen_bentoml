import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import os
import bentoml

DATA_PATH = "data/processed/"
metrics_path = "models/metrics/"
model_path = "models/model/"


def compute_metrics(model: LinearRegression, X_test: pd.DataFrame, y_test: pd.DataFrame) -> dict:
    from sklearn.metrics import mean_squared_error, r2_score
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return {"Mean Squared Error": mse, "R^2 Score": r2}


def normalize_data(X_train, X_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, scaler


def grid_search_hyperparameters(X_train, y_train):
    from sklearn.model_selection import GridSearchCV
    
    model = LinearRegression()
    param_grid = {
        'fit_intercept': [True, False],
        'positive': [True, False]
    }
    
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)
    
    return grid_search.best_estimator_


if __name__ == "__main__":
    # Charger les données
    X_train = pd.read_csv(os.path.join(DATA_PATH, "x_train.csv"))
    y_train = pd.read_csv(os.path.join(DATA_PATH, "y_train.csv"))
    X_test = pd.read_csv(os.path.join(DATA_PATH, "x_test.csv"))
    y_test = pd.read_csv(os.path.join(DATA_PATH, "y_test.csv"))

    # Normalisation
    X_train_scaled, X_test_scaled, scaler = normalize_data(X_train, X_test)

    # Recherche d’hyperparamètres
    best_model = grid_search_hyperparameters(X_train_scaled, y_train)

    # Calcul des métriques
    metrics = compute_metrics(best_model, X_test_scaled, y_test)

    print("Evaluation Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")

    # Sauvegarde des dossiers
    os.makedirs(model_path, exist_ok=True)
    os.makedirs(metrics_path, exist_ok=True)

    # Sauvegarde du modèle optimisé
    bentoml.sklearn.save_model(
        "linear_regression_model",
        best_model,
        signatures={"predict": {"batchable": True}},
        custom_objects={"scaler": scaler},
    )

    # Sauvegarde du scaler séparé
    bentoml.sklearn.save_model(
        "data_scaler",
        scaler,
        signatures={"transform": {"batchable": True}},
    )

    # Vérification des modèles
    models = bentoml.models.list()
    for m in models:
        print("Model:", m.tag)
        if hasattr(m.info, "creation_time"):
            print("Created at:", m.info.creation_time)
        else:
            print("No creation_time attribute found")
        print("-----")

    # Sauvegarde des métriques
    with open(os.path.join(metrics_path, "metrics.txt"), "w") as f:
        for metric, value in metrics.items():
            f.write(f"{metric}: {value}\n")
