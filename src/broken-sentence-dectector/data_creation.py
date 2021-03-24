import random
import spacy
import glob
import string
from tqdm import tqdm

ASCII_UPPER = string.ascii_uppercase
ASCII_LOWER = string.ascii_lowercase
ASCII_NUMBER = string.digits
ASCII_PUNCT = string.punctuation
PRINTABLE = string.printable

class NoFilesException(Exception):
    """Exception raised for no files when expecting files"""
    def __init__(self, path, message="No files were located."):
        self.message = message
        self.path = path
        super().__init__(self.message)


class TokenLengthMismatchException(Exception):
    """Exception raised for mismatches in original token lengths."""
    def __init__(self, total_length, discovered_length):
        self.total_length = total_length
        self.discovered_length = discovered_length
        self.message = f"Lists do not match length.  Found {total_length} versus {discovered_length}."
        super().__init__(self.message)


class FewTokensException(Exception):
    """Exception raised for too few tokens."""
    def __init__(self, message="Too few tokens for modifying sentence."):
        self.message = message
        super().__init__(self.message)
    
class MissingWhitespaceException(Exception):
    """Exception raised for sentences that contain no whitespace."""
    def __init__(self, message="No whitespace detected."):
        self.message = message
        super().__init__(self.message)


def load_files(path_to_files, ext=".txt"):
    #TODO Implement Generator
    paths_query = f"{path_to_files}/*{ext}"
    files_to_load = glob.glob(paths_query)

    if len(files_to_load) == 0:
        raise NoFilesException


def get_tokens_from_idx(token_list, indexes):
    """Method to take a list of tokens and a list of indexes and
    extract the tokens with the corresponding index.

    Args:
        token_list (list): list with tokens desired to be extracted.
        indexes (list): desired locations of the tokens.

    Returns:
        [list]: tokens that are at the represented indexes.
        [list]: original list with the tokens removed.
    """
    tokens = []
    for idx in indexes:
        token_of_interest = token_list[idx]
        tokens.append(token_of_interest)
        token_list.remove(token_of_interest)
    return tokens, token_list


def get_random_span(text):
    """Method to take a string and generate a variable span based off
    the total length of the string

    Args:
        text (str): Sequence to text to create a span from

    Returns:
        [list]: The left and right index of the span on a character level
    """
    string_length = len(text)
    random_span_1 = int(random.random()*string_length)
    random_span_2 = int(random.random()*string_length)
    while random_span_1 == random_span_2:
        random_span_2 = int(random.random()*string_length)
    span = [random_span_1, random_span_2]
    span.sort()
    return span


def scramble_some_words(text):
    """Method to randomly select N number of words in a sentence, shuffle them
    and randomly replace those tokens in the original sentence.

    Args:
        text (str): Text of the sentence to shuffle the words around in.
    """
    text = text[:-1] # Remove last character (which should be punctuation)
    tokens = text.split(' ')
    original_tokens = tokens.copy()
    total_len = len(tokens)
    num_tokens_to_move = int(random.random() * total_len / 2) * 2
    idx_tokens_to_move = random.sample(range(total_len), num_tokens_to_move) # Creates the indexes to shuffle
    
    for i in range(0, len(idx_tokens_to_move), 2):
        idx_1 = idx_tokens_to_move[i]
        idx_2 = idx_tokens_to_move[i + 1]
        token_1 = tokens[idx_1]
        token_2 = tokens[idx_2]
        tokens[idx_1] = token_2
        tokens[idx_2] = token_1
    
    if len(tokens) != total_len:
        raise TokenLengthMismatchException
    
    sentence = ' '. join(tokens)
    sentence = sentence + '.'
    return sentence


def move_span(text):
    """
    Method to move a span randomly in a sentence
    Args:
        text (str): Sequence of text

    Returns:
        [str]: Text of the sentence to shuffle the words around in.
    """

    target_span = get_random_span(text)
    span_length = target_span[1] - target_span[0]
    inital_idx = target_span[0]
    char_list = list(text)
    span_list = []
    for i in range(span_length):
        span_list.append(char_list.pop(inital_idx))
    
    new_idx = int(random.random() * len(char_list))
    while new_idx == inital_idx:
        new_idx = int(random.random() * len(char_list))

    for i in range(span_length):
        char_list.insert(new_idx, span_list.pop())
    sentence = ''.join(char_list)

    return sentence


def truncate_sentence(text):
    """Method to strip characters from a sentence from the left.

    Args:
        text (str): String that is a sentence.
    
    Raises:
        FewTokensException: Exception when not enough tokens are present to run the method.

    Returns:
        [str]: Modified string that has been randomly truncated
    """

    tokens = ' '.split(text)
    if len(tokens) <= 2:
        raise FewTokensException("Too few tokens, check your data")

    length_truncated = int(random.random()* len(tokens))
    
    while len(tokens) == length_truncated or length_truncated == 0:
        length_truncated = int(random.random()* len(tokens))
    tokens = tokens[: length_truncated]
    sentence = ' '.join(tokens)
    return sentence


def negative_truncation(text):
    """Method to strip character from a sentence from the right.

    Args:
        text (str): String that is a sentence.

    Raises:
        FewTokensException: Exception when not enough tokens are present to run the method.

    Returns:
        [str]: Modified string that has been randomly truncated
    """
    tokens = ' '.split(text)
    if len(tokens) <= 2:
        raise FewTokensException("Too few tokens, check your data")
    length_truncated = int(random.random()* len(tokens))
    while len(tokens) == length_truncated:
        length_truncated = int(random.random()* len(tokens))
    tokens = tokens[length_truncated:]
    sentence = ' '.join(tokens)
    return sentence


def generate_char_list(char_list, weight=0.75):
    """Method to generate a character list with missing whitespace.

    Args:
        char_list (list): List of characters with whitesmace
    
    Raises:
        MissingWhitespaceException: Exception when not enough whitesapce is present to run the method.
    
    Returns:
        [list]: Modified character list with missing whitespace.
    """
    new_char_list = []
    if ' ' not in char_list:
        raise MissingWhitespaceException("No whitespace present.")
    for i in char_list:
        if i is " " and bool(random.random() > weight):
            continue
        new_char_list.append(i)
    
    if char_list == new_char_list:
        return generate_char_list(char_list)
    
    return(new_char_list)


def remove_whitespace(text, weight=0.75):
    """Method to take an input sentence and randomly remove whitespace.

    Args:
        text ([type]): [description]
        weight (float): Percentage of weight given to the random number for removing whitespace.

    Returns:
        [str]: Modified sentence as a string.
    """
    char_list = list(text)
    new_char_list = generate_char_list(char_list, weight)
    sentence = ''.join(new_char_list)
    return sentence


def point_mutation(token_string):
    """Method to randomly change a character in a string

    Args:
        token_string (str): String to have the letter changed on.

    Returns:
        [str]: The modified string.
    """
    length_string = len(token_string)
    point_change = int(random.random() * length_string)
    letter_to_change = string[point_change]
    if letter_to_change in ASCII_UPPER:
        new_letter = random.choice(ASCII_UPPER)
        while new_letter == letter_to_change:
            new_letter = random.choice(ASCII_UPPER)
        token_string[point_change] = new_letter
    elif letter_to_change in ASCII_LOWER:
        new_letter = random.choice(ASCII_LOWER)
        while new_letter == letter_to_change:
            new_letter = random.choice(ASCII_LOWER)
        token_string[point_change] = new_letter
    elif letter_to_change in ASCII_NUMBER:
        new_letter = random.choice(ASCII_NUMBER)
        while new_letter == letter_to_change:
            new_letter = random.choice(ASCII_NUMBER)
        token_string[point_change] = new_letter
    elif letter_to_change in ASCII_PUNCT:
        new_letter = random.choice(ASCII_PUNCT)
        while new_letter == letter_to_change:
            new_letter = random.choice(ASCII_PUNCT)
        token_string[point_change] = new_letter
    else:
        new_letter = random.choice(PRINTABLE)
        while new_letter == letter_to_change:
            new_letter = random.choice(PRINTABLE)
        token_string[point_change] = new_letter
    
    return token_string


def mispell_some_words(text):
    
    tokens = text.split(' ')
    total_tokens = len(tokens)
    total_mutations = int(random.random()*total_tokens)
    mutation_idx = random.sample(range(total_tokens), total_mutations)
    for i in mutation_idx:
        word = point_mutation(tokens[i])
        tokens[i] = word

    sentence = ' '.join(tokens)
    return sentence
