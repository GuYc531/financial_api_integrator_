import logging
import logging.handlers
import os


class Logger:
    def __init__(self, name: str, log_file: str = None, level=logging.INFO, cloud_log=False):
        """
        Initialize the Logger.

        :param name: Logger name (usually __name__).
        :param log_file: Optional file path to log to.
        :param level: Logging level (e.g., logging.INFO, logging.DEBUG).
        :param cloud_log: boolean states if sending logs to cloud vendor (not implemented fully)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Optional file handler
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        if cloud_log:
            self._add_cloud_vendor_handler()

    def get_logger(self):
        return self.logger

    def _add_cloud_vendor_handler(self):
        """
        General function for connecting the logs into cloud provider, in order to monitor
        the data pipeline and trace errors
        :return:
        """
        try:
            # client = cloud_logging.Client()
            # client.setup_logging()

            self.logger.info("Cloud Logging handler initialized.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Cloud Logging: {e}")
