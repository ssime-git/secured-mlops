import pandas as pd
import numpy as np
from sklearn.datasets import load_iris

# Load iris dataset and save as CSV for demonstration
iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['target'] = iris.target
df['target_name'] = [iris.target_names[i] for i in iris.target]

# Save to data directory
df.to_csv('../data/iris_dataset.csv', index=False)
print("Sample dataset created at code-server/data/iris_dataset.csv")
