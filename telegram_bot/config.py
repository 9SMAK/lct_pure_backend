import os

from markup import Markup

next_idea_phrase = 'Следующая идея'
start_markup = Markup([[next_idea_phrase]]).reply

like_symbol = '👍'
dislike_symbol = '👎'
request_membership_symbol = '📝'

swipe_message = 'Нажмите на кнопку внизу для выбора'
swipe_markup = Markup([[like_symbol, request_membership_symbol, dislike_symbol]])

help_msg = f'{like_symbol} - Лайк\n{dislike_symbol} - Дизлайк\n{request_membership_symbol} - Отправить свое портфолио'
replies = {
    'No ideas to show': 'Все идеи закончились',
    'Telegram not found': 'Вы не указали telegram в личном кабинете',
    'start_help': f'Здравствуйте, теперь можете смотреть идеи\n{help_msg}\n'
                  f'Для того чтобы получить эту информацию ещё раз наберите /help',
    'help': help_msg
}


TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
HOST = os.getenv("HOST")

