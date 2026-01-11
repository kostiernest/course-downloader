import sys
from logging import getLogger, Logger, FileHandler, StreamHandler, Formatter, DEBUG, INFO


def setup_logging(logger_file_path: str) -> Logger:
	"""
	Setups main logger for project.
	Args:
		logger_file_path(str): Path to logging file.
	Returns:
		Logger: Object of main Logger.
	"""

	#Main logger
	logger = getLogger()
	logger.setLevel(DEBUG)

	#Handlers
	file_handler = FileHandler(filename=logger_file_path, mode="a", encoding="utf-8")
	file_handler.setLevel(DEBUG)

	stream_handler = StreamHandler(stream=sys.stdout)
	stream_handler.setLevel(INFO)

	#Formatters
	message_format = "%(asctime)s | %(name)s | %(funcName)s | [%(levelname)s] - %(message)s"
	date_format = "%Y-%m-%d %H:%M:%S"
	formatter = Formatter(fmt=message_format, datefmt=date_format)

	#Adding formatters to handlers
	file_handler.setFormatter(formatter)
	stream_handler.setFormatter(formatter)

	#Adding handlers to logger
	logger.addHandler(file_handler)
	logger.addHandler(stream_handler)

	return logger

if __name__ == "__main__":
	pass