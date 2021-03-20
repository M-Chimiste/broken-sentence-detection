import glob
import argparse
from tqdm import tqdm

# Custom Exceptions
class NoFilesFoundException(Exception):
    """Custom exception for not finding files."""
    def __init__(self, path, message="No Files Found at Location"):
        self.path = path
        self.message = message + f"  : {path}"
        super().__init__(self.message)



# Parser Object
parser = argparse.ArgumentParser(description="Arguments for processing data")
parser.add_argument("-path", type=str, default='data/document_parses/pmc_json')
parser.add_argument("-ext", type=str, default=".txt")

def get_files_from_dir(path, ext):
    """Function to get all files of a certain extension at a specific path.

    Args:
        path (str): folder directory for data location.
        ext (str): file format string (e.g. .txt)

    Raises:
        NoFilesFoundException: Exception if the paths list length is zero.

    Returns:
        [list]: List of files found using the path and file extension.
    """
    full_path = f"{path}/*{ext}"
    paths = glob.glob(full_path)
    if len(paths) == 0:
        raise NoFilesFoundException(path=full_path)
    return paths

if __name__ == '__main__':
    args = parser.parse_args()

