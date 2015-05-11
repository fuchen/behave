# coding=utf-8

from .core import SUCCESS, FAILURE, RUNNING
from .helper import decorator


@decorator
def forever(bb, node):
    while True:
        func = bb.new_iterator(node)
        while func() == RUNNING:
            yield RUNNING


def repeat(count):
    @decorator
    def repeat_worker(bb, node):
        for _ in range(count):
            func = bb.new_iterator(node)
            while func() == RUNNING:
                yield RUNNING

    return repeat_worker


@decorator
def succeeder(bb, node):
    func = bb.new_iterator(node)
    while func() == RUNNING:
        yield RUNNING
    yield SUCCESS


@decorator
def failer(bb, node):
    func = bb.new_iterator(node)
    while func() == RUNNING:
        yield RUNNING
    yield FAILURE


@decorator
def not_(bb, node):
    func = bb.new_iterator(node)
    x = func()
    while x == RUNNING:
        yield x
        x = func()
    yield FAILURE if x == SUCCESS else SUCCESS


