from Kernel import Kernel
from Retrievers import Retrievers


def main(question, id, config):
    # initialization
    retriever = Retrievers(config)
    kernel = Kernel(config)
    # pipeline
    question = kernel.reformulate_question(question, id)
    chunks = retriever.invoke(question)
    return kernel.invoke(question, id, chunks)


