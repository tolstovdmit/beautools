import functools
import logging
import time
import traceback



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


# F = func
# F(args)
# G = gunc -> Callable
# def gunc(func, args, kwargs):
#     return func(args, kwargs) + 1
# G_F = gunc(func)
#
def log_call(level=logging.INFO, logger=logging.getLogger()):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.log(level, f"{func.__name__} Start")
            try:
                res = await func(*args, **kwargs)
                logger.log(level, f"{func.__name__} Finish")
                return res
            except:
                logger.error(f"{func.__name__} Error")
                raise
        
        
        return wrapper
    
    
    return decorator
