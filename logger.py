import logging
import os


class Logger:

    def __init__(self, namespace='AppLogger', log_dir='logs', log_file='app.log'):
        log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        self.logger = logging.getLogger(namespace)
        self.logger.setLevel(log_level)

        # Ensure the logs directory exists
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Only add handlers if they are not already added
        if not self.logger.hasHandlers():
            # Create a file handler
            file_handler = logging.FileHandler(os.path.join(log_dir, log_file))
            file_handler.setLevel(log_level)

            # Create a console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)

            # Create a logging format
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Add the handlers to the logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger
