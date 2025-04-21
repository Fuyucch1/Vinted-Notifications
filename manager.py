import multiprocessing
from apscheduler.schedulers.background import BackgroundScheduler
import time, telegram_bot
import db, core


def scraper_process(items_queue):
    print("Scrape process started")
    scraper_scheduler = BackgroundScheduler()
    scraper_scheduler.add_job(core.process_items, 'interval', seconds=5, args=[items_queue], name="scraper")
    scraper_scheduler.start()
    try:
        # Keep the process running
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scraper_scheduler.shutdown()
        print("Scrape process stopped")


def item_extractor(items_queue, new_items_queue):
    try:
        while True:
            # Check if there's an item in the queue
            core.clear_item_queue(items_queue, new_items_queue)
            time.sleep(0.1)  # Small sleep to prevent high CPU usage
    except (KeyboardInterrupt, SystemExit):
        print("Consumer process stopped")


def intermediate_process(queue):
    print("Intermediate process started")
    try:
        pass
    except (KeyboardInterrupt, SystemExit):
        print("Intermediate process stopped")
    except Exception as e:
        print(f"Error in intermediate process: {e}")


def telegram_bot_process(queue):
    print("Telegram bot process started")
    import asyncio
    try:
        # Import LeRobot
        from telegram_bot import LeRobot
        # The bot will run with app.run_polling() which is already in the module
        asyncio.run(LeRobot(queue))
    except (KeyboardInterrupt, SystemExit):
        print("Telegram bot process stopped")
    except Exception as e:
        print(f"Error in telegram bot process: {e}")


if __name__ == "__main__":
    # Create a shared queue
    items_queue = multiprocessing.Queue()
    new_items_queue = multiprocessing.Queue()

    # Create and start the telegram bot process
    telegram_process = multiprocessing.Process(target=telegram_bot_process, args=(new_items_queue,))
    telegram_process.start()

    # Create and start the scrape process
    scrape_process = multiprocessing.Process(target=scraper_process, args=(items_queue,))
    scrape_process.start()

    # Create the item extractor process
    item_extractor_process = multiprocessing.Process(target=item_extractor, args=(items_queue, new_items_queue))
    item_extractor_process.start()

    # Create and start the consumer process
    # intermediate_process = multiprocessing.Process(target=intermediate_process, args=(new_items_queue,))
    # intermediate_process.start()
    try:
        # Wait for processes to finish (which they won't unless interrupted)
        scrape_process.join()
        item_extractor_process.join()
        # intermediate_process.join()
        telegram_process.join()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("Main process interrupted")
        scrape_process.terminate()
        item_extractor_process.terminate()
        # intermediate_process.terminate()
        telegram_process.terminate()
        scrape_process.join()
        item_extractor_process.join()
        # intermediate_process.join()
        telegram_process.join()
        print("All processes terminated")
