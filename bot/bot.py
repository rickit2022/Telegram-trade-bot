import logging, os, random
from bot.data import *
from utils import search_song, search_youtube, download_youtube, getGIF
from credsManager import get_key
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler

STATE_FIND_SONG = 1

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)                             

def escape_chars(text):
    """Helper function to escape special characters for MarkdownV2"""
    special_characters = r"_*`[]()-~>#+=|{}.!"
    escaped_text = """"""
    for char in text:
        if char in special_characters:
            escaped_text += "\\" + char
        else:
            escaped_text += char
    return escaped_text

async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message as a command trigger."""
    if update.message.text == '/start':
        buttons = [[KeyboardButton('Find a song')],[KeyboardButton('Random song')], [KeyboardButton('Help')]]
        await context.bot.send_message(
            chat_id = update.effective_chat.id, 
            parse_mode = 'MarkdownV2',
            reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard = True),
            text=
"""
_こんにちは_, I'm Akira\-chan\! \~\(≧▽≦\)\~

If you don't know where to start, *use one of the buttons below* to get started\!
"""
        )
    elif update.message.text == '/commands':
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            parse_mode = 'MarkdownV2',
            text= 
f"""
*Available commands\:*

/start \- Initiate the bot 

/random 
\- Get a random song

/commands 
\- List all available commands

/help 
\- Guide on how to use the bot

*Special commands*\:
\(_See documentation for setting params_\)

/get *ticker _{escape_chars("[params]")}_* 
\- Get historical data of a stock by ticker symbol 

/visualise *ticker _{escape_chars("[params]")}_*
\- Create a rough chart of a stock trend  

"""
        )
    elif update.message.text == '/help':
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            parse_mode = 'MarkdownV2',
            text=
"""
_*\~ Akira at your service\! \~ はじめまして\!*_
Please read more about me on [GitHub](


"""
        )

    elif update.message.text.strip().startswith('/get'):
        msg = message_parser(update.message.text)
        df = get_symbol_history(msg[0], **msg[1])
        df.to_csv(f'bot/resources/requests/{msg[0]}.csv', index=False)

        with open(f'bot/resources/requests/{msg[0]}.csv', 'rb') as f:
            await context.bot.send_document(
                chat_id = update.effective_chat.id,
                document = f
            )

    elif update.message.text.strip().startswith('/visualise'):
        msg = message_parser(update.message.text)
        df = get_data_df(f"{msg[0]}", "resources/requests")
        
        visualise(df, msg[0], **msg[1])

        await context.bot.send_photo(
            chat_id = update.effective_chat.id,
            parse_mode='MarkdownV2',
            photo = open(f'bot/resources/charts/{msg[0]}.png', 'rb'),
            caption=
f"""
*_{escape_chars(msg[0])}'s chart_*
"""
            )

async def sendTo_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.sendMessage(
        chat_id=update.effective_chat.id,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👍", callback_data="like"),InlineKeyboardButton("👎", callback_data="dislike")]]),
        parse_mode = 'MarkdownV2',
        text=
f""" 
_Prefer to listen and watch it on YouTube?_
"""
                )

async def song_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get user input for song name"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=
"""
What song are you looking for? ಠ_ಠ
"""
    )
    return STATE_FIND_SONG

async def find_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gif_load = await context.bot.send_animation(
            chat_id=update.effective_chat.id,
            animation= getGIF("anime smile")
        )

    load = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode = 'MarkdownV2',
        text =
"""
_Finding a match for you\.\.\._
"""
        )
    user_key = update.message.text
    local_query = search_song(user_key)
    youtube_query = search_youtube(user_key)
    if youtube_query != None:
        context.bot_data["youtube response"] = youtube_query[0]

    #if there's already a match in the database
    if local_query: 
        with open(f'bot\songs\{local_query}', 'rb') as voice_file:
            await context.bot.sendVoice(
                chat_id=update.effective_chat.id,
                voice = voice_file,
                parse_mode = 'MarkdownV2',
                caption=
f"""
Found it\!

*_{escape_chars(local_query[:-4])}_*
"""
            )

        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id= load.message_id
        )

        await sendTo_youtube(update, context)

    #no match in local, search youtube
    elif youtube_query:
        if not download_youtube(youtube_query[0]):
            gif_load = await context.bot.send_animation(
                chat_id=update.effective_chat.id,
                animation= getGIF("anime sad")
            )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                parse_mode = 'MarkdownV2',
                text =
"""
_Couldn\'t save it to our database\.\.\.\!_
"""
            )
            return
        print(youtube_query[1])
        with open(f'bot/resources/songs/{youtube_query[1]}.opus', 'rb') as voice_file:
            await context.bot.sendVoice(
                chat_id=update.effective_chat.id,
                voice = voice_file,
                parse_mode = 'MarkdownV2',
                caption=
f"""
Found it\!

*_{escape_chars(youtube_query[1])}_*
"""
            )

        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id= load.message_id
        )

        await sendTo_youtube(update, context)

    else:
        await context.bot.delete_message(
            chat_id= update.effective_chat.id,
            message_id= gif_load.message_id
        )
        await context.bot.send_animation(
            chat_id=update.effective_chat.id,
            animation= getGIF("anime sad")
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode = 'MarkdownV2',
            text =
f"""
_No result {escape_chars("(￣ω￣)")}\!_
"""
        )
        await context.bot.delete_message(
            chat_id= update.effective_chat.id,
            message_id= load.message_id
        )

    return ConversationHandler.END

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handling the callback from the youtube prompt button."""
    query = update.callback_query

    if query.data == "like":
        await context.bot.editMessageReplyMarkup(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup= None,
        )

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            parse_mode='MarkdownV2',
            text=
f"""
Here you go\!

{escape_chars(context.bot_data["youtube response"])}
"""
        ) 
    await context.bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id
    )

    await update.callback_query.answer()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=
"""
*Cancelled\!*
"""
    )
    return ConversationHandler.END

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handling the message sent by the user."""
    if "Random song" in update.message.text:
        random_voice = random.choice([file for file in os.listdir(os.getcwd() + r"\bot\resources\songs") if file.endswith(".opus")])

        await context.bot.send_animation(
                chat_id=update.effective_chat.id,
                animation= getGIF("anime smile")
            )
        
        load = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode = 'MarkdownV2',
            text =
"""
_Loading a random song\.\.\._
"""
        )
        
        with open(f'bot/resources/songs/{random_voice}', 'rb') as voice_file:
            await context.bot.sendVoice(
                chat_id=update.effective_chat.id,
                voice = voice_file,
                parse_mode = 'MarkdownV2',
                caption = 
f"""Here\'s a random song for you\!

*_{escape_chars(random_voice[:-4])}_*
"""
            )

        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id= load.message_id
        )
    elif "Help" in update.message.text:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode = 'MarkdownV2',
            text=
"""
Check out this starter guide on how to use me\!
_[insert link]_
"""
        )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id= update.effective_chat.id,text = "Sowii~~ I can't find any commands for that...!")

def run():
    application = ApplicationBuilder().concurrent_updates(True).token(get_key("telegram_key")).build()

    command_handler = CommandHandler(['start', 'get', 'visualise', 'commands' ], commands)
    application.add_handler(command_handler)

    find_song_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Find a song$"), song_input)],
        states={
            STATE_FIND_SONG: [MessageHandler(filters.TEXT, find_song)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Cancel$"), cancel)]
        )
    application.add_handler(find_song_handler)

    callback_handler = CallbackQueryHandler(callback)
    application.add_handler(callback_handler)

    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message, block = False)
    application.add_handler(message_handler)

    unknown_handler = MessageHandler(filters.COMMAND, unknown, block = False)
    application.add_handler(unknown_handler)

    application.run_polling(poll_interval= 5, timeout= 30)
    
    # application.run_webhook(
    #     listen='0.0.0.0',
    #     port=8443,
    #     secret_token='ASecretTokenIHaveChangedByNow',
    #     key='private.key',
    #     cert='cert.pem',
    #     webhook_url='https://example.com:8443'
    # )