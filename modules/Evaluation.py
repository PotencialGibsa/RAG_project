import pandas as pd
import numpy as np
import string
from langchain.retrievers import BM25Retriever
from Retrievers import Retrievers
from Read_config import read_config
from utils import make_HF_embedding
from langchain_chroma import Chroma
from Text_process import preprocess_string, tokenize


# def tokenize(s):
#     return s.lower().translate(str.maketrans("", "", string.punctuation)).split(" ")


def Rank_precision(table, rank):
    table_new = table.loc[table.Rank <= rank]
    return len(table_new.loc[table_new.Judgment == True]) / len(table_new)


def Rank_recall(table, rank):
    all_R = table.loc[table.Judgment == True]
    if len(all_R) == 0:
        return 0
    table_new = table.loc[table.Rank <= rank]
    return len(table_new.loc[table_new.Judgment == True]) / len(all_R)


# Average precision
def AP(table):
    choose_relevant = table.loc[table.Judgment == True].Precision
    if choose_relevant.count() == 0:
        return 0
    return choose_relevant.sum() / choose_relevant.count()


config = read_config('config_eval.json')
evaluation_name = config['evaluation']['evaluation_name']
test_quest_df_path = config['evaluation']['test_quest_df_path']
test_df = pd.read_csv(test_quest_df_path)
retriever = Retrievers(config)
k = config['retrievers'][0]['k']
vector_store_path = config['retrievers'][0]['path']#config['evaluation']['vector_store_path']
collection_name = config['retrievers'][0]['collection_name']#config['evaluation']['collection_name']


vector_store = Chroma(collection_name,
                       embedding_function = make_HF_embedding(),
                         persist_directory=vector_store_path
                    )

bm25_retriever = BM25Retriever.from_texts(
      texts=vector_store.get()['documents'],
      preprocess_func=tokenize, #preprocess_string,
      k=k,
)

AP_list = []

test_quest_df_name = test_quest_df_path[test_quest_df_path.rfind('/')+1:test_quest_df_path.rfind('.csv')-1] 
vector_store_name = vector_store_path[vector_store_path.rfind('/')+1:]
evaluation_name = evaluation_name + '_' + test_quest_df_name + "_" + vector_store_name + '_' + str(k)
logs = evaluation_name + '\n\n'

for i in range(len(test_df)):
    question_test = test_df.iloc[i].question
    answer_test = test_df.iloc[i].answer
    #result_question = [i.page_content for i in bm25_retriever.get_relevant_documents(question_test, k = k)]
    #result_question = [i.page_content for i in vs_retriever.invoke(question_test)]
    #result_question = [i.page_content for i in vector_store.similarity_search(question_test, k = k)]
    #result_answer = [i.page_content for i in bm25_retriever.get_relevant_documents(answer_test, k = 4)]
    result_question = [i.page_content for i in retriever.invoke(question_test)]
    result_answer = [i.page_content for i in bm25_retriever.get_relevant_documents( test_df.iloc[i].context, k = 4)]
    result_question_set = set(result_question)
    result_answer_set = set(result_answer)
    result_cross_set = result_question_set & result_answer_set
    rank_table = pd.DataFrame(columns = ['chunk', 'Rank', 'Judgment', 'Precision', 'Recall'])
    rank_table['chunk'] = result_question
    rank_table['Rank'] = list(range(len(result_question)))
    rank_table['Judgment'] = rank_table.chunk.apply(lambda x: x in result_cross_set)

    Rank_precision_list = []
    Rank_recall_list = []
    
    for r in rank_table.Rank:
        Rank_precision_list.append(Rank_precision(rank_table, r))
        Rank_recall_list.append(Rank_recall(rank_table, r))
    
    rank_table['Precision'] = Rank_precision_list
    rank_table['Recall'] = Rank_recall_list

    AP_val = AP(rank_table)
    
    AP_list.append(AP_val)
    print(str(i), 'Question: ', question_test, 'with AP = ', AP_val)
    logs += str(i) + '. Question: ' + question_test + '\n   AP = ' + str(AP_val) + '\n'

MAP = np.mean(AP_list)


with open('Eval_logs/' + evaluation_name + '.txt', 'w') as f:
    f.write(logs)
    f.write(f'MAP = {MAP}')