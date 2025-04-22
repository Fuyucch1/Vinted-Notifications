import multiprocessing
from apscheduler.schedulers.background import BackgroundScheduler
import time, core
from logger import get_logger
import configuration_values
from rss_feed import rss_feed_process

# Get logger for this module
logger = get_logger(__name__)


def scraper_process(items_queue):
    logger.info("Scrape process started")
    scraper_scheduler = BackgroundScheduler()
    scraper_scheduler.add_job(core.process_items, 'interval', seconds=1, args=[items_queue], name="scraper")
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
        from telegram_bot import LeRobot
        # The bot will run with app.run_polling() which is already in the module
        asyncio.run(LeRobot(queue))
    except (KeyboardInterrupt, SystemExit):
        logger.info("Telegram bot process stopped")
    except Exception as e:
        logger.error(f"Error in telegram bot process: {e}", exc_info=True)


if __name__ == "__main__":
    # Create a shared queue
    items_queue = multiprocessing.Queue()
    new_items_queue = multiprocessing.Queue()
    rss_queue = multiprocessing.Queue()
    telegram_queue = multiprocessing.Queue()

    # 1. Create and start the scrape process
    # This process will scrape items and put them in the items_queue
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

    # 4. Create and start the telegram bot process
    # This process will handle the new items and send them to the telegram bot
    telegram_process = multiprocessing.Process(target=telegram_bot_process, args=(telegram_queue,))
    telegram_process.start()

    # 5. Create and start the RSS feed process if enabled
    # This process will handle the new items and add them to the RSS feed
    rss_process = None
    if configuration_values.RSS_ENABLED:
        rss_process = multiprocessing.Process(target=rss_feed_process, args=(rss_queue,))
        rss_process.start()


    try:
        # Wait for processes to finish (which they won't unless interrupted)
        scrape_process.join()
        item_extractor_process.join()
        dispatcher_process.join()
        telegram_process.join()
        if configuration_values.RSS_ENABLED and rss_process:
            rss_process.join()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        logger.info("Main process interrupted")
        scrape_process.terminate()
        item_extractor_process.terminate()
        dispatcher_process.terminate()
        telegram_process.terminate()
        if configuration_values.RSS_ENABLED and rss_process:
            rss_process.terminate()
        scrape_process.join()
        item_extractor_process.join()
        dispatcher_process.join()
        telegram_process.join()
        if configuration_values.RSS_ENABLED and rss_process:
            rss_process.join()
        logger.info("All processes terminated")
