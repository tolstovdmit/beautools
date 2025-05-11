import asyncio
import logging
import time
import traceback



class Cycler:
    def __init__(self, name, async_cycled_func=None, DEFAULT_SLEEP=1, WAS_WORK_SLEEP=1, ERROR_SLEEP=1 * 60):
        self.name = name
        if async_cycled_func is not None:
            self.async_cycled_func = async_cycled_func
        self.DEFAULT_SLEEP = DEFAULT_SLEEP
        self.WAS_WORK_SLEEP = WAS_WORK_SLEEP
        self.ERROR_SLEEP = ERROR_SLEEP
    
    
    def run(self):
        
        i = 1
        while True:
            logging.info(f"{self.name}: Cycle {i}")
            wasWork = False
            sleep_time = self.DEFAULT_SLEEP
            try:
                wasWork = self.cycled_func()
                if wasWork:
                    sleep_time = self.WAS_WORK_SLEEP
            except Exception as e:
                logging.error(e)
                logging.error(traceback.format_exc())
                sleep_time = self.ERROR_SLEEP
            
            logging.info(f"{self.name}: Cycle {i} completed. Sleeping for {sleep_time} sec")
            time.sleep(sleep_time)
            i += 1
    
    
    def cycled_func(self):
        return False


class AsyncCycler:
    def __init__(self, name, async_cycled_func=None, DEFAULT_SLEEP=1, WAS_WORK_SLEEP=1, ERROR_SLEEP=1 * 60):
        self.name = name
        if async_cycled_func is not None:
            self.async_cycled_func = async_cycled_func
        self.DEFAULT_SLEEP = DEFAULT_SLEEP
        self.WAS_WORK_SLEEP = WAS_WORK_SLEEP
        self.ERROR_SLEEP = ERROR_SLEEP
    
    
    async def run(self):
        
        i = 1
        while True:
            logging.info(f"{self.name}: Cycle {i}")
            wasWork = False
            sleep_time = self.DEFAULT_SLEEP
            try:
                wasWork = await self.async_cycled_func()
                if wasWork:
                    sleep_time = self.WAS_WORK_SLEEP
            except Exception as e:
                logging.error(e)
                logging.error(traceback.format_exc())
                sleep_time = self.ERROR_SLEEP
            
            logging.info(f"{self.name}: Cycle {i} completed. Sleeping for {sleep_time} sec")
            await asyncio.sleep(sleep_time)
            i += 1
    
    
    async def async_cycled_func(self):
        return False
