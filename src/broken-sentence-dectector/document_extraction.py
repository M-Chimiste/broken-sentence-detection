import glob
import json
import argparse
import multiprocessing
import spacy
import scispacy
from tqdm import tqdm

CPU_COUNT = multiprocessing.cpu_count()
SPACY_MODEL = spacy.load("en_core_sci_lg")

# Custom Exceptions
class NoFilesFoundException(Exception):
    """Custom exception for not finding files."""
    def __init__(self, path, message="No Files Found at Location"):
        self.path = path
        self.message = message + f"  : {path}"
        super().__init__(self.message)


class NotEnoughCPUsException(Exception):
    """Custom exception if a user tries to use too many CPUs"""
    def __init__(self, cpu_count, max_cpu_count=CPU_COUNT, message="Invalid Number of CPUs."):
        self.cpu_count = cpu_count
        self.max_cpu_count = max_cpu_count
        self.message = f"{message} Number of CPUs attempted: {cpu_count}.  Number of CPUs available {max_cpu_count}."
        super().__init__(self.message)


# Parser Object
parser = argparse.ArgumentParser(description="Arguments for processing data")
parser.add_argument("-path", type=str, default='data/document_parses/pmc_json')
parser.add_argument("-ext", type=str, default=".json")
parser.add_argument("-cpus", type=int, default=1)
# ----------------------------------------


def get_files_from_dir(path, ext):
    """Function to get all files of a certain extension at a specific path.

    Args:
        path (str): folder directory for data location.
        ext (str): file format string (e.g. .txt)

    Raises:
        NoFilesFoundException: Exception if the paths list length is zero.

    Returns:
        [list]: List of files found using the path and file extension.
        [int]: Total number of files found at the location.
    """
    full_path = f"{path}/*{ext}"
    paths = glob.glob(full_path)
    num_files = len(paths)
    if num_files == 0:
        raise NoFilesFoundException(path=full_path)
    return paths, num_files


def extract_body_text(file_name):
    """Function to open the data json file and extract just the text data.

    Args:
        file_name (str): Full file path to the json file.

    Returns:
        [list]: List of the text data from the 
    """
    text_data = []
    
    with open(file_name, 'r') as f:
        json_obj = json.load(f)
    body_text = json_obj['body_text']
    for text in body_text:
        text_data.append(text['text'])
    return text_data


if __name__ == '__main__':
    args = parser.parse_args()

