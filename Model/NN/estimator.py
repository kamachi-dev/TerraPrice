import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import pickle
import __main__



# HELPER FUNCTIONS ################################################################
def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return (x > 0).astype(float)

# NN FUNCTIONS ################################################################
def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return (x > 0).astype(float)

class NeuralNetwork:
    def __init__(self, layer_sizes, learning_rate=0.01):
        self.layer_sizes = layer_sizes
        self.learning_rate = learning_rate
        self.w = []
        self.b = []
        
        for i in range(len(layer_sizes) - 1):
            # Heuristic init: Xavier
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]) * np.sqrt(1. / layer_sizes[i])
            b = np.zeros((1, layer_sizes[i+1]))
            self.w.append(w)
            self.b.append(b)

    def forwardFeed(self, X):
        outs = [X]
        raw_outs = []
        
        for i in range(len(self.w) - 1):
            raw_out = outs[-1] @ self.w[i] + self.b[i]
            out = relu(raw_out)
            raw_outs.append(raw_out)
            outs.append(out)
        
        raw_out = outs[-1] @ self.w[-1] + self.b[-1]
        raw_outs.append(raw_out)
        outs.append(raw_out)

        return outs, raw_outs

    def backwardPropogation(self, outs, raw_outs, y_train):
        if y_train.ndim == 1:
            y_train = y_train.reshape(-1, 1)
            
        m = y_train.shape[0]
        w_adjustments = []
        b_adjustments = []
        
        error = outs[-1] - y_train
        w_adjustments.append((1/m) * outs[-2].T @ error)
        b_adjustments.append((1/m) * np.sum(error, axis=0, keepdims=True))
        
        for i in range(len(self.layer_sizes) - 2, 0, -1):
            error = (error @ self.w[i].T) * relu_derivative(raw_outs[i-1])
            w_adjustments.insert(0, (1/m) * outs[i-1].T @ error)
            b_adjustments.insert(0, (1/m) * np.sum(error, axis=0, keepdims=True))
        
        for i in range(len(w_adjustments)):
            w_adjustments[i] = np.clip(w_adjustments[i], -0.5, 0.5)
            b_adjustments[i] = np.clip(b_adjustments[i], -0.5, 0.5)
        
        for i in range(len(self.w)):
            self.w[i] -= self.learning_rate * w_adjustments[i]
            self.b[i] -= self.learning_rate * b_adjustments[i]

    def fit(self, X_train, y_train, epochs=1000, validation_split=0.2, patience=50, tol=1):
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=validation_split, random_state=None, shuffle=True
        )
        
        best_val_loss = float('inf')
        patience_counter = 0
        best_weights = None
        best_biases = None
        
        for epoch in range(epochs):
            outs, raw_outs = self.forwardFeed(X_train_split)
            self.backwardPropogation(outs, raw_outs, y_train_split)
            
            if (epoch % (epochs // 10) == 0) or (epoch % 10 == 0):
                if y_train_split.ndim == 1:
                    y_train_reshaped = y_train_split.reshape(-1, 1)
                else:
                    y_train_reshaped = y_train_split
                train_loss = np.mean((outs[-1] - y_train_reshaped) ** 2)
                
                val_outs, _ = self.forwardFeed(X_val)
                if y_val.ndim == 1:
                    y_val_reshaped = y_val.reshape(-1, 1)
                else:
                    y_val_reshaped = y_val
                val_loss = np.mean((val_outs[-1] - y_val_reshaped) ** 2)
                
                print(f"Epoch {epoch:4d} | Train Loss: {train_loss:.6f} | Val Loss: {val_loss:.6f}")
                
                # Early stopping check
                if val_loss < best_val_loss + tol:
                    best_val_loss = val_loss
                    patience_counter = 0
                    best_weights = [w.copy() for w in self.w]
                    best_biases = [b.copy() for b in self.b]
                else:
                    patience_counter += 1
                    
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch} (patience: {patience})")
                    # Restore best weights
                    if best_weights is not None:
                        self.w = best_weights
                        self.b = best_biases
                    break

    def predict(self, X):
        outs, _ = self.forwardFeed(X)
        return outs[-1]

# PREDICTION FUNCTION ###############################################
def predict_from_saved_model(data_input, model_path='estimator.pkl'):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_model_path = os.path.join(script_dir, model_path)
    
    # Load the saved model
    with open(full_model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    nn = model_data['neural_network']
    scaler = model_data['scaler']
    feature_columns = model_data['feature_columns']

    new_commodity = f'commodity_{data_input.get('commodity', None)}'
    new_pricetype = f'pricetype_{data_input.get('pricetype', None)}'

    # Process input data
    if isinstance(data_input, str):  # CSV file path
        df = pd.read_csv(data_input)
    elif isinstance(data_input, dict):  # Dictionary input
        df = pd.DataFrame([{
            'latitude': data_input.get('latitude', None),
            'longitude': data_input.get('longitude', None),
            new_commodity: 1,
            new_pricetype: 1
        }], columns=feature_columns)
        df = df.fillna(0)
    else:  # Already a DataFrame
        df = data_input.copy()

    print(df.head())

    # Clean and preprocess data
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df = df.dropna()
    
    # Scale the data using the saved scaler
    X_scaled = scaler.transform(df.values)

    print(pd.DataFrame(X_scaled, columns=feature_columns).head())  # Debugging line to check scaled data
    
    # Make predictions
    predictions = nn.predict(X_scaled)
    
    return predictions.flatten()


# ALDRINE FUNCTIONS!!! ############################################################
def train():
    # uses data.csv by default, ALDRINE HAS TO ADD DATABASE CONNECTION HERE
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'data.csv')
    
    print("Loading data...")
    csv = pd.read_csv(data_path, low_memory=False)
    csv = csv[['latitude', 'longitude', 'commodity', 'pricetype', 'price']].reset_index(drop=True)
    
    csv['price'] = pd.to_numeric(csv['price'], errors='coerce')
    csv['latitude'] = pd.to_numeric(csv['latitude'], errors='coerce')
    csv['longitude'] = pd.to_numeric(csv['longitude'], errors='coerce')
    csv = csv.dropna()
    
    onehot = pd.get_dummies(csv, columns=['commodity', 'pricetype'], drop_first=True)
    
    X = onehot.drop(columns=['price']).values.astype(float)
    y = onehot['price'].values.astype(float)

    print(f"Dataset shape: X={X.shape}, y={y.shape}")
    print(f"Price range: {y.min():.2f} to {y.max():.2f}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Normalize the data for better training
    scaler = StandardScaler()
    
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    nn = NeuralNetwork(
        layer_sizes=[X.shape[1], 256, 128, 64, 1],
        learning_rate=0.005
    )
    
    print("\nTraining neural network...")
    nn.fit(X_train_scaled, y_train, patience=5)
    
    # Save the trained model and scaler
    model_data = {
        'neural_network': nn,
        'scaler': scaler,
        'feature_columns': list(onehot.drop(columns=['price']).columns)
    }
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, 'estimator.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    print(f"Model saved to: {model_path}")

    y_pred = nn.predict(X_test_scaled)

    print("\nSample predictions:")
    for i in range(min(10, len(y_test))):
        print(f"Actual: {y_test[i]:.2f}, Predicted: {y_pred[i][0]:.2f}")
    
    print("\n" + "="*50)
    print("TESTING SAVED MODEL PREDICTIONS")
    print("="*50)
    
    try:
        # Get original data for proper categorical matching
        original_sample = csv.iloc[0][['latitude', 'longitude', 'commodity', 'pricetype']].to_dict()
        saved_prediction = predict_from_saved_model(original_sample)
        print(f"Prediction from saved model: {saved_prediction[0]:.2f}")
        print("Model loading and prediction successful!")
    except Exception as e:
        print(f"Error testing saved model: {e}")

def pred(longt, lati, commo, pricetype):
    new_data = {
        'latitude': lati,
        'longitude': longt,
        'commodity': commo,
        'pricetype': pricetype
    }
    prediction = predict_from_saved_model(new_data)
    print(prediction)
    print(f"Predicted price: {prediction[0]:.2f}")
    return prediction[0]

__main__.NeuralNetwork = NeuralNetwork