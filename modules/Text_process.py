import string
import re
import nltk
from nltk.tokenize import word_tokenize
from langdetect import detect
from langchain_text_splitters import RecursiveCharacterTextSplitter




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

    return s


def del_rubbish(doc):
    NUM_SLASH_N = 5
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200,
                                              chunk_overlap=0)
    text_splitted = text_splitter.split_text(doc[0].page_content)
    text_choosen = ''
    for t in text_splitted:
        if t.count('\n') <= NUM_SLASH_N:
            text_choosen += t + ' '
    doc[0].page_content = text_choosen
    return doc


    

