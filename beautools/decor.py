import asyncio
import functools
import logging
import time
import traceback
from .utils import to_async



def catch_print_swallow_exc(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            traceback.print_exc()
    
    
    return wrapper


def a_catch_print_swallow_exc(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except:
            traceback.print_exc()
    
    
    return wrapper


def log_execution_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        except:
            traceback.print_exc()
        finally:
            end_time = time.perf_counter()
            logging.warning(f"---- {func.__name__} executed in {end_time - start_time:.6f} seconds")
    
    
    return wrapper


def a_log_execution_time(func, level=logging.INFO):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        except:
            traceback.print_exc()
        finally:
            end_time = time.perf_counter()
            logging.log(level, f"---- {func.__name__} executed in {end_time - start_time:.6f} seconds")
    
    
    return wrapper


import threading



# Create a thread-local storage object
thread_local = threading.local()
thread_local.call_indent = 0


# F = func
# F(args)
# G = gunc -> Callable
# def gunc(func, args, kwargs):
#     return func(args, kwargs) + 1
# G_F = gunc(func)
#
def log_call(level=logging.INFO, logger=logging.getLogger()):
    def actual_decorator(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                w = 8
                i = thread_local.call_indent * w
                thread_local.call_indent += 1
                logger.log(level, f"{i * ' '}{func.__name__} Start")
                try:
                    res = await to_async(func, *args, **kwargs)
                    logger.log(level, f"{i * ' '}{func.__name__} Finish")
                    return res
                except:
                    logger.error(f"{i * ' '}{func.__name__} Error")
                    raise
                finally:
                    thread_local.call_indent -= 1
            
            
            return wrapper
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                logger.log(level, f"{func.__name__} Start")
                try:
                    res = func(*args, **kwargs)
                    logger.log(level, f"{func.__name__} Finish")
                    return res
                except:
                    logger.error(f"{func.__name__} Error")
                    raise
            
            
            return wrapper
    
    
    return actual_decorator
