import telebot
from time import sleep
from Read_config import read_config
from Main import main
from utils import add_user_article, delete_folder_recursively
import os


config = read_config('config.json')
token = config["tg_bot"]["token"]
SAVE_DIR_DOCUMENTS = config["tg_bot"]["doc_save_dir"]
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=['audio',
                                    'video',
                                    'photo',
                                    'sticker',
                                    'voice',
                                    'location',
                                    'contact'])
def not_text(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Я работаю только с текстовыми сообщениями!')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,"Привет ✌️ ")



# Функция, обрабатывающая текстовые сообщения
@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    user_id = message.chat.id
    question = message.text
    answer = main(question, user_id, config)
        
    bot.send_message(user_id, text = f"""This is the question:    {question}\n\n
                     This is the answer:     {answer}""")
    sleep(2)


# Функция, обрабатывающая файлы сообщения
@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.chat.id
    try:
        # Получаем информацию о документе
        file_info = bot.get_file(message.document.file_id)
        file_name = message.document.file_name

        # Загружаем документ с серверов Telegram
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем документ на диск
        file_path = os.path.join(SAVE_DIR_DOCUMENTS, file_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        db_path = add_user_article(config, user_id, file_name, file_path)
        # config for main 
        config_tg = read_config('config_tg.json')
        for r in range(len(config_tg['retrievers'])):
            config_tg['retrievers'][r]['path'] = db_path
            config_tg['retrievers'][r]['collection_name'] = str(user_id)

        # Сохраняем текст сообщения, если он есть
        print('mess text ', message.caption)
        if message.caption:
            question = message.caption
            answer = main(question, user_id, config_tg)
            print('after main')
            # Отправляем сообщение пользователю о том, что документ и текст сохранены
            bot.send_message(user_id, text = f"""This is the question:    {question}\n\n
                        This is the answer:     {answer}""")
            sleep(2)

    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при сохранении файла или текста.")
        print(f"Ошибка: {e}")


# Запуск бота
bot.polling(none_stop=True)