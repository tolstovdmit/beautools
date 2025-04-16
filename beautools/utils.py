import asyncio



def _Raise_if_len0(lst, err_text):
    if len(lst) == 0:
        raise Exception(err_text)


def RAISE_IF_NONE(var, err_text):
    if var is None:
        raise Exception(err_text)


def get_or_first(d, k=None):
    if k is None:
        return next(iter(d.values()))
    return d.get(k, next(iter(d.values())))


def first_or_none(a):
    return a[0] if len(a) > 0 else None


def map_many(iterable, function, *other):
    if other:
        return map_many(map(function, iterable), *other)
    return map(function, iterable)


def applyer(*funcs):
    def _applyer(x):
        for func in funcs:
            x = func(x)
        return x
    
    
    return _applyer


from collections import defaultdict



def reverse_dict(d):
    reversed_d = defaultdict(list)
    
    for key, value in d.items():
        if isinstance(value, list):
            for v in value:
                reversed_d[v].append(key)
        else:
            reversed_d[value].append(key)
    
    return {k: v[0] if len(v) == 1 else v for k, v in reversed_d.items()}


def merge(D1s: dict, *D2s: dict):
    def merge_two(D1: dict, D2: dict):
        for key, value in D1.items():
            if key in D2:
                if type(value) is dict:
                    merge(D1[key], D2[key])
                else:
                    if type(value) in (int, float, str):
                        D1[key] = [value]
                    if type(D2[key]) is list:
                        D1[key].extend(D2[key])
                    else:
                        D1[key].append(D2[key])
        for key, value in D2.items():
            if key not in D1:
                D1[key] = [value]
    
    
    for D2n in D2s:
        merge_two(D1s, D2n)


async def to_async(func, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)
