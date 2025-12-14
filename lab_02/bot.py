import telebot                                                                        # импортируем библиотеку для работы с telegram API
import logging                                                                        # lля логирования ошибок и действий бота
import json                                                                           # для работы с JSON-форматом
import asyncio                                                                        # для асинхронных операций
from pathlib import Path                                                              # для работы с путями файлов
from telebot import types                                                             # для создания кнопок и клавиатур в Telegram

from config import BOT_KEY                                                            # импортируем все нужные штуки - ключ для бота из конфига
from gpt_api import gpt_generation                                                    # функцию генерации через гпт
from llama_api import llama_generation                                                # аналогичную функцию но через лламу

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(
    level=logging.INFO,                                                               # уровень логирования (по хорошему это в конфиг бы знаю.............)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'                     # формат вывода логов
)
logger = logging.getLogger(__name__)                                                  # создаем логгер

# ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
bot = telebot.TeleBot(BOT_KEY)                                                        # создаем объект бота с использованием токена

# ========== СОСТОЯНИЯ ==========
# состояния бота, которые помогают контролировать этапы взаимодействия с пользователем
class BotState:
    CHOOSING_MODEL = "choosing_model"                                                 # выбор модели (GPT или LLaMA)
    ENTERING_TEMPERATURE = "entering_temperature"                                     # ввод температуры
    ENTERING_TOKENS = "entering_tokens"                                               # ввод количества токенов
    CHOOSING_DIVINATION_TYPE = "choosing_divination"                                  # выбор типа гадания
    CHOOSING_ZODIAC = "choosing_zodiac"                                               # выбор знака зодиака
    ENTERING_DETAILS = "entering_details"                                             # ввод дополнительных деталей
    CONFIRMING = "confirming"                                                         # подтверждение выбора пользователя

# ========== ЗАГРУЗКА ТЕКСТОВ ==========
def load_messages():
    """Загружает тексты из JSON файла"""
    try:
        messages_path = Path(__file__).parent / "static" / "messages.json"            # формируем путь к файлу с текстами
        with open(messages_path, "r", encoding="utf-8") as file:                      # открываем и загружаем данные из файла
            messages = json.load(file)
            return messages
    except Exception as error:
        logger.error(f"Ошибка загрузки messages.json: {error}")                       # логируем ошибку, если файл не найден
        return {}                                                                     # возвращаем пустой словарь в случае ошибки

MESSAGES = load_messages()                                                            # загружаем все тексты

# ========== ПОМОЩНИКИ ==========
def get_message(key, **kwargs):
    """Возвращает текст с подстановкой параметров"""
    text = MESSAGES.get(key, f"[{key} не найден]")                                    # ищем текст по ключу
    if kwargs and isinstance(text, str):
        try:
            return text.format(**kwargs)                                              # форматируем строку с подставленными параметрами
        except:
            pass
    return text                                                                       # возвращаем текст, если ошибок не было

def create_keyboard(items, row_width=2):
    """Создает клавиатуру из списка элементов"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
    for item in items:
        keyboard.add(types.KeyboardButton(item))                                      # добавляем кнопки на клавиатуру
    return keyboard

# создаем различные клавиатуры для выбора модели, знака зодиака и типа гадания
def model_keyboard():
    return create_keyboard(["🧠 GPT-дух", "🦙 LLaMA-привидение"])

def zodiac_keyboard():
    zodiacs = MESSAGES.get("zodiac_signs", [])
    return create_keyboard(zodiacs, row_width=3)

def divination_keyboard():
    types_list = MESSAGES.get("divination_types", [])
    return create_keyboard(types_list)

def confirm_keyboard():
    items = [
        MESSAGES.get("menu_confirm", "✅ Да, всё верно!"),
        MESSAGES.get("menu_add_details", "✨ Добавить детали"),
        MESSAGES.get("menu_back", "↩️ Назад")
    ]
    return create_keyboard(items)

def restart_keyboard():
    items = [
        MESSAGES.get("menu_restart", "🔄 Новое гадание"),
        "🚪 Выйти"
    ]
    return create_keyboard(items)

# ========== ГЕНЕРАЦИЯ ПРЕДСКАЗАНИЙ ==========
def run_async(coroutine):
    """Запускает асинхронную функцию"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

async def generate_prediction(user_data):
    """Генерирует предсказание через выбранную модель"""
    # Формируем запрос для модели на основе выбранных данных пользователя
    user_prompt = f"Сделай {user_data['divination_type'].lower()} для знака {user_data['zodiac']}."    
    
    if user_data.get('details'):
        user_prompt += f" Дополнительные детали: {user_data['details']}"
    
    # В зависимости от выбранной модели, генерируем предсказание с помощью соответствующей функции
    if user_data['model'] == 'gpt':
        result = await gpt_generation(
            user_prompt=user_prompt,
            temperature=user_data['temperature'],
            max_tokens=user_data['tokens'],
            zodiac=user_data['zodiac'],
            divination_type=user_data['divination_type']
        )
    else:
        result = await llama_generation(
            user_prompt=user_prompt,
            temperature=user_data['temperature'],
            max_tokens=user_data['tokens'],
            zodiac=user_data['zodiac'],
            divination_type=user_data['divination_type']
        )
    
    return result

def send_long_message(chat_id, text):
    """Отправляет длинное сообщение частями"""
    if len(text) > 4000:
        # разделяем текст на части по 4000 символов - вообще там лимит 4096, для удобства взяла 4000
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for i, part in enumerate(parts):
            if i == 0:
                # отправляем первую часть без добавления текста "продолжение"
                bot.send_message(chat_id, part, parse_mode=None)
            else:
                 # для всех остальных частей добавляем пометку "продолжение"
                bot.send_message(chat_id, f"*(продолжение)*\n\n{part}", parse_mode="Markdown")
    else:
        # если текст меньше 4000 символов, отправляем его целиком
        bot.send_message(chat_id, text, parse_mode=None)

# ========== ОБРАБОТЧИКИ КОМАНД ==========
@bot.message_handler(commands=['start', 'divine'])
def handle_start(message):
    """Обработчик команд /start и /divine"""
    logger.info(f"Пользователь {message.from_user.id} начал гадание")                                     # логируем начало гадания
    bot.set_state(message.from_user.id, BotState.CHOOSING_MODEL, message.chat.id)                         # устанавливаем состояние выбора модели
    bot.send_message(
        message.chat.id,
        get_message("greeting"),                                                                          # отправляем приветственное сообщение
        parse_mode="Markdown",
        reply_markup=model_keyboard()                                                                     # прикрепляем клавиатуру для выбора модели
    )

@bot.message_handler(commands=['help'])
def handle_help(message):
    """Обработчик команды /help"""
    help_text = (
        "*🧙‍♀️ помощь от нейро-ведьмы аграфены*\n\n"
        "📜 *команды:*\n"
        "• /start — начать гадание\n"
        "• /help — эта справка\n\n"
        "🔮 *как работает:*\n"
        "1. выбери модель (GPT или LLaMA)\n"
        "2. настрой температуру и длину\n"
        "3. выбери тип гадания\n"
        "4. укажи знак зодиака\n"
        "5. получи предсказание!\n\n"
        "*удачи, дорогуша!* ✨"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")                                   # отправляем справку

@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id, message.chat.id) == BotState.CHOOSING_MODEL)    
def handle_model_selection(message):
    """Обработчик выбора модели"""
    # проверяем, что пользователь выбрал одну из допустимых моделей
    if message.text not in ["🧠 GPT-дух", "🦙 LLaMA-привидение"]:
        bot.send_message(message.chat.id, "Выбери модель из кнопок ниже! 👇", reply_markup=model_keyboard())  # отправляем сообщение с запросом выбрать модель
        return
    
    # сопоставляем текст с моделью
    model_map = {"🧠 GPT-дух": "gpt", "🦙 LLaMA-привидение": "llama"}
    
    # сохраняем выбор модели в данные пользователя
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['model'] = model_map[message.text]
    
    # переходим к следующему состоянию (ввод температуры)
    bot.set_state(message.from_user.id, BotState.ENTERING_TEMPERATURE, message.chat.id)
    bot.send_message(
        message.chat.id,
        get_message("ask_temperature"),                                                                    # запрашиваем температуру
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()                                                           # убираем клавиатуру выбора модели
    )

@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id, message.chat.id) == BotState.ENTERING_TEMPERATURE)
def handle_temperature_input(message):
    """Обработчик ввода температуры"""
    try:
        temperature = float(message.text.replace(',', '.'))                                                # преобразуем введенное значение в число с плавающей точкой
        if 0.0 <= temperature <= 1.0:                                                                      # проверяем, что температура в пределах от 0.0 до 1.0
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['temperature'] = temperature                                                          # сохраняем температуру в данные пользователя
            
            bot.set_state(message.from_user.id, BotState.ENTERING_TOKENS, message.chat.id)
            bot.send_message(
                message.chat.id,
                get_message("ask_max_tokens"),                                                             # запрашиваем количество токенов
                parse_mode="Markdown"
            )
        else:
            bot.send_message(message.chat.id, get_message("error_number"))                                 # если введено неверное значение, отправляем ошибку
    except ValueError:
        bot.send_message(message.chat.id, get_message("error_number"))                                     # если не число, отправляем ошибку

@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id, message.chat.id) == BotState.ENTERING_TOKENS)
def handle_tokens_input(message):
    """Обработчик ввода количества токенов"""
    try:
        tokens = int(message.text)                                                                         # преобразуем введенное количество токенов в целое число
        if 1000 <= tokens <= 4000:                                                                          # проверяем, что количество токенов в пределах от 1000 до 4000
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:                   
                data['tokens'] = tokens                                                                    # сохраняем количество токенов в данные пользователя
            
            # переходим к следующему состоянию (выбор типа гадания)
            bot.set_state(message.from_user.id, BotState.CHOOSING_DIVINATION_TYPE, message.chat.id)
            bot.send_message(
                message.chat.id,
                get_message("ask_divination_type"),                                                        # запрашиваем тип гадания
                parse_mode="Markdown",
                reply_markup=divination_keyboard()                                                         # прикрепляем клавиатуру с типами гадания
            )
        else:
            bot.send_message(message.chat.id, get_message("error_number"))                                 # если введено неверное количество токенов, отправляем ошибку
    except ValueError:
        bot.send_message(message.chat.id, get_message("error_number"))                                     # если введено не число, отправляем ошибку

@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id, message.chat.id) == BotState.CHOOSING_DIVINATION_TYPE)
def handle_divination_selection(message):
    """Обработчик выбора типа гадания"""
    divination_types = MESSAGES.get("divination_types", [])                                                # получаем доступные типы гадания из сообщений
    if message.text not in divination_types:                                                               # проверяем, что пользователь выбрал один из допустимых типов гадания
        bot.send_message(message.chat.id, "Выбери тип гадания из кнопок! 👇", reply_markup=divination_keyboard())
        return
    
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['divination_type'] = message.text                                                             # сохраняем выбранный тип гадания
    
    bot.set_state(message.from_user.id, BotState.CHOOSING_ZODIAC, message.chat.id)                         # переходим к следующему состоянию (выбор знака зодиака)
    bot.send_message(
        message.chat.id,
        get_message("ask_zodiac_sign"),                                                                    # запрашиваем знак зодиака
        parse_mode="Markdown",
        reply_markup=zodiac_keyboard()                                                                     # прикрепляем клавиатуру с знаками зодиака
    )

@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id, message.chat.id) == BotState.CHOOSING_ZODIAC)
def handle_zodiac_selection(message):
    """Обработчик выбора знака зодиака"""
    zodiacs = MESSAGES.get("zodiac_signs", [])                                                             # получаем список всех доступных знаков зодиака из сообщений
    # проверяем, выбран ли пользователем один из допустимых знаков зодиака
    if message.text not in zodiacs:
        bot.send_message(message.chat.id, "Выбери знак зодиака из кнопок! 👇", reply_markup=zodiac_keyboard())
        return
    
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:                                 # сохраняем выбранный знак зодиака в данные пользователя
        data['zodiac'] = message.text
    
    bot.set_state(message.from_user.id, BotState.ENTERING_DETAILS, message.chat.id)                        # переходим к следующему состоянию (ввод дополнительных деталей)
    bot.send_message(
        message.chat.id,
        get_message("details_prompt"),                                                                     # запрашиваем дополнительные детали
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()                                                           # убираем клавиатуру выбора знаков зодиака
    )

@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id, message.chat.id) == BotState.ENTERING_DETAILS)
def handle_details_input(message):
    """Обработчик ввода дополнительных деталей"""
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['details'] = message.text                                                                     # сохраняем введенные пользователем детали
        
        # формируем текст подтверждения, отображая выбранную модель, температуру и другие параметры
        model_display = "🧠 GPT-дух" if data['model'] == 'gpt' else "🦙 LLaMA-привидение"
        zodiac_only = data['zodiac'].split('—')[0].strip() if '—' in data['zodiac'] else data['zodiac']
        
        # создаем текст подтверждения с деталями, которые выбрал пользователь
        confirm_text = get_message(
            "confirm_prompt",
            model=model_display,
            temperature=data['temperature'],
            tokens=data['tokens'],
            divination_type=data['divination_type'],
            zodiac=zodiac_only,
            details=data.get('details', 'не указаны')
        )
    
    bot.set_state(message.from_user.id, BotState.CONFIRMING, message.chat.id)                               # переходим к состоянию подтверждения
    bot.send_message(
        message.chat.id,
        confirm_text,                                                                                       # отправляем текст подтверждения
        parse_mode="Markdown",
        reply_markup=confirm_keyboard()                                                                     # добавляем клавиатуру с кнопками подтверждения
    )

@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id, message.chat.id) == BotState.CONFIRMING)
def handle_confirmation(message):
    """Обработчик подтверждения"""
    # если пользователь подтвердил все данные, начинаем генерацию предсказания
    if message.text == get_message("menu_confirm"):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            user_data = data.copy()                                                                         # получаем все данные пользователя
        
        logger.info(f"Начинаем генерацию для пользователя {message.from_user.id}")
        bot.send_message(
            message.chat.id,
            get_message("waiting_generation"),                                                              # сообщаем, что идет генерация 
            parse_mode="Markdown",
            reply_markup=types.ReplyKeyboardRemove()                                                       
        )
                
        try:
            # генерация предсказания с использованием выбранной модели
            result = run_async(generate_prediction(user_data))
            
            # если результат пустой, отправляем сообщение об ошибке
            if not result or result.strip() == "":
                logger.warning("Получен пустой результат от API")
                result = "🌀 Упс... звёзды сегодня капризничают.\n\nПохоже, вселенная решила сохранить свои секреты на сегодня.\nПопробуем ещё раз? 💫"
            
            send_long_message(message.chat.id, result)                                                      # отправляем результат (если он не пустой)
            
            # подсчитываем количество слов в ответе и отправляем сообщение о завершении генерации
            words_count = len(result.split()) if result else 0
            bot.send_message(
                message.chat.id,
                get_message("generation_done", words=words_count),                                          # сообщение о завершении
                parse_mode="Markdown",
                reply_markup=restart_keyboard()                                                             # клавиатура с возможностью начать новое гадание
            )
            
            logger.info(f"Генерация завершена, {words_count} слов")
            
        except Exception as error:
            # обработка ошибки, если генерация не удалась
            logger.error(f"Ошибка генерации: {error}")
            error_message = str(error)[:200]                                                                # ограничиваем длину сообщения об ошибке
            bot.send_message(
                message.chat.id,
                get_message("generation_error", error=error_message),                                       # отправляем сообщение об ошибке
                parse_mode="Markdown",
                reply_markup=create_keyboard([get_message("menu_restart")])                                 # кнопка для перезапуска
            ) 
        
        bot.delete_state(message.from_user.id, message.chat.id)                                             # сбрасываем состояние пользователя
    
    elif message.text == get_message("menu_add_details"):
        # если пользователь хочет добавить дополнительные детали, переходим к состоянию ввода деталей
        bot.set_state(message.from_user.id, BotState.ENTERING_DETAILS, message.chat.id)
        bot.send_message(
            message.chat.id,
            get_message("details_prompt"),                                                                  # запрашиваем дополнительные детали
            parse_mode="Markdown",
            reply_markup=types.ReplyKeyboardRemove()                                                        # убираем клавиатуру
        )
    
    elif message.text == get_message("menu_back"):
        # если пользователь хочет вернуться назад, переходим к выбору типа гадания
        bot.set_state(message.from_user.id, BotState.CHOOSING_DIVINATION_TYPE, message.chat.id)
        bot.send_message(
            message.chat.id,
            get_message("ask_divination_type"),                                                             # запрашиваем выбор типа гадания
            parse_mode="Markdown",
            reply_markup=divination_keyboard()                                                              # прикрепляем клавиатуру для выбора типа гадания
        )

@bot.message_handler(func=lambda message: message.text == get_message("menu_restart"))
def handle_restart(message):
    """Обработчик кнопки 'Новое гадание'"""
    handle_start(message)                                                                                   # перезапуск гадания с самого начала

@bot.message_handler(func=lambda message: message.text == "🚪 Выйти")
def handle_exit(message):
    """Обработчик кнопки 'Выйти'"""
    bot.send_message(
        message.chat.id,
        "👋 *прощай, дорогуша!*\n\nвозвращайся, когда захочешь снова заглянуть в будущее!\nпросто напиши /start ✨",
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()                                                             # убираем клавиатуру
    )
    bot.delete_state(message.from_user.id, message.chat.id)                                                  # убираем состояние
