import string
import re
import nltk
from nltk.tokenize import word_tokenize
from langdetect import detect



def tokenize(s):
    return s.lower().translate(str.maketrans("", "", string.punctuation)).split(" ")




def preprocess_string(s):
    """
    Preprocesses a string for adding to a vector database.

    Args:
        s (str): The input string.

    Returns:
        str: The preprocessed string.
    """
    # Remove URLs
    s = re.sub(r'http\S+', '', s)

    # Remove non-ASCII characters, non-Russian/English characters, and digits
    s = re.sub(r'[^\x00-\x7Fа-яА-Яa-zA-Z0-9\s]', '', s)

    # Remove punctuation
    s = re.sub(r'[^\w\s]', '', s)

    # Detect the language of the text
    try:
        language = detect(s)
    except:
        language = 'None'

    return s, language

# # Example usage
# input_string = "Hello, world! https://example.com это 12412 тестовый текст."
# preprocessed_string, language = preprocess_string(input_string)

# print("Preprocessed string:", preprocessed_string)
# print("Language:", language)
