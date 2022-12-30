import telebot
import bot_token
from random import randint
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import currency_exchange

bot = telebot.TeleBot(bot_token.token)

# данные для курса валют и клавиатура
url = 'https://www.cbr-xml-daily.ru/'
daily_rates_file = 'daily_json.js'
keys = ['GBP', 'USD', 'EUR', 'CNY', 'JPY', 'curr_info', 'Exit']  # валюты для кнопок и кнопка info показа всех валют

def keyboard():
    markup = ReplyKeyboardMarkup(row_width=7, resize_keyboard=True)
    row = [KeyboardButton(x) for x in keys]
    markup.add(*row)
    return markup

# ------- /start -------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Привет, {message.from_user.first_name}!\nВыбери /help для перехода в главное меню.")
    
# ----- /help -------
@bot.message_handler(commands=['help'])
def send_help_info(message):
    menu = \
"Главное меню:\n\
/start - приветствие\n\
/help - главное меню\n\
/remove - удаление слов из текста\n\
/game - игра в конфеты\n\
/currency_exch - курс валют"
    bot.send_message(message.chat.id, menu)


#################################
# ------- Удаление слов ---------
#################################
@bot.message_handler(commands=['remove'])
def remove_words_with_string(message):
    text_all = message.text.split()
    if len(text_all) < 2:
        answer = \
f'Usage: /remove text string\n\
Удаление слов из "text", содержащих "string"\n\
/help'
        bot.send_message(message.chat.id, answer)
    else:
        text_init = text_all[1:-1]
        string = text_all[-1]   #'абв'
        text_new = ' '.join([word for word in text_init if string not in word])
        text_init_msg = f"Исходный текст:\n{' '.join(text_init)}"
        bot.send_message(message.chat.id, text_init_msg)
        text_new_msg = f'Текст после обработки:\n{text_new}'
        bot.send_message(message.chat.id, text_new_msg)
        removed_msg = f'Удалены слова, содержащие "{string}"'
        bot.send_message(message.chat.id, removed_msg)
        bot.send_message(message.chat.id, '/help')


############################
# ---- ИГРА В КОНФЕТЫ ------
############################
def game_init(message):
    """ Инициализация параметров игры """
    global total_qty, turn, limit_up, limit_down, user_id
    total_qty = 117
    turn = get_turn()     # определение 1-го хода: 0 - player 1,  1 - player 2
    limit_up = 28
    limit_down = 1
    user_id = message.from_user.first_name  # имя пользователя

def game_rules():
    """ Правила игры """
    rules = \
f'--- Игра с конфетами ---\n\
Правила игры:\n\
На столе лежит {total_qty} конфет. За один ход можно забрать не более чем {limit_up} конфет. \
Побеждает тот, кто сделает последний ход.'
    return rules

def get_turn() -> int:
    """ Жребий
    0 - Player 1
    1 - Player 2 (бот)
    """
    return randint(0, 1)


def player_name(turn):
    """ имя игрока """
    global user_id
    # player = 'User'
    player = user_id
    if turn == 1:
        player = 'Bot'
    return player

# ------- /game ------------
@bot.message_handler(commands=['game'])
def start_candy_game(message):
    global total_qty, turn, limit_up, limit_down
    game_init(message)          # начальные параметры
    rules_msg = game_rules()    # правила игры
    bot.send_message(message.chat.id, rules_msg)
    if turn == 1:               # ход бота
        player_turn_msg = f'Ходит {player_name(turn)}'
        bot.send_message(message.chat.id, player_turn_msg)
        bot_taken = bot_action(total_qty)
        total_qty -= bot_taken
        if is_game_over(total_qty): # проверка окончания игры
            winner_msg = f'Игра окончена. Победил {player_name(turn)}\n/help'
            bot.send_message(message.chat.id, winner_msg)
        else:
            bot_taken_msg = taken_candy_msg(total_qty, bot_taken, player_name(turn))
            turn = 0    # смена хода
            player_turn_msg = f'\nХодит {player_name(turn)}'
            bot_msg = bot.send_message(message.chat.id, f'{bot_taken_msg}\n{player_turn_msg}')
            bot.register_next_step_handler(bot_msg, next_action)
    else:
        # ход игрока
        player_turn_msg = f'Ходит {player_name(turn)}'
        player_msg = bot.send_message(message.chat.id, player_turn_msg)  # сообщение о ходе игрока
        bot.register_next_step_handler(player_msg, next_action)
        
        
def next_action(message):
    global total_qty, turn, limit_up, limit_down
    player_took = int(message.text)
    if is_in_limit(player_took):
        total_qty -= player_took
        player_taken_msg = taken_candy_msg(total_qty, player_took, player_name(turn))
        bot.send_message(message.chat.id, player_taken_msg)
        if is_game_over(total_qty): # проверка окончания игры
            winner_msg = f'Игра окончена. Победил {player_name(turn)}\n/help'
            bot.send_message(message.chat.id, winner_msg)
        else:
            # ход бота
            turn = 1
            player_turn_msg = f'Ходит {player_name(turn)}'
            bot.send_message(message.chat.id, player_turn_msg)
            bot_taken = bot_action(total_qty)
            total_qty -= bot_taken
            # print(f'{player_name(turn)}: {bot_taken} {total_qty}')
            if is_game_over(total_qty): # проверка окончания игры
                winner_msg = f'Игра окончена. Победил {player_name(turn)}\n/help'
                bot.send_message(message.chat.id, winner_msg)
            else:
                bot_taken_msg = taken_candy_msg(total_qty, bot_taken, player_name(turn))
                turn = 0    # смена хода
                player_turn_msg = f'\nХодит {player_name(turn)}'
                bot_msg = bot.send_message(message.chat.id, f'{bot_taken_msg}\n{player_turn_msg}')
                bot.register_next_step_handler(bot_msg, next_action)
    else:
        # если игрок ввел число не в разрешенных пределах
        over_limit_msg = \
f'Ошибка ввода.\n\
Взять можно от {limit_down} до {limit_up} конфет и не больше оставшихся.\n\
\nПовторите ввод.'
        repeat_msg = bot.send_message(message.chat.id, over_limit_msg)
        bot.register_next_step_handler(repeat_msg, next_action)


def is_in_limit(taken_qty):
    """ проверка лимитов по условию задачи """
    global limit_up, limit_down, total_qty
    if limit_down <= taken_qty <= limit_up and taken_qty <= total_qty:
        return True


def bot_action(total_qty: int) -> int:
    """ действие бота """
    global limit_up, limit_down
    if total_qty <= limit_up:
        bot_took = total_qty
    else:
        bot_took = randint(limit_down, limit_up)
    return bot_took


def taken_candy_msg(total_qty, take_qty, player):
    """ сообщение о взятых конфетах """
    if total_qty <= 0:
        msg = \
f'{player} взял: {take_qty}\n\
Конфет не осталось.'
    else:
        msg = \
f'{player} взял: {take_qty}\n\
Осталось: {total_qty}'
    return msg

    
def is_game_over(total_qty):
    """ проверка окончания игры """
    if total_qty <= 0:
        return True
# ----- Конец игры в конфеты ---------
    
###########################
# ---- курсы валют --------
###########################
@bot.message_handler(commands=['currency_exch'])
def currency_exch(message):
    msg = 'Используй кнопки для наиболее популярных валют или введи буквенный код валюты'
    bot_msg = bot.send_message(message.chat.id, msg, reply_markup=keyboard())
    bot.register_next_step_handler(bot_msg, curr_keys_reply)

    
def curr_keys_reply(message):
    global latest_curr_data, all_curr_list
    latest_curr_data = currency_exchange.get_json_data_from_url(url+daily_rates_file)
    all_curr_list = currency_exchange.get_all_currency_list(latest_curr_data)
    text = message.text # ввод кода валюты
    if text == 'Exit':
        bot.send_message(message.chat.id, '/help', reply_markup=telebot.types.ReplyKeyboardRemove())
    elif text != 'curr_info' and text[0] != '/':
        rate_for_curr = currency_exchange.get_rate_for_currency(text, latest_curr_data)
        msg = bot.send_message(message.chat.id, rate_for_curr, reply_markup=keyboard())
        bot.register_next_step_handler(msg, curr_keys_reply)
    elif text != 'curr_info' and text[0] == '/':
        rate_for_curr = currency_exchange.get_rate_for_currency(text[1:], latest_curr_data)
        msg = bot.send_message(message.chat.id, rate_for_curr, reply_markup=keyboard())
        bot.register_next_step_handler(msg, curr_keys_reply)
    elif text == 'curr_info':
        msg = bot.send_message(message.chat.id, '\n'.join(all_curr_list))
        bot.register_next_step_handler(msg, curr_keys_reply)

# -------- Конец курса валют ------------

print('Bot is running ...')

bot.infinity_polling()
