from Read_config import read_config
from Text_process import tokenize
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from utils import make_HF_embedding


class Retrievers():
    

    def __init__ (self, config):
        retrievers_list = config['retrievers']
        if len(retrievers_list) == 0:
            raise "No retriever, check the config file"
        elif len(retrievers_list) == 1:
            self.retrivier = self.create_one_retriever(retrievers_list[0])
        else:
            retrievers = [self.create_one_retriever(r) for r in retrievers_list]
            self.retrivier = EnsembleRetriever(
                retrievers=retrievers,
                weights=[1/len(retrievers) for i in retrievers],
            )

    
    def create_one_retriever(self, retriever):
        name = retriever['name']
        path = retriever['path']
        collection_name = retriever['collection_name']
        k = retriever['k']
        db = Chroma(collection_name = collection_name,
                        embedding_function = make_HF_embedding(),
                        persist_directory = path
                    )
        if name == 'HF':
            model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': False}
            embedding = HuggingFaceEmbeddings(model_name=model_name,
                                            model_kwargs=model_kwargs,
                                            encode_kwargs=encode_kwargs)
            retriever_made =  db.as_retriever(search_kwargs={"k": k})
            return retriever_made
        elif name == 'bm25':
            texts = db.get()['documents']
            retriever_made = BM25Retriever.from_texts(
                texts=texts,
                preprocess_func=tokenize,
                k=k,
            )
            return retriever_made
        

    def invoke(self, text):
        return self.retrivier.invoke(text)
    

if __name__ == "__main__":
    config = read_config('config.json')
    ret = Retrievers(config)
    for i in ret.invoke('Какое место заняло ОАЭ в рейтингах в Оксфордском индексе?'):
        print(i.page_content, '\n')
