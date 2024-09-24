import string


def tokenize(s):
    return s.lower().translate(str.maketrans("", "", string.punctuation)).split(" ")