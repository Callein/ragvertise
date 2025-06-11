import logging
import sys


def get_logger(service_name: str = "ragvertise", level: int = logging.INFO) -> logging.Logger:
    """
    서비스 이름별로 구분되는 표준 로거를 반환한다.

    :param service_name: 서비스 이름
    :param level: 로깅 레벨
    :return: 로거 객체
    """
    logger = logging.getLogger(service_name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        f"[{service_name}] [%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # 필요하다면, 파일 핸들러도 추가할 수 있음
    # file_handler = logging.FileHandler(f'logs/{service_name}.log')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    return logger