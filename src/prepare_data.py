
import pandas as pd
from sklearn.model_selection import train_test_split


path = "raw/data/prepared_data.csv"
DATA_PATH = "data/raw/admission.csv"
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
    return train_data, test_data
def prepare_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and split the data into training and testing sets.
    
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: The training and testing data.
    """
    data = load_data(DATA_PATH)
    train_data, test_data = split_data(data, TEST_SIZE, RANDOM_STATE)
    return train_data, test_data



if __name__ == "__main__":
    train_data, test_data = prepare_data()
    print("Training Data:")
    print(train_data.head())
    print("\nTesting Data:")
    print(test_data.head()) 

