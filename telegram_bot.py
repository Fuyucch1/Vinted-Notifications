from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import db, os, configuration_values, requests
from pyVintedVN import Vinted, requester
from traceback import print_exc
from asyncio import queues
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import core

VER = "0.6.0"


# Verify if the bot is running
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Hello {update.effective_user.first_name}! Vinted-Notifications is running under version {VER}.\n')


### QUERIES ###

# Add a query to the db
async def add_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = context.args
    if not query:
        await update.message.reply_text('No query provided.')
        return

    # Process the query using the core function
    message, is_new_query = core.process_query(query[0])

    if is_new_query:
        # Create a string with all the keywords
        query_list = core.get_formatted_query_list()
        await update.message.reply_text(f'{message} \nCurrent queries: \n{query_list}')
    else:
        await update.message.reply_text(message)


# Remove a query from the db
async def remove_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    number = context.args
    if not number:
        await update.message.reply_text('No number provided.')
        return

    # Process the removal using the core function
    message, success = core.process_remove_query(number[0])

    if success:
        if number[0] == "all":
            await update.message.reply_text(message)
        else:
            # Get the updated list of queries
            query_list = core.get_formatted_query_list()
            await update.message.reply_text(f'{message} \nCurrent queries: \n{query_list}')
    else:
        await update.message.reply_text(message)

# get all queries from the db
async def queries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query_list = core.get_formatted_query_list()
    await update.message.reply_text(f'Current queries: \n{query_list}')


### ALLOWLIST ###

async def clear_allowlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db.clear_allowlist()
    await update.message.reply_text(f'Allowlist cleared. All countries are allowed.')

async def add_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    country = context.args
    if not country:
        await update.message.reply_text('No country provided')
        return

    # Process the country using the core function
    message, country_list = core.process_add_country(' '.join(country))

    await update.message.reply_text(f'{message} Current allowlist: {country_list}')

async def remove_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    country = context.args
    if not country:
        await update.message.reply_text('No country provided')
        return

    # Process the country using the core function
    message, country_list = core.process_remove_country(' '.join(country))

    await update.message.reply_text(f'{message} Current allowlist: {country_list}')

async def allowlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if db.get_allowlist() == 0:
        await update.message.reply_text(f'No allowlist set. All countries are allowed.')
    else:
        await update.message.reply_text(f'Current allowlist: {db.get_allowlist()}')


### TELEGRAM SPECIFIC FUNCTIONS ###

async def send_new_post(content, url, text):
    async with bot:
        await bot.send_message(configuration_values.CHAT_ID, content, parse_mode="HTML", read_timeout=40,
                               write_timeout=40,
                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=text, url=url)]]))


async def background_worker(context: ContextTypes.DEFAULT_TYPE):
    # TODO : Lock while working
    try:
        await core.process_items(items_queue)
    except Exception:
        print_exc()


async def check_version(context: ContextTypes.DEFAULT_TYPE):
    # get latest version from the repository
    url = f"https://github.com/Fuyucch1/Vinted-Notifications/releases/latest"
    response = requests.get(url)

    if response.status_code == 200:
        if VER != response.url.split('/')[-1]:
            await send_new_post("A new version is available, please update the bot.", url, "Open Github")


async def clean_db(context: ContextTypes.DEFAULT_TYPE):
    db.clean_db()


async def clear_telegram_queue(context: ContextTypes.DEFAULT_TYPE):
    while 1:
        content, url, text = await new_items_queue.get()
        await send_new_post(content, url, text)


async def clear_item_queue(context: ContextTypes.DEFAULT_TYPE):
    while 1:
        data, query = await items_queue.get()
        for item in data:
            # Get the id of the item to check if it is already in the db
            id = item.id
            # If already in db, pass
            if db.is_item_in_db(id) != 0:
                pass
            # If there's an allowlist and
            # If the user's country is not in the allowlist, we add it to the db and do nothing else
            elif db.get_allowlist() != 0 and (core.get_user_country(item.raw_data["user"]["id"])) not in (
                    db.get_allowlist() + ["XX"]):
                db.add_item_to_db(id, query)
                pass
            else:
                # We create the message
                content = configuration_values.MESSAGE.format(
                    title=item.title,
                    price=str(item.price) + " €",
                    brand=item.brand_title,
                    image=None if item.photo is None else item.photo
                )
                # add the item to the queue
                await new_items_queue.put((content, item.url, "Open Vinted"))
                # Add the item to the db
                db.add_item_to_db(id, query)


async def set_commands(context: ContextTypes.DEFAULT_TYPE):
    await bot.set_my_commands([
        ("hello", "Verify if bot is running"),
        ("add_query", "Add a keyword to the bot"),
        ("remove_query", "Remove a keyword from the bot"),
        ("queries", "List all keywords"),
        ("clear_allowlist", "Clear the allowlist"),
        ("add_country", "Add a country to the allowlist"),
        ("remove_country", "Remove a country from the allowlist"),
        ("allowlist", "List all countries in the allowlist")
    ])


if not os.path.exists("vinted.db"):
    db.create_sqlite_db()

bot = Bot(configuration_values.TOKEN)
app = ApplicationBuilder().token(configuration_values.TOKEN).build()

# Create the item queue to process
items_queue = queues.Queue()
# Create the item queue to send to telegram
new_items_queue = queues.Queue()

# Handler verify if bot is running
app.add_handler(CommandHandler("hello", hello))
# Keyword handlers
app.add_handler(CommandHandler("add_query", add_query))
app.add_handler(CommandHandler("remove_query", remove_query))
app.add_handler(CommandHandler("queries", queries))
# Allowlist handlers
app.add_handler(CommandHandler("clear_allowlist", clear_allowlist))
app.add_handler(CommandHandler("add_country", add_country))
app.add_handler(CommandHandler("remove_country", remove_country))
app.add_handler(CommandHandler("allowlist", allowlist))

# TODO : Help command

# TODO : Manage removals after current items have been processed.

job_queue = app.job_queue
# Every minute we check for new listings
job_queue.run_repeating(background_worker, interval=60, first=10)
# Every day we check for a new version
job_queue.run_repeating(check_version, interval=86400, first=1)
# Every day we clean the db
job_queue.run_repeating(clean_db, interval=86400, first=1)
# Every second we send the posts to telegram
job_queue.run_once(clear_telegram_queue, when=1)
# Every second we process the items
job_queue.run_once(clear_item_queue, when=1)
# Set the commands
job_queue.run_once(set_commands, when=1)

print("Bot started. Head to your telegram and type /hello to check if it's running.")

app.run_polling()
