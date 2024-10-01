from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import db, os, configuration_values, requests
from pyVinted import Vinted
from traceback import print_exc

VER = "0.2.2"

# verify if bot still running
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


# add a keyword to the db
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyword = context.args
    if not keyword:
        await update.message.reply_text('No keyword provided')
        return
    # merge keyword list into a string
    keyword = ' '.join(keyword)
    if db.is_keyword_in_db(keyword) >= 1:
        await update.message.reply_text(f'Keyword "{keyword}" already exists')
    else:
        # add the keyword to the db
        db.add_keyword_to_db(keyword)
        # Create a string with all the keywords
        keyword_list = (", ").join([i[0] for i in db.get_keywords()])
        await update.message.reply_text(f'Keyword "{keyword}" added. \nCurrent keywords: {keyword_list}')


# remove a keyword from the db
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyword = context.args
    if not keyword:
        await update.message.reply_text('No keyword provided')
        return
    keyword = ' '.join(keyword)
    if keyword == "all":
        db.remove_all_keywords_from_db()
        await update.message.reply_text(f'All keywords removed')
        return
    if db.is_keyword_in_db(keyword) == 0:
        await update.message.reply_text(f'Keyword "{keyword}" does not exist')
    else:
        db.remove_keyword_from_db(keyword)
        keyword_list = (", ").join([i[0] for i in db.get_keywords()])
        await update.message.reply_text(f'Keyword "{keyword}" removed. \nCurrent keywords: {keyword_list}')


# get all keywords from the db
async def keywords(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyword_list = (", ").join([i[0] for i in db.get_keywords()])
    await update.message.reply_text(f'Current keywords: {keyword_list}')


async def send_new_post(content, image):
    async with bot:
        await bot.send_message(configuration_values.CHAT_ID, content, read_timeout=10)
    if image is not None:
        try:
            async with bot:
                await bot.send_photo(configuration_values.CHAT_ID, image, read_timeout=10)
        except Exception:
            print_exc()


async def process_items():
    keywords = db.get_keywords()
    vinted = Vinted()
    # for each keyword we parse data
    for keyword in keywords:
        URL = configuration_values.VINTED_URL.format(keyword=keyword[0]).replace(" ", "%20")

        already_processed = keyword[1]
        data = vinted.items.search(URL)

        for item in data:

            # Parse pictures, if there is no picture we put to None
            if item.photo is not None:
                # Sometimes this bugs out, dunno why, so we put it in a try except
                try:
                    image = item.photo
                except:
                    image = None

            # Get the id of the item to check if it is already in the db
            id = item.id

            # Process the item if it's not in the db
            if db.is_item_in_db(id) == 0:
                content = configuration_values.MESSAGE.format(
                    title=item.title,
                    price=str(item.price) + " €",
                    brand=item.brand_title,
                    url=item.url
                )
                # Send notification
                if already_processed == 1:
                    await send_new_post(content, image)
                # Add the item to the db
                db.add_item_to_db(id, keyword[0])
            else:
                pass
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
            await send_new_post("A new version is available, please update the bot.", None)
        else:
            print("You have the latest version!")

async def clean_db(context: ContextTypes.DEFAULT_TYPE):
    db.clean_db()

if not os.path.exists("vinted.db"):
    db.create_sqlite_db()

bot = Bot(configuration_values.TOKEN)
app = ApplicationBuilder().token(configuration_values.TOKEN).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("remove", remove))
app.add_handler(CommandHandler("keywords", keywords))

job_queue = app.job_queue
# Every minute we check for new listings
job_queue.run_repeating(background_worker, interval=60, first=1)
# Every day we check for a new version
job_queue.run_repeating(check_version, interval=86400, first=1)
# Every day we clean the db
job_queue.run_repeating(clean_db, interval=86400, first=1)

app.run_polling()
