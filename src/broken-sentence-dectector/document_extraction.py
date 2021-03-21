import glob
import json
import argparse
import os
import uuid
import multiprocessing
import spacy
import scispacy
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

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


class TooFewCPUsException(Exception):
    """Custom exception if a user tries to use too few CPUs"""
    def __init__(self, message="Invalid CPU Number.  Please try to use more than 0 CPUs."):
        self.message = message
        super().__init__(self.message)


# Parser Object
parser = argparse.ArgumentParser(description="Arguments for processing data")
parser.add_argument("--path", type=str, default='data/document_parses/pmc_json')
parser.add_argument("--ext", type=str, default=".json")
parser.add_argument('--outdir', type=str, default="data/text")
parser.add_argument("--cpus", type=int, default=10)
parser.add_argument("--verbose", type=int, default=1)
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


def extract_body_text(file_name, model=SPACY_MODEL):
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
        document = model(text['text'])
        
        for sent in document.sents:
            text_data.append(sent.text)

    return text_data


def save_data(counter, outdir, text_data):
    """Function to save text data to disk at a given output directory.

    Args:
        counter (int): file number to be written.
        outdir ([type]): directory for the files to be output to.
        text_data ([type]): 
    """
    filename = str(counter) + '.txt'
    file_path = os.path.join(outdir, filename)
    with open(file_path, 'w') as f:
        for line in text_data:
            line = line + '\n'
            f.write(line)


def multiprocess_extract_data(path):
    """Function to implement a way to multiprocess the extraction process.

    Args:
        path (str): path to the file to be processed.
        outdir (str): path to save the data
    """
    global outdir
    nlp = spacy.load("en_core_sci_lg")
    filename = f"{str(uuid.uuid4)}.txt"
    full_path = os.path.join(outdir, filename)
    
    text_data = extract_body_text(path, model=nlp)
    with open(full_path, 'w') as f:
        for txt in text_data:
            if len(txt) == 0:
                continue
            txt = txt +'\n'
            f.write(txt)

    

if __name__ == '__main__':
    
    # Get all of the cli arguments
    args = parser.parse_args()
    
    path = args.path
    outdir = args.outdir
    
    ext = args.ext
    cpus = args.cpus
    verbose = args.verbose

    if cpus < 0:

        raise TooFewCPUsException

    if verbose:
        print("Verbose mode enabled.")
        print("Arguments selected as follows:")
        print(f"path: {path}\noutdir: {outdir}\next: {ext}\ncpus: {cpus}")
    try:
        os.makedirs(outdir, exist_ok=False)
    except:
        print(f'The directory structure {outdir} does already exists.  Skipping directory generation.')
        os.makedirs(outdir, exist_ok=True)

    json_paths, num_files = get_files_from_dir(path, ext)
    
    if cpus == 1:
        if verbose:
            print(f"Total number of files are: {num_files}")
        
        file_counter = 0
        document_counter = 1
        blocks = 1000
        text_array = []
        for doc in tqdm(json_paths):
            
            if document_counter > blocks:
                save_data(counter=document_counter, text_data=text_array, outdir=outdir)
                file_counter += 1
                document_counter = 1
                text_array = []
            
            doc_sents = extract_body_text(file_name=doc)
            text_array += doc_sents
            document_counter += 1

    if cpus > 1:
        process_map(multiprocess_extract_data, json_paths, max_workers=cpus)
