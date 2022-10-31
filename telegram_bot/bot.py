import os
import copy
import config
import logging
import requests

from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_swipe_markup(idea_id):
    markup = copy.deepcopy(config.swipe_markup)

    markup.edit_callback(0, 0, f'{idea_id}:like')
    markup.edit_callback(0, 1, f'{idea_id}:request')
    markup.edit_callback(0, 2, f'{idea_id}:dislike')

    return markup.inline


async def send_next_idea(bot, username, chat_id):
    idea_request = requests.get(f'{host}/api/telegram/get_unwatched_idea',
                                params={'telegram_username': username})
    data = idea_request.json()

    if idea_request.status_code == 200:
        media = list([InputMediaPhoto(requests.get(f'{host}/api/static/photo',
                                                   params={'file_id': file_id}).content) for file_id in
                      data['photo_ids']])

        if data.get('video_id') is not None:
            media.append(InputMediaVideo(requests.get(f'{host}/api/static/video',
                                                      params={'file_id': data['video_id']}).content,
                                         caption=f'{data["title"]}\n\n{data["description"]}'))

        await bot.send_media_group(chat_id=chat_id,
                                   media=media)
        await bot.send_message(chat_id=chat_id,
                               text=config.swipe_message,
                               reply_markup=get_swipe_markup(data['id']))

        return True

    elif idea_request.status_code == 400:
        await bot.send_message(chat_id=chat_id, text=config.replies[data['detail']])
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(text=config.replies['start_help'], reply_markup=config.start_markup)
    await send_next_idea(context.bot, update.message.from_user.username, update.message.from_user.id)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(text=config.replies['help'])


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    idea_id, swipe_value = int(query.data.split(':')[0]), query.data.split(':')[1]

    if swipe_value == 'like':
        like_request = requests.post(f'{host}/api/telegram/like',
                                     params={'telegram_username': query.from_user.username, 'idea_id': idea_id})
        await query.edit_message_text(text=config.like_symbol, reply_markup=None)
    elif swipe_value == 'request':
        request_request = requests.post(f'{host}/api/telegram/request_membership',
                                        params={'telegram_username': query.from_user.username, 'idea_id': idea_id})
        await query.edit_message_text(text=config.request_membership_symbol, reply_markup=None)
    elif swipe_value == 'dislike':
        dislike_request = requests.post(f'{host}/api/telegram/dislike',
                                        params={'telegram_username': query.from_user.username, 'idea_id': idea_id})
        await query.edit_message_text(text=config.dislike_symbol, reply_markup=None)

    await query.answer()

    await send_next_idea(context.bot, query.from_user.username, query.from_user.id)


async def bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == config.next_idea_phrase:
        await send_next_idea(context.bot, update.message.from_user.username, update.message.from_user.id)


def main() -> None:
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot))

    application.run_polling()


if __name__ == "__main__":
    host = config.HOST
    token = config.TG_BOT_TOKEN
    main()
