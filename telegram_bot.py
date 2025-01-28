from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import db, os, configuration_values, requests
from pyVinted import Vinted, requester
from traceback import print_exc
from asyncio import queues
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

VER = "0.5.2"


# verify if bot still running
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


# add a keyword to the db
async def add_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = context.args
    if not query:
        await update.message.reply_text('No query provided.')
        return
    query = query[0]
    # Parse the URL and extract the query parameters
    parsed_url = urlparse(query)
    query_params = parse_qs(parsed_url.query)

    # Ensure the order flag is set to newest_first
    query_params['order'] = ['newest_first']
    # Remove time and search_id if provided
    query_params.pop('time', None)
    query_params.pop('search_id', None)

    searched_text = query_params.get('search_text')

    # Rebuild the query string and the entire URL
    new_query = urlencode(query_params, doseq=True)
    query = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment))

    if db.is_query_in_db(searched_text[0]) is True:
        await update.message.reply_text(f'Query already exists.')
    else:
        # add the keyword to the db
        db.add_query_to_db(query)
        # Create a string with all the keywords
        query_list = format_queries()
        await update.message.reply_text(f'Query added. \nCurrent queries: \n{query_list}')


# remove a keyword from the db
async def remove_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    number = context.args
    if not number:
        await update.message.reply_text('No number provided.')
        return
    number = number[0]
    if number == "all":
        db.remove_all_queries_from_db()
        await update.message.reply_text(f'All queries removed.')
        return
    # if number is not a number
    if not number[0].isdigit():
        await update.message.reply_text('Invalid number.')
        return
    else:
        db.remove_query_from_db(number)
        # We'll write the keyword lis this way : 1. keyword\n2. keyword\n3. keyword
        query_list = format_queries()
        await update.message.reply_text(f'Query removed. \nCurrent queries: \n{query_list}')


# get all keywords from the db
async def queries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query_list = format_queries()
    await update.message.reply_text(f'Current queries: \n{query_list}')


def format_queries():
    all_queries = db.get_queries()
    queries_keywords = []
    for query in all_queries:
        parsed_url = urlparse(query[0])
        query_params = parse_qs(parsed_url.query)

        # Extract the value of 'search_text'
        search_text = query_params.get('search_text', [None])
        queries_keywords.append(search_text)

    query_list = ("\n").join([str(i + 1) + ". " + j[0] for i, j in enumerate(queries_keywords)])
    return query_list


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
        await update.message.reply_text('Invalid country code')
        return
    # if already in allowlist
    if country.upper() in (country_list := db.get_allowlist()):
        await update.message.reply_text(f'Country "{country.upper()}" already in allowlist. Current allowlist: {country_list}')
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
        await bot.send_message(configuration_values.CHAT_ID, content, parse_mode="HTML", read_timeout=20,
                               write_timeout=20,
                               reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=text, url=url)]]))


def get_user_country(profile_id):
    # Users are shared between all Vinted platforms, so we can use any of them
    url = f"https://www.vinted.fr/api/v2/users/{profile_id}?localize=false"
    response = requester.get(url)
    # That's a LOT of requests, so if we get a 429 we wait a bit before retrying once
    if response.status_code == 429:
        # In case of rate limit, we're switching the endpoint. This one is slower, but it doesn't RL as soon. 
        # We're limiting the items per page to 1 to grab as little data as possible
        url = f"https://www.vinted.fr/api/v2/users/{profile_id}/items?page=1&per_page=1"
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
    all_queries = db.get_queries()
    vinted = Vinted()
    # for each keyword we parse data
    for query in all_queries:
        already_processed = query[1]
        data = vinted.items.search(query[0])
        await items_queue.put((data, already_processed, query[0]))
        # Update processed value to start notifying
        db.update_query_processed(query[0])


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
        data, already_processed, query = await items_queue.get()
        for item in data:
            # Get the id of the item to check if it is already in the db
            id = item.id
            # If it's the first run, we add the item to the db and do nothing else
            if already_processed == 0:
                db.add_item_to_db(id, query)
                pass
            # If already in db, pass
            elif db.is_item_in_db(id) != 0:
                pass
            # If there's an allowlist and
            # If the user's country is not in the allowlist, we add it to the db and do nothing else
            elif db.get_allowlist() != 0 and (get_user_country(item.raw_data["user"]["id"])) not in (
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
app.add_handler(CommandHandler("add_query", add_query))
app.add_handler(CommandHandler("remove_query", remove_query))
app.add_handler(CommandHandler("queries", queries))
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
