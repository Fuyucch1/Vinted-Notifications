from flask import Flask, Response
import threading
import time
from logger import get_logger
import configuration_values
from feedgen.feed import FeedGenerator
import datetime
import html

# Get logger for this module
logger = get_logger(__name__)


class RSSFeed:
    def __init__(self, queue):
        """
        Initialize the RSS feed handler.
        
        Args:
            queue (Queue): The queue to get new items from
        """
        self.app = Flask(__name__)
        self.queue = queue
        self.items = []
        self.max_items = configuration_values.RSS_MAX_ITEMS

        # Initialize feed generator
        self.fg = FeedGenerator()
        self.fg.title('Vinted Notifications')
        self.fg.description('Latest items from Vinted matching your search queries')
        self.fg.link(href=f'http://localhost:{configuration_values.RSS_PORT}')
        self.fg.language('en')

        # Set up routes
        self.app.route('/')(self.serve_rss)

        # Start thread to check queue
        self.thread = threading.Thread(target=self.run_check_queue)
        self.thread.daemon = True
        self.thread.start()

    def run_check_queue(self):
        """
        Continuously check the queue for new items.
        """
        while True:
            try:
                self.check_rss_queue()
                time.sleep(0.1)  # Small sleep to prevent high CPU usage
            except Exception as e:
                logger.error(f"Error checking RSS queue: {str(e)}", exc_info=True)

    def check_rss_queue(self):
        """
        Check the queue for new items and add them to the RSS feed.
        """
        if not self.queue.empty():
            try:
                content, url, text = self.queue.get()

                # Add item to the feed
                self.add_item_to_feed(content, url)
            except Exception as e:
                logger.error(f"Error processing item for RSS feed: {str(e)}", exc_info=True)

    def add_item_to_feed(self, content, url):
        """
        Add an item to the RSS feed.
        
        Args:
            content (str): The HTML content of the item
            url (str): The URL of the item
        """
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
        """
        Serve the RSS feed.
        
        Returns:
            Response: The RSS feed as an XML response
        """
        return Response(self.fg.rss_str(), mimetype='application/rss+xml')

    def run(self):
        """
        Run the Flask app to serve the RSS feed.
        """
        try:
            logger.info(f"Starting RSS feed server on port {configuration_values.RSS_PORT}")
            self.app.run(host='0.0.0.0', port=configuration_values.RSS_PORT)
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
