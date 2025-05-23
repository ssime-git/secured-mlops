import os
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris

# Load iris dataset and save as CSV for demonstration
iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['target'] = iris.target
df['target_name'] = [iris.target_names[i] for i in iris.target]

# Save to data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
data_path = os.path.join(DATA_DIR, 'iris_dataset.csv')
df.to_csv(data_path, index=False)
print(f"Sample dataset created at {data_path}")
