from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import db, configuration_values, requests
import core
from logger import get_logger

VER = "0.6.0"

# Get logger for this module
logger = get_logger(__name__)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text(
            f'Hello {update.effective_user.first_name}! Vinted-Notifications is running under version {VER}.\n')
    except Exception as e:
        logger.error(f"Error in hello command: {str(e)}", exc_info=True)
        try:
            await update.message.reply_text('An error occurred. Please try again later.')
        except:
            pass


class LeRobot:
    def __init__(self, queue):
        from telegram import Bot
        from telegram.ext import ApplicationBuilder, CommandHandler
        import db, os, configuration_values

        try:
            if not os.path.exists("vinted.db"):
                db.create_sqlite_db()

            self.bot = Bot(configuration_values.TOKEN)
            self.app = ApplicationBuilder().token(configuration_values.TOKEN).build()

            # Create the item queue to send to telegram
            self.new_items_queue = queue

            # Handler verify if bot is running
            self.app.add_handler(CommandHandler("hello", hello))
            # Keyword handlers
            self.app.add_handler(CommandHandler("add_query", self.add_query))
            self.app.add_handler(CommandHandler("remove_query", self.remove_query))
            self.app.add_handler(CommandHandler("queries", self.queries))
            # Allowlist handlers
            self.app.add_handler(CommandHandler("clear_allowlist", self.clear_allowlist))
            self.app.add_handler(CommandHandler("add_country", self.add_country))
            self.app.add_handler(CommandHandler("remove_country", self.remove_country))
            self.app.add_handler(CommandHandler("allowlist", self.allowlist))

            # TODO : Help command

            # TODO : Manage removals after current items have been processed.

            job_queue = self.app.job_queue
            # Set the commands
            job_queue.run_once(self.set_commands, when=1)
            # Every day we check for a new version
            job_queue.run_repeating(self.check_version, interval=86400, first=1)
            # Every day we clean the db
            job_queue.run_repeating(self.clean_db, interval=86400, first=1)
            # Every second we check for new posts to send to telegram
            job_queue.run_repeating(self.check_telegram_queue, interval=1, first=1)

            self.app.run_polling()
        except Exception as e:
            logger.error(f"Error initializing bot: {str(e)}", exc_info=True)

    # Verify if the bot is running

    ### QUERIES ###

    # Add a query to the db
    async def add_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
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
        except Exception as e:
            logger.error(f"Error adding query: {str(e)}", exc_info=True)
            try:
                await update.message.reply_text('An error occurred while adding the query. Please try again later.')
            except:
                pass

    # Remove a query from the db
    async def remove_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
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
        except Exception as e:
            logger.error(f"Error removing query: {str(e)}", exc_info=True)
            try:
                await update.message.reply_text('An error occurred while removing the query. Please try again later.')
            except:
                pass

    # get all queries from the db
    async def queries(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            query_list = core.get_formatted_query_list()
            await update.message.reply_text(f'Current queries: \n{query_list}')
        except Exception as e:
            logger.error(f"Error retrieving queries: {str(e)}", exc_info=True)
            try:
                await update.message.reply_text(
                    'An error occurred while retrieving the queries. Please try again later.')
            except:
                pass

    ### ALLOWLIST ###

    async def clear_allowlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            db.clear_allowlist()
            await update.message.reply_text(f'Allowlist cleared. All countries are allowed.')
        except Exception as e:
            logger.error(f"Error clearing allowlist: {str(e)}", exc_info=True)
            try:
                await update.message.reply_text(
                    'An error occurred while clearing the allowlist. Please try again later.')
            except:
                pass

    async def add_country(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            country = context.args
            if not country:
                await update.message.reply_text('No country provided')
                return

            # Process the country using the core function
            message, country_list = core.process_add_country(' '.join(country))

            await update.message.reply_text(f'{message} Current allowlist: {country_list}')
        except Exception as e:
            logger.error(f"Error adding country to allowlist: {str(e)}", exc_info=True)
            try:
                await update.message.reply_text(
                    'An error occurred while adding the country to the allowlist. Please try again later.')
            except:
                pass

    async def remove_country(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            country = context.args
            if not country:
                await update.message.reply_text('No country provided')
                return

            # Process the country using the core function
            message, country_list = core.process_remove_country(' '.join(country))

            await update.message.reply_text(f'{message} Current allowlist: {country_list}')
        except Exception as e:
            logger.error(f"Error removing country from allowlist: {str(e)}", exc_info=True)
            try:
                await update.message.reply_text(
                    'An error occurred while removing the country from the allowlist. Please try again later.')
            except:
                pass

    async def allowlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            if db.get_allowlist() == 0:
                await update.message.reply_text(f'No allowlist set. All countries are allowed.')
            else:
                await update.message.reply_text(f'Current allowlist: {db.get_allowlist()}')
        except Exception as e:
            logger.error(f"Error retrieving allowlist: {str(e)}", exc_info=True)
            try:
                await update.message.reply_text(
                    'An error occurred while retrieving the allowlist. Please try again later.')
            except:
                pass

    ### TELEGRAM SPECIFIC FUNCTIONS ###

    async def send_new_post(self, content, url, text):
        try:
            logger.info(f"Sending new post: {content} - {url} - {text}")
            async with self.bot:
                await self.bot.send_message(configuration_values.CHAT_ID, content, parse_mode="HTML", read_timeout=40,
                                            write_timeout=40,
                                            reply_markup=InlineKeyboardMarkup(
                                                [[InlineKeyboardButton(text=text, url=url)]]))
        except Exception as e:
            logger.error(f"Error sending new post: {str(e)}", exc_info=True)

    async def check_version(self, context: ContextTypes.DEFAULT_TYPE):
        try:
            # get latest version from the repository
            url = f"https://github.com/Fuyucch1/Vinted-Notifications/releases/latest"
            response = requests.get(url)

            if response.status_code == 200:
                if VER != response.url.split('/')[-1]:
                    await self.send_new_post("A new version is available, please update the bot.", url, "Open Github")
        except Exception as e:
            logger.error(f"Error checking for new version: {str(e)}", exc_info=True)

    async def clean_db(self, context: ContextTypes.DEFAULT_TYPE):
        try:
            db.clean_db()
        except Exception as e:
            logger.error(f"Error cleaning database: {str(e)}", exc_info=True)

    async def check_telegram_queue(self, context: ContextTypes.DEFAULT_TYPE):
        try:
            if not self.new_items_queue.empty():
                content, url, text = self.new_items_queue.get()
                await self.send_new_post(content, url, text)
        except Exception as e:
            logger.error(f"Error checking telegram queue: {str(e)}", exc_info=True)

    async def set_commands(self, context: ContextTypes.DEFAULT_TYPE):
        try:
            await self.bot.set_my_commands([
                ("hello", "Verify if bot is running"),
                ("add_query", "Add a keyword to the bot"),
                ("remove_query", "Remove a keyword from the bot"),
                ("queries", "List all keywords"),
                ("clear_allowlist", "Clear the allowlist"),
                ("add_country", "Add a country to the allowlist"),
                ("remove_country", "Remove a country from the allowlist"),
                ("allowlist", "List all countries in the allowlist")
            ])
            logger.info("Bot commands set successfully")
        except Exception as e:
            logger.error(f"Error setting bot commands: {str(e)}", exc_info=True)
