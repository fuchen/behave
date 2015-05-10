# coding=utf-8

from __future__ import absolute_import
from behave.core import BeGeneratorAction, BeAction, BeCondition, BeDecorator, \
                        SUCCESS, FAILURE, RUNNING
import inspect
from functools import wraps

def action(f):
    if inspect.isgeneratorfunction(f):
        return BeGeneratorAction(f)
    else:
        return BeAction(f)


def condition(f):
    return BeCondition(f)


def generator_decorator(f):
    def ctor(bb, node):
        g = f(bb, node)
        def iter_func():
            try:
                return next(g)
            except StopIteration:
                return SUCCESS
        return iter_func
    return ctor

def decorator(f):
    if inspect.isgeneratorfunction(f):
        f = wraps(f)(generator_decorator(f))
    return BeDecorator([f])


# decorators

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


