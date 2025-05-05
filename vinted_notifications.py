import multiprocessing, time, core, os, db, configuration_values
from apscheduler.schedulers.background import BackgroundScheduler
from logger import get_logger
from rss_feed_plugin.rss_feed import rss_feed_process
from web_ui_plugin.web_ui import web_ui_process

# Get logger for this module
logger = get_logger(__name__)

# Global process references
telegram_process = None
rss_process = None
scrape_process = None
current_query_refresh_delay = None

def scraper_process(items_queue):
    logger.info("Scrape process started")

    # Get the query refresh delay from the database
    current_query_refresh_delay = int(db.get_parameter("query_refresh_delay"))
    logger.info(f"Using query refresh delay of {current_query_refresh_delay} seconds")

    scraper_scheduler = BackgroundScheduler()
    scraper_scheduler.add_job(core.process_items, 'interval', seconds=current_query_refresh_delay, args=[items_queue],
                              name="scraper")
    scraper_scheduler.start()
    try:
        # Keep the process running
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scraper_scheduler.shutdown()
        logger.info("Scrape process stopped")


def item_extractor(items_queue, new_items_queue):
    logger.info("Item extractor process started")
    try:
        while True:
            # Check if there's an item in the queue
            core.clear_item_queue(items_queue, new_items_queue)
            time.sleep(0.1)  # Small sleep to prevent high CPU usage
    except (KeyboardInterrupt, SystemExit):
        logger.info("Consumer process stopped")


def dispatcher_function(input_queue, rss_queue, telegram_queue):
    logger.info("Dispatcher process started")
    try:
        while True:
            # Get from input queue
            item = input_queue.get()
            # Send to RSS queue
            rss_queue.put(item)
            #
            telegram_queue.put(item)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Dispatcher process stopped")
    except Exception as e:
        logger.error(f"Error in dispatcher process: {e}", exc_info=True)


def telegram_bot_process(queue):
    logger.info("Telegram bot process started")
    import asyncio
    try:
        # Import LeRobot
        from telegram_bot_plugin.telegram_bot import LeRobot
        # The bot will run with app.run_polling() which is already in the module
        asyncio.run(LeRobot(queue))
    except (KeyboardInterrupt, SystemExit):
        logger.info("Telegram bot process stopped")
    except Exception as e:
        logger.error(f"Error in telegram bot process: {e}", exc_info=True)


def check_refresh_delay(items_queue):
    """Check if the query refresh delay has changed and update the scheduler if needed"""
    global scrape_process, current_query_refresh_delay

    # Check if the scheduler is running

    if scrape_process is None or not scrape_process.is_alive():
        return

    # Get the current value from the database
    try:
        new_delay = int(db.get_parameter("query_refresh_delay"))

        # If the delay has changed, update the scheduler
        if new_delay != current_query_refresh_delay:
            logger.info(f"Query refresh delay changed from {current_query_refresh_delay} to {new_delay} seconds")

            # Update the global variable
            current_query_refresh_delay = new_delay

            # Remove the existing job and add a new one with the updated interval
            scrape_process.terminate()
            scrape_process.join()
            scrape_process = multiprocessing.Process(target=scraper_process, args=(items_queue,))
            scrape_process.start()

            logger.info(f"Scheduler updated with new refresh delay of {new_delay} seconds")
    except Exception as e:
        logger.error(f"Error updating refresh delay: {e}", exc_info=True)


def monitor_processes(items_queue, telegram_queue, rss_queue):
    global telegram_process, rss_process

    # Check if the query refresh delay has changed
    check_refresh_delay(items_queue)

    ### TELEGRAM ###
    # Check telegram process status
    telegram_should_run = db.get_parameter('telegram_process_running') == 'True'
    # Check if the telegram token and chat ID are set
    telegram_token = db.get_parameter('telegram_token')
    telegram_chat_id = db.get_parameter('telegram_chat_id')
    if not telegram_token or not telegram_chat_id:
        telegram_should_run = False
    telegram_is_running = telegram_process is not None and telegram_process.is_alive()

    if telegram_should_run and not telegram_is_running:
        # Start telegram process
        logger.info("Starting telegram bot process.")
        telegram_process = multiprocessing.Process(target=telegram_bot_process, args=(telegram_queue,))
        telegram_process.start()
    elif not telegram_should_run and telegram_is_running:
        # Stop telegram process
        logger.info("Stopping telegram bot process.")
        telegram_process.terminate()
        telegram_process.join()
        telegram_process = None

    ### RSS ###
    # Check RSS process status
    rss_should_run = db.get_parameter('rss_process_running') == 'True'
    rss_is_running = rss_process is not None and rss_process.is_alive()

    if rss_should_run and not rss_is_running:
        # Start RSS process
        logger.info("Starting RSS process based on database status")
        rss_process = multiprocessing.Process(target=rss_feed_process, args=(rss_queue,))
        rss_process.start()
    elif not rss_should_run and rss_is_running:
        # Stop RSS process
        logger.info("Stopping RSS process based on database status")
        rss_process.terminate()
        rss_process.join()
        rss_process = None


def plugin_checker():
    # Get telegram and rss enable status
    telegram_enabled = db.get_parameter('telegram_enabled')
    logger.info("Telegram enabled: {}".format(telegram_enabled))
    rss_enabled = db.get_parameter('rss_enabled')
    logger.info("RSS enabled: {}".format(rss_enabled))

    # Reset process status at startup
    db.set_parameter('telegram_process_running', telegram_enabled)
    db.set_parameter('rss_process_running', rss_enabled)


if __name__ == "__main__":
    # Starting sequence
    # Db check
    if not os.path.exists("./vinted_notifications.db"):
        db.create_sqlite_db()
        logger.info("Database created successfully")
    # Set version
    db.set_parameter('version', "1.0.1")

    # Plugin checker
    plugin_checker()

    # Create a shared queue
    items_queue = multiprocessing.Queue()
    new_items_queue = multiprocessing.Queue()
    rss_queue = multiprocessing.Queue()
    telegram_queue = multiprocessing.Queue()

    # 1. Create and start the scrape process
    # This process will scrape items and put them in the items_queue
    current_query_refresh_delay = int(db.get_parameter("query_refresh_delay"))
    scrape_process = multiprocessing.Process(target=scraper_process, args=(items_queue,))
    scrape_process.start()

    # 2. Create the item extractor process
    # This process will extract items from the items_queue and put them in the new_items_queue
    item_extractor_process = multiprocessing.Process(target=item_extractor, args=(items_queue, new_items_queue))
    item_extractor_process.start()

    # 3. Create the dispatcher process
    # This process will handle the new items and send them to the enabled services
    dispatcher_process = multiprocessing.Process(target=dispatcher_function,
                                                 args=(new_items_queue, rss_queue, telegram_queue,))
    dispatcher_process.start()

    # 4. Set up a scheduler to monitor processes
    # This will check the process status in the database and start/stop processes as needed
    monitor_scheduler = BackgroundScheduler()
    monitor_scheduler.add_job(monitor_processes, 'interval', seconds=5, args=[items_queue, telegram_queue, rss_queue],
                              name="process_monitor")
    monitor_scheduler.start()

    # 5. Create and start the Web UI process
    # This process will provide a web interface to control the application
    web_ui_process_instance = multiprocessing.Process(target=web_ui_process)
    web_ui_process_instance.start()
    logger.info(f"Web UI started on port {configuration_values.WEB_UI_PORT}")


    try:
        # Wait for processes to finish (which they won't unless interrupted)
        scrape_process.join()
        item_extractor_process.join()
        dispatcher_process.join()
        web_ui_process_instance.join()

        # plugins
        if telegram_process:
            telegram_process.join()
        if rss_process:
            rss_process.join()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        logger.info("Main process interrupted")

        # Shutdown the monitor scheduler
        monitor_scheduler.shutdown()

        # Terminate all processes
        scrape_process.terminate()
        item_extractor_process.terminate()
        dispatcher_process.terminate()
        # Terminate web UI process
        web_ui_process_instance.terminate()

        # Plugins

        if telegram_process and telegram_process.is_alive():
            telegram_process.terminate()
            # Set the process status in the database
            db.set_parameter('telegram_process_running', 'False')
        if rss_process and rss_process.is_alive():
            rss_process.terminate()
            # Set the process status in the database
            db.set_parameter('rss_process_running', 'False')

        # Wait for all processes to terminate
        scrape_process.join()
        item_extractor_process.join()
        dispatcher_process.join()
        web_ui_process_instance.join()

        # Plugins
        if telegram_process:
            telegram_process.join()
        if rss_process:
            rss_process.join()

        logger.info("All processes terminated")
