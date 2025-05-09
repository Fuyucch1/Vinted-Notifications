from flask import Flask, Response
import threading, time, db, datetime, html
from logger import get_logger
from feedgen.feed import FeedGenerator

# Get logger for this module
logger = get_logger(__name__)


class RSSFeed:
    def __init__(self, queue):
        self.app = Flask(__name__)
        self.queue = queue
        self.items = []
        self.max_items = db.get_parameter("rss_max_items")

        # Initialize feed generator
        self.fg = FeedGenerator()
        self.fg.title('Vinted Notifications')
        self.fg.description('Latest items from Vinted matching your search queries')
        self.fg.link(href=f'http://localhost:{db.get_parameter("rss_port")}')
        self.fg.language('en')

        # Set up routes
        self.app.route('/')(self.serve_rss)

        # Start thread to check queue
        self.thread = threading.Thread(target=self.run_check_queue)
        self.thread.daemon = True
        self.thread.start()

    def run_check_queue(self):
        while True:
            try:
                self.check_rss_queue()
                time.sleep(0.1)  # Small sleep to prevent high CPU usage
            except Exception as e:
                logger.error(f"Error checking RSS queue: {str(e)}", exc_info=True)

    def check_rss_queue(self):
        if not self.queue.empty():
            try:
                content, url, text, buy_url, buy_text = self.queue.get()

                # Add item to the feed
                self.add_item_to_feed(content, url)
            except Exception as e:
                logger.error(f"Error processing item for RSS feed: {str(e)}", exc_info=True)

    def add_item_to_feed(self, content, url):
        # Extract title from content (assuming it's in the format from configuration_values.MESSAGE)
        title = "New Vinted Item"
        try:
            # Try to extract title from the content
            title_start = content.find('🆕 Title : ') + len('🆕 Title : ')
            if title_start > len('🆕 Title : '):
                title_end = content.find('\n', title_start)
                if title_end > 0:
                    title = content[title_start:title_end]
        except:
            pass

        # Create a new entry
        fe = self.fg.add_entry()
        fe.id(url)
        fe.title(title)
        fe.link(href=url)
        fe.description(html.escape(content))
        fe.published(datetime.datetime.now(datetime.timezone.utc))

        # Add to our items list (for tracking)
        self.items.append((title, url, content, datetime.datetime.now()))

        # Limit the number of items
        if len(self.items) > self.max_items:
            self.items.pop(0)

    def serve_rss(self):
        return Response(self.fg.rss_str(), mimetype='application/rss+xml')

    def run(self):

        try:
            port = db.get_parameter("rss_port")
            logger.info(f"Starting RSS feed server on port {port}")
            self.app.run(host='0.0.0.0', port=port)
        except Exception as e:
            logger.error(f"Error starting RSS feed server: {str(e)}", exc_info=True)


def rss_feed_process(queue):
    """
    Process function for the RSS feed.
    
    Args:
        queue (Queue): The queue to get new items from
    """
    logger.info("RSS feed process started")
    try:
        feed = RSSFeed(queue)
        feed.run()
    except (KeyboardInterrupt, SystemExit):
        logger.info("RSS feed process stopped")
    except Exception as e:
        logger.error(f"Error in RSS feed process: {e}", exc_info=True)
