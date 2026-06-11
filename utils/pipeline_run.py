import logging
import time
import os


class PipelineRun:
    def __init__(self, pipeline_name: str) -> None:
        self.pipeline_name = pipeline_name
        self.start_time = None

    def __enter__(self):
        # TODO: log pipeline started, record start time
        logging.info(f"Pipeline {self.pipeline_name} started")
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: calculate duration, log complete or failed
        time_taken = time.time() - self.start_time
        if hasattr(self, "temp_filepath") and self.temp_filepath:
            os.remove(self.temp_filepath)
            logging.info(f"Cleaned up temp file: {self.temp_filepath}")
        if exc_type is not None:
            logging.error(
                f"Pipeline failed: {self.pipeline_name} — {exc_type.__name__} — {time_taken:.2f}s")
        else:
            logging.info(
                f"Pipeline complete: {self.pipeline_name} — {time_taken:.2f}s")

        return False   
        