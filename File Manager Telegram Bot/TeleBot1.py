from telegram.ext import Updater, PicklePersistence, CallbackQueryHandler, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

persistence = PicklePersistence(filename='3_FilePersis')

file_ids = {} #CallbackContext.user_data

def start(update: Update, context: CallbackContext):
    # Get the user's ID
    #user_id = update.effective_user.id

    # Check if we have any data saved for this user
    if 'files' not in context.user_data:
        # If not, create an empty dictionary to store the user's files
        context.user_data['files'] = {}
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Send me a file and I will store it for you.')

def handle_file(update: Update, context: CallbackContext):
    #user_id = update.effective_user.id
    """Handle files uploaded by the user."""
    file_id = update.message.document.file_id
    file_name = update.message.document.file_name
    file_ids[file_name] = file_id
    context.user_data['files'][file_name] = file_id
    update.message.reply_text(f'{file_name} has been saved.')


def get_file(update: Update, context: CallbackContext):
    """Get a file by its name."""
    query = update.message.text
    if query in file_ids:
        send_file(context.bot, update.message.chat_id, file_ids[query])
    else:
        update.message.reply_text(f'Sorry, {query} is not in the list(get_files) of saved files.')

def send_file(bot, chat_id, file_id):
    """Send a file to the user."""
    bot.send_document(chat_id=chat_id, document=file_id)


def list_files(update: Update, context: CallbackContext):
    """List all saved files."""
    #user_id = update.message.chat_id
    files = context.user_data  # Retrieve the stored files from context.user_data
    if files:
        file_list = "\n".join(files.keys())
        message = f"List of saved files:\n{file_list}"
    else:
        message = "No files found."
    #context.bot.send_message(chat_id=user_id, text=message)'''

    keyboard = []
    for file_name in files['files']:
        keyboard.append([InlineKeyboardButton(file_name, callback_data=file_name)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Choose a file:', reply_markup=reply_markup)


def button_callback(update: Update, context: CallbackContext):
    """Handle button callbacks."""
    query = update.callback_query
    file_name = query.data
    files = context.user_data
    if file_name in files['files']:
        send_file(context.bot, query.message.chat_id, files['files'][file_name])
    else:
        query.answer(text=f'Sorry, {file_name} is not in the list of saved files.')

def main():
    """Start the bot."""
    updater = Updater('TOKEN',persistence=persistence, use_context=True)

    # Add handlers for various commands
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.document, handle_file))
    updater.dispatcher.add_handler(CommandHandler('list_files', list_files))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, get_file))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_callback))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()