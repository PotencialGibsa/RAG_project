from langchain.embeddings import HuggingFaceEmbeddings


def make_HF_embedding():
    model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    return HuggingFaceEmbeddings(model_name=model_name,
                                    model_kwargs=model_kwargs,
                                    encode_kwargs=encode_kwargs)



from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
import os
import glob


def add_user_article(config, id, file_name, file_path):
    print('!!!!')
    doc_save_dir = config['tg_bot']['doc_save_dir']
    dbs_save_dir = config['tg_bot']['db_save_dir']
    chunk_size = config['tg_bot']['chunk_size']
    chunk_overlap = config['tg_bot']['chunk_overlap']
    print('!!!!')

    db_list = glob.glob(dbs_save_dir + f'/{id}')
    if not os.path.exists(dbs_save_dir):
        os.makedirs(dbs_save_dir)

    if len(db_list) == 0:
        db_save_dir = dbs_save_dir + f'/{id}'
        chroma_db = Chroma(str(id),embedding_function = make_HF_embedding(), persist_directory=db_save_dir)
    else:
        db_save_dir = db_list[0]
        chroma_db = Chroma(str(id),embedding_function = make_HF_embedding(), persist_directory=db_save_dir)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                              chunk_overlap=chunk_overlap)

    file_chunks = []
    
    if '.pdf' in file_name:
        loader = PyPDFLoader(file_path) # PyPdfMiner add
        for chunk_pdf in loader.load_and_split(text_splitter):
            file_chunks.append(chunk_pdf)
    elif '.docx' in file_name:
        loader = UnstructuredWordDocumentLoader(file_path)
        for chunk_docx in loader.load_and_split(text_splitter):
            file_chunks.append(chunk_docx)
    elif '.doc' in file_name:
        loader = UnstructuredWordDocumentLoader(file_path)
        for chunk_docx in loader.load_and_split(text_splitter):
            file_chunks.append(chunk_docx)
    else:
        raise 'Error not pdf or docx or doc dociment'
    if len(file_chunks) == 0:
        raise 'Document cant be loaded'
    chroma_db.add_documents(file_chunks)
    
    return db_save_dir


def delete_folder_recursively(folder_path):
    # Проверяем, существует ли папка
    if os.path.exists(folder_path):
        # Проходим по всем файлам и подпапкам в указанной директории
        for root, dirs, files in os.walk(folder_path, topdown=False):
            # Удаляем все файлы
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Файл '{file_path}' удален.")
            # Удаляем все директории
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                os.rmdir(dir_path)
                print(f"Папка '{dir_path}' удалена.")
        # Удаляем саму корневую пап