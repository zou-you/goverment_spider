import os
import logging
from typing import Union
from pathlib import Path
from logging import handlers

Pathlike = Union[str, Path]

# 设置日志对象
def setup_logger(
    log_name: str,
    log_filename: Pathlike, 
    log_level: str = "info",
    use_console: bool = True
    ) -> logging:
    """
    Args:
      log_name:
        The name of log.
      log_filename:
        The filename to save the log.
      log_level:
        The log level to use, e.g., "debug", "info", "warning", "error", "critical"
      use_console:
        True to also print logs to console.
    """

    # 0、基础设置
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    
    level = logging.ERROR
    if log_level == "debug":
        level = logging.DEBUG
    elif log_level == "info":
        level = logging.INFO
    elif log_level == "warning":
        level = logging.WARNING
    elif log_level == "critical":
        level = logging.CRITICAL

    # 1、创建日志收集器
    logger = logging.getLogger(log_name)
 
    # 2、创建日志收集器的等级
    logger.setLevel(level=level)
 
    # 3、创建日志收集渠道和等级
    fh = handlers.TimedRotatingFileHandler(filename=log_filename, when="D",interval=1,backupCount=10,encoding="utf-8")
    fh.setLevel(level=level)
    logger.addHandler(fh)
 
    # 4、设置日志的输出格式
    formats = "%(asctime)s - [%(funcName)s-->line:%(lineno)d] - %(levelname)s:%(message)s"
    log_format = logging.Formatter(fmt=formats)
    fh.setFormatter(log_format)

    # 在终端打印
    if use_console:
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(logging.Formatter(formats))
        logger.addHandler(console)
        
    return logger