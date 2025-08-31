class WorkerException(Exception):
    pass

class WorkerStatusException(Exception):
    def __init__(self, worker_status: int, message: str | None = None):
        self.__worker_status = worker_status
        self.__message = message if message is not None else ''

    def __str__(self):
        return f"Worker failed with status {str(self.__worker_status)}: {self.__message}"