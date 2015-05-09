# coding=utf-8

from __future__ import absolute_import, print_function
from behave.core import BeGeneratorAction, BeAction, BeCondition, BeDecorator, \
                        SUCCESS, FAILURE, RUNNING
import inspect


def action(f):
    if inspect.isgeneratorfunction(f):
        return BeGeneratorAction(f)
    else:
        return BeAction(f)


def condition(f):
    return BeCondition(f)


def decorator(f):
    return BeDecorator(f)


# decorators

@decorator
def forever(node, *args, **kwargs):
    while True:
        blackboard = node(*args, **kwargs)
        x = blackboard()
        while x == RUNNING:
            yield x
            x = blackboard()


def repeat(count):
    @decorator
    def repeat_worker(node, *args, **kwargs):
        for _ in range(count):
            blackboard = node(*args, **kwargs)
            x = blackboard()
            while x == RUNNING:
                yield x
                x = blackboard()

    return repeat_worker

@decorator
def succeeder(node, *args, **kwargs):
    blackboard = node(*args, **kwargs)
    x = blackboard()
    while x == RUNNING:
        yield x
        x = blackboard()
    yield SUCCESS


@decorator
def failer(node, *args, **kwargs):
    blackboard = node(*args, **kwargs)
    x = blackboard()
    while x == RUNNING:
        yield x
        x = blackboard()
    yield FAILURE


@decorator
def not_(node, *args, **kwargs):
    blackboard = node(*args, **kwargs)
    x = blackboard()
    while x == RUNNING:
        yield x
        x = blackboard()

    yield FAILURE if x == SUCCESS else SUCCESS

