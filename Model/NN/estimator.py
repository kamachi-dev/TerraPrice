# IMPORTS ###############################################################
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import root_mean_squared_error, r2_score

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor

from sklearn.preprocessing import StandardScaler

from sklearn.model_selection import GridSearchCV

import time
import pickle
import os

# CSV READ ##############################################################

script_dir = os.path.dirname(os.path.abspath(__file__))

def train():
    datasets = {}
    data_path = os.path.join(script_dir, 'data.csv')
    csv = pd.read_csv(data_path)[['latitude', 'longitude', 'commodity', 'pricetype', 'price']][1:]

    onehot = pd.get_dummies(csv, columns=['commodity', 'pricetype'], drop_first=True)
    datasets = {}
    datasets['X_train'] = onehot.drop(columns=['price'])
    datasets['y_train'] = onehot[['price']]

    X_train, X_test, y_train, y_test = train_test_split(datasets['X_train'].values, datasets['y_train'].values, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        'Linear': {
            'model': LinearRegression(),
            'param_grid': {
                'fit_intercept': [True, False]
            },
            'toScale': True
        },
        'Ridge': {
            'model': Ridge(),
            'param_grid': {
                'alpha': [0.1, 1.0, 10.0],
                'fit_intercept': [True, False]
            },
            'toScale': True
        },
        'Lasso': {
            'model': Lasso(),
            'param_grid': {
                'alpha': [0.1, 1.0, 10.0],
                'fit_intercept': [True, False]
            },
            'toScale': True
        },
        'DecisionTree': {
            'model': DecisionTreeRegressor(),
            'param_grid': {
                'criterion': ['squared_error'],
                'max_depth': [None, 5, 10, 20],
                'min_samples_split': [2, 5, 10]
            },
            'toScale': False
        }
    }

    res = {}

    for model_name, model_info in models.items():
        start_time = time.time()
        metrics = {}

        estimator = GridSearchCV(
            model_info['model'],
            param_grid=model_info['param_grid'],
            cv=5,
            n_jobs=-1,
            verbose=0
        ).fit(
            X_train_scaled if model_info['toScale'] else X_train,
            y_train
        ).best_estimator_

        y_pred = estimator.predict(
            X_test_scaled if model_info['toScale'] else X_test
        )
        metrics['rmse'] = root_mean_squared_error(y_test, y_pred)
        metrics['r2'] = r2_score(y_test, y_pred)
        metrics['model'] = estimator
        res[model_name] = metrics
        print(f"Model {model_name} trained in {time.time() - start_time:.2f} seconds.")

    out = pd.DataFrame(res).T
    print(f'\n{out}')

    # Find the model with the best R2 score
    best_model_name = max(res, key=lambda k: res[k]['r2'])
    best_model_info = res[best_model_name]
    print(f'Best model by R2: {best_model_name} (R2={best_model_info["r2"]:.4f})')

    # Save both model and column names
    model_data = {
        'model': best_model_info['model'],
        'columns': datasets['X_train'].columns.tolist(),
        'scaler': scaler if models[best_model_name]['toScale'] else None
    }
    
    with open(os.path.join(script_dir, 'model.pkl'), 'wb') as f:
        pickle.dump(model_data, f)

def predict(latitude, longitude, commodity, pricetype):
    with open(os.path.join(script_dir, 'model.pkl'), 'rb') as f:
        model_data = pickle.load(f)

    model = model_data['model']
    training_columns = model_data['columns']
    scaler = model_data.get('scaler')

    data = pd.DataFrame({
        'latitude': [latitude],
        'longitude': [longitude],
        'commodity': [commodity],
        'pricetype': [pricetype]
    })

    onehot = pd.get_dummies(data, columns=['commodity', 'pricetype'], drop_first=True)
    
    onehot = onehot.reindex(columns=training_columns, fill_value=0)
    
    if scaler is not None:
        onehot_values = scaler.transform(onehot.values)
    else:
        onehot_values = onehot.values

    prediction = model.predict(onehot_values)
    return prediction