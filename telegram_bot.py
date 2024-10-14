from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import db, os, configuration_values, requests
from pyVinted import Vinted, requester
from traceback import print_exc
from time import sleep
from asyncio import queues

VER = "0.4.3"


# verify if bot still running
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


# add a keyword to the db
async def add_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyword = context.args
    if not keyword:
        await update.message.reply_text('No keyword provided')
        return
    # merge keyword list into a string
    keyword = ' '.join(keyword).lower()
    if db.is_keyword_in_db(keyword) >= 1:
        await update.message.reply_text(f'Keyword "{keyword}" already exists')
    else:
        # add the keyword to the db
        db.add_keyword_to_db(keyword)
        # Create a string with all the keywords
        keyword_list = ("\n").join([str(i + 1) + ". " + j[0] for i, j in enumerate(db.get_keywords())])
        await update.message.reply_text(f'Keyword "{keyword}" added. \nCurrent keywords: \n{keyword_list}')


# remove a keyword from the db
async def remove_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyword = context.args
    if not keyword:
        await update.message.reply_text('No keyword provided')
        return
    keyword = ' '.join(keyword).lower()
    if keyword == "all":
        db.remove_all_keywords_from_db()
        await update.message.reply_text(f'All keywords removed')
        return
    if db.is_keyword_in_db(keyword) == 0:
        await update.message.reply_text(f'Keyword "{keyword}" does not exist')
    else:
        db.remove_keyword_from_db(keyword)
        # We'll write the keyword lis this way : 1. keyword\n2. keyword\n3. keyword
        keyword_list = ("\n").join([str(i + 1) + ". " + j[0] for i, j in enumerate(db.get_keywords())])
        await update.message.reply_text(f'Keyword "{keyword}" removed. \nCurrent keywords: \n{keyword_list}')


# get all keywords from the db
async def keywords(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyword_list = ("\n").join([str(i + 1) + ". " + j[0] for i, j in enumerate(db.get_keywords())])
    await update.message.reply_text(f'Current keywords: \n{keyword_list}')


async def create_allowlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db.create_allowlist()
    await update.message.reply_text(f'Allowlist created. Add countries by using /add_country "FR,BE,ES,IT,LU,DE etc."')


async def delete_allowlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db.delete_allowlist()
    await update.message.reply_text(f'Allowlist deleted. All countries are allowed.')


async def add_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    country = context.args
    if not country:
        await update.message.reply_text('No country provided')
        return
    # remove spaces
    country = ' '.join(country).replace(" ", "")
    if len(country) != 2:
        a = len(country)
        await update.message.reply_text('Invalid country code')
        return
    # if already in allowlist
    if country.upper() in (list := db.get_allowlist()):
        await update.message.reply_text(f'Country "{country.upper()}" already in allowlist. Current allowlist: {list}')
    else:
        db.add_to_allowlist(country.upper())
        await update.message.reply_text(f'Done. Current allowlist: {db.get_allowlist()}')


async def remove_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    country = context.args
    if not country:
        await update.message.reply_text('No country provided')
        return
    # remove spaces
    country = ' '.join(country).replace(" ", "")
    if len(country) != 2:
        await update.message.reply_text('Invalid country code')
        return
    db.remove_from_allowlist(country.upper())
    await update.message.reply_text(f'Done. Current allowlist: {db.get_allowlist()}')


async def allowlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if db.get_allowlist() == 0:
        await update.message.reply_text(f'No allowlist set. All countries are allowed.')
    else:
        await update.message.reply_text(f'Current allowlist: {db.get_allowlist()}')


async def send_new_post(content, url, text):
    async with bot:
        await bot.send_message(configuration_values.CHAT_ID, content, parse_mode="HTML", read_timeout=10,
                               write_timeout=10,
                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=text, url=url)]]))


def get_user_country(profile_id):
    url = configuration_values.VINTED_BASE_URL + f"/api/v2/users/{profile_id}?localize=false"
    response = requester.get(url)
    # That's a LOT of requests, so if we get a 429 we wait a bit before retrying once
    if response.status_code == 429:
        # In case of rate limit, we're switching the endpoint. This one is slower, but it doesn't RL as soon. 
        # We're limiting the items per page to 1 to grab as little data as possible
        url = configuration_values.VINTED_BASE_URL + f"/api/v2/users/{profile_id}/items?page=1&per_page=1"
        response = requester.get(url)
        try:
            user_country = response.json()["items"][0]["user"]["country_iso_code"]
        except KeyError:
            print("Couldn't get the country due to too many requests. Returning default value.")
            user_country = "XX"
    else:
        user_country = response.json()["user"]["country_iso_code"]
    return user_country


async def process_items():
    keywords = db.get_keywords()
    vinted = Vinted()
    # for each keyword we parse data
    for keyword in keywords:
        URL = configuration_values.VINTED_URL.format(keyword=keyword[0]).replace(" ", "%20")
        already_processed = keyword[1]
        data = vinted.items.search(URL)
        await items_queue.put((data, already_processed, keyword[0]))
        # Update processed value to start notifying
        db.update_keyword_processed(keyword[0])


async def background_worker(context: ContextTypes.DEFAULT_TYPE):
    # TODO : Lock while working
    try:
        await process_items()
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
        data, already_processed, keyword = await items_queue.get()
        for item in data:
            # Get the id of the item to check if it is already in the db
            id = item.id
            # TODO : Sort by category_id
            # If it's the first run, we add the item to the db and do nothing else
            if already_processed == 0:
                db.add_item_to_db(id, keyword)
                pass
            # If already in db, pass
            elif db.is_item_in_db(id) != 0:
                pass
            # If there's an allowlist and
            # If the user's country is not in the allowlist, we add it to the db and do nothing else
            elif db.get_allowlist() != 0 and (get_user_country(item.raw_data["user"]["id"])) not in (
                    db.get_allowlist() + ["XX"]):
                db.add_item_to_db(id, keyword)
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
                db.add_item_to_db(id, keyword)

async def set_commands(context: ContextTypes.DEFAULT_TYPE):
    await bot.set_my_commands([
            ("hello", "Verify if bot is running"),
            ("add_keyword", "Add a keyword to the bot"),
            ("remove_keyword", "Remove a keyword from the bot"),
            ("keywords", "List all keywords"),
            ("create_allowlist", "Create an allowlist"),
            ("delete_allowlist", "Delete the allowlist"),
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
app.add_handler(CommandHandler("add_keyword", add_keyword))
app.add_handler(CommandHandler("remove_keyword", remove_keyword))
app.add_handler(CommandHandler("keywords", keywords))
# Allowlist handlers
app.add_handler(CommandHandler("create_allowlist", create_allowlist))
app.add_handler(CommandHandler("delete_allowlist", delete_allowlist))
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
