from langchain.chat_models.gigachat import GigaChat
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from Read_config import read_config
from collections import deque


class Kernel:

    history = {}
    history_len = 2

    def __init__(self, config):
        self.model_name = config["kernel"]["model_name"]
        if self.model_name == "GigaChat":
            self.credentials = config["kernel"]["GigaChat"]["credentials"]
            self.llm = GigaChat(
                credentials=self.credentials,
                model="GigaChat:latest",
                verify_ssl_certs=False,
                profanity_check=False,
            )
            self.prompt = """
                Контекст: @context@ \n
                Ты диалоговый ассистент.
                Твоя главная задача развернуто ответить на сообщение пользователя. 
                Ты можешь использовать для ответа только информацию из контекста.
                Если в контексте нет информации для ответа, проси уточнить вопрос.
                \n
                Сообщение пользователя:\n
                    @input@ \n
                Ответ AI ассистента:\n
                """
            self.prompt_history = """
                Ты диалоговый Ai ассистент.
                Учитывая историю чата и вопрос пользователя
                , который может ссылаться на контекст в истории чата, сформулируй отдельный вопрос,
                который можно понять без истории чата. НЕ отвечай на вопрос,
                просто переформулируй его, если необходимо, в противном случае верни вопрос неизмененным как есть.\n
                История чата :@history@ \n 
                Вопрос пользователя:@input@\n
                Ответ AI ассистента:\n
                """
        else:
            raise "Unpropper model name"

    def update_history(self, answer, session_id, question=""):
        while len(self.history[session_id]) > self.history_len:
            self.history[session_id].popleft()
        note = f"""\n
                Пользователь : {question}\n
                AI ассистент : {answer}\n
        """
        self.history[session_id].append(note)

    def make_context(self, chunks):
        context = ""
        i = 1
        for chunk in chunks:
            try:
                context_add = f"Контекст №{i}:\nМетадата: {chunk.meta_data}\nТекст: {chunk.page_content}\n"
            except:
                try:
                    context_add = f"Контекст №{i}:\nТекст: {chunk}\n"
                except:
                    raise "Error with chunk"
            context += context_add
            i += 1
        return context

    def make_history(self, session_id):
        history = ""
        for h in self.history[session_id]:
            history += h
        return history

    def invoke(self, question, session_id, chunks=[]):
        if not self.history.get(session_id, False):
            self.history[session_id] = deque()
            # answer = 'Hello! What can I help you with?'
            # self.update_history(answer, session_id, question=question)
            # return answer
        if len(chunks) != 0:
            print("len chunks:", len(chunks))
            context = self.make_context(chunks)
        else:
            context = "Нет контекста"

        query = self.prompt.replace("@context@", context).replace("@input@", question)
        # print(query)
        answer = self.llm.invoke(query).content
        self.update_history(answer, session_id, question=question)
        return answer

    def reformulate_question(self, question, session_id):
        if not self.history.get(session_id, False):
            self.history[session_id] = deque()
        history = self.make_history(session_id)
        query_history = self.prompt_history.replace("@history@", history).replace(
            "@input@", question
        )
        question = self.llm.invoke(query_history).content
        print("Question reformulated = ", question)
        return question


if __name__ == "__main__":
    config = read_config("config.json")
    kernel = Kernel(config)
    for i in range(10):
        print(kernel.invoke(input(), 1))
