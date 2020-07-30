from watchdog.events import RegexMatchingEventHandler


class LoggedRegexMatchingEventHandler(RegexMatchingEventHandler): 
    def __init__(self, logger, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.logger = logger

    def on_created(self, event): 
        super().on_created(event)
        self.logger.info("CSV file created - % s" % event.src_path) 


    def on_modified(self, event): 
        super().on_created(event)
        self.logger.info("CSV file modified - % s" % event.src_path) 