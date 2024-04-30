import pandas as pd
from pathlib import Path

def batch_csvs(path: str, batch_size: int = 500):
    """
    Batch a directory of CSV files
    
    Parameters
    ----------
    path : str
        Path to the directory containing the CSV files
    batch_size : int, optional
        Number of CSV files to process in each batch, by default 500
    
    Returns
    -------
    None
    
    """
    # Convert path to Path object for easier manipulation
    path = Path(path)
    
    # List all CSV files in the specified directory
    csv_files = sorted(path.glob('*.csv'), key=lambda x: int(x.stem))
    
    # Process files in batches
    for i in range(0, len(csv_files), batch_size):
        batch_files = csv_files[i:i + batch_size]
        
        # Read and concatenate the batch of files
        df = pd.concat([pd.read_csv(f) for f in batch_files])
        
        # Get the UNIX timestamp of the first file in the batch for naming
        first_file_timestamp = batch_files[0].stem
        
        # Save the concatenated DataFrame to a new CSV file
        output_filename = f"{first_file_timestamp}_batched.csv"
        output_path = path / output_filename
        df.to_csv(output_path, index=False)
        
        print(f"Batch starting with {first_file_timestamp} saved to {output_filename}")

# Example usage:
# batch_csvs('/path/to/your/csv/directory', batch_size=5)
