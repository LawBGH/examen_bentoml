
import pandas as pd
from sklearn.model_selection import train_test_split


path = "raw/data/prepared_data.csv"
DATA_PATH = "data/raw/admission.csv"
# Metriques de split
TEST_SIZE = 0.2
RANDOM_STATE = 42 

def load_data(path: str) -> pd.DataFrame:
    """Load data from a CSV file.
        
    Args:
        path (str): The file path to the CSV file. 
    Returns:
        pd.DataFrame: The loaded data as a pandas DataFrame.
    """
    data = pd.read_csv(path)
    # Nettoyage Suppression des lignes avec des valeurs manquantes
    data = data.dropna()
    return data

def split_data(     
data: pd.DataFrame, test_size: float, random_state: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data into training and testing sets.
    
    Args:
        data (pd.DataFrame): The input data.
        test_size (float): The proportion of the dataset to include in the test split.
        random_state (int): The random state for reproducibility.
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: The training and testing data.
    """
    train_data, test_data = train_test_split(data, test_size=test_size, random_state=random_state)


    # Suppresssion des colonnes initutiles commme le serial No et suppression de la colonne cible chance of admit
    X_train = train_data.drop(["Chance of Admit ", "Serial No."], axis=1)
    y_train = train_data["Chance of Admit "]
    X_test = test_data.drop(["Chance of Admit ", "Serial No."], axis=1)
    y_test = test_data["Chance of Admit "]

    x_train_file = "data/processed/x_train.csv"
    y_train_file = "data/processed/y_train.csv"
    x_test_file = "data/processed/x_test.csv"
    y_test_file = "data/processed/y_test.csv"
    X_train.to_csv(x_train_file, index=False)
    y_train.to_csv(y_train_file, index=False)
    X_test.to_csv(x_test_file, index=False) 
    y_test.to_csv(y_test_file, index=False)

    return train_data, test_data



if __name__ == "__main__":
    data = load_data(DATA_PATH)
    split_data(data, TEST_SIZE, RANDOM_STATE)
    print("Data preparation completed.")

    
 

