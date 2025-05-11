import asyncio
import datetime
import logging
import traceback



class HotAsyncCycler:
    HOT_TIMES = [
    ]
    
    
    def __init__(self, name, func=None,
                 SUPERVISION_SLEEP=1,
                 HOT_SLEEP=0.2,
                 DEFAULT_SLEEP=1,
                 WAS_WORK_SLEEP=1,
                 ERROR_SLEEP=1 * 60):
        self.name = name
        if func is not None:
            self.run1 = func
        self.SUPERVISION_SLEEP = SUPERVISION_SLEEP
        self.HOT_SLEEP = HOT_SLEEP
        self.DEFAULT_SLEEP = DEFAULT_SLEEP
        self.WAS_WORK_SLEEP = WAS_WORK_SLEEP
        self.ERROR_SLEEP = ERROR_SLEEP
        self._current_sleep = self.DEFAULT_SLEEP
        self._last_awake = datetime.datetime.min
    
    
    async def loop1(self):
        logging.info(f"{self.name}: loop1")
        i = 1
        while True:
            logging.debug("Awaked")
            if self.is_default_sleep_passed():
                logging.info(f"{self.name}: Cycle {i}")
                self._last_awake = datetime.datetime.now()
                WAS_WORK = False
                WAS_ERROR = False
                try:
                    WAS_WORK = await self.run1()
                except Exception as e:
                    logging.error(e)
                    logging.error(traceback.format_exc())
                    WAS_ERROR = True
                finally:
                    self._current_sleep = self.refresh_sleeptime(WAS_WORK, WAS_ERROR)
            
            logging.info(f"{self.name}: Cycle {i} completed. Sleeping for {self._current_sleep} sec")
            await asyncio.sleep(self._current_sleep)
            i += 1
    
    
    def refresh_sleeptime(self, was_work, was_error):
        if was_error:
            return self.ERROR_SLEEP
        
        if self.is_hot_now():
            return self.HOT_SLEEP
        
        if was_work:
            return self.WAS_WORK_SLEEP
        
        return self.DEFAULT_SLEEP
    
    
    def is_default_sleep_passed(self):
        return datetime.datetime.now() >= self._last_awake + datetime.timedelta(seconds=self._current_sleep)
    
    
    @staticmethod
    def is_hot_now():
        now_t = datetime.datetime.now().time()
        for start, end in HotAsyncCycler.HOT_TIMES:
            if start <= now_t <= end:
                return True
        return False
    
    
    async def run1(self):
        return False


async def func():
    return False


async def main():
    hac = HotAsyncCycler("2342342", func=func)
    HotAsyncCycler.HOT_TIMES = [(datetime.time(10, 8), datetime.time(10, 9))]
    await hac.loop1()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(module)s - %(levelname)s\n%(message)s")
    asyncio.run(main())
