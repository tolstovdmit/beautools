"""
print(mapl(lambda x: x + 1, [1, 2, 3]))
print(mapc(set, lambda x: x + 1, [1, 2, 3]))
"""


def mapl(f, it):
    return list(map(f, it))


def filterl(f, it):
    return list(filter(f, it))


def mapc(collect, f, it):
    return collect(map(f, it))


def filterc(collect, f, it):
    return collect(filter(f, it))
