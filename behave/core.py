# coding=utf-8

SUCCESS = "Success"
FAILURE = "Failure"
RUNNING = "Running"


class BehaveException(Exception):
    pass


class BeNode(object):
    def __init__(self):
        self.desc = None

    def __call__(self, *args, **kwargs):
        return self.call_worker(None, *args, **kwargs)

    def call_worker(self, debugger, *args, **kwargs):
        blackboard = self.new_iterator(debugger, *args, **kwargs)
        def bb_next():
            if bb_next.finished:
                raise BehaveException("Calling a finished action!")

            x = next(blackboard)
            if x != RUNNING:
                bb_next.finished = True
            return x

        bb_next.finished = False
        return bb_next

    debug = call_worker

    def new_iterator(self, debugger, *args, **kwargs):
        assert False
        yield SUCCESS

    def __or__(self, sibling):
        sel = BeSelect()
        return sel | self | sibling

    def __rshift__(self, sibling):
        seq = BeSeqence()
        return seq >> self >> sibling

    def __floordiv__(self, desc):
        self.desc = desc
        return self


class BeAction(BeNode):
    def __init__(self, func):
        super(BeAction, self).__init__()
        self.func = func

    def new_iterator(self, debugger, *args, **kwargs):
        while True:
            x = self.func(*args, **kwargs)
            if x != RUNNING:
                break
            if debugger:
                debugger(self, x)
            yield x

        if x is None or x == SUCCESS:
            if debugger:
                debugger(self, SUCCESS)
            yield SUCCESS

        assert x == FAILURE
        if debugger:
            debugger(self, x)
        yield x


class BeGeneratorAction(BeNode):
    def __init__(self, generatorfunc):
        super(BeGeneratorAction, self).__init__()
        self.generatorfunc = generatorfunc

    def new_iterator(self, debugger, *args, **kwargs):
        for x in self.generatorfunc(*args, **kwargs):
            if x is None or x == RUNNING:
                if debugger:
                    debugger(self, RUNNING)
                yield RUNNING
            else:
                assert x == FAILURE or x == SUCCESS
                if debugger:
                    debugger(self, x)
                yield x
                return

        if debugger:
            debugger(self, SUCCESS)
        yield SUCCESS

class BeCondition(BeNode):
    def __init__(self, func):
        super(BeCondition, self).__init__()
        self.func = func

    def new_iterator(self, debugger, *args, **kwargs):
        x = SUCCESS if self.func(*args, **kwargs) else FAILURE
        if debugger:
            debugger(self, x)
        yield x


class BeComposite(BeNode):
    def __init__(self):
        super(BeComposite, self).__init__()
        self.children = []


class BeSelect(BeComposite):
    def new_iterator(self, debugger, *args, **kwargs):
        for c in self.children:
            for x in c.new_iterator(debugger, *args, **kwargs):
                if x == RUNNING:
                    if debugger:
                        debugger(self, x)
                    yield x
                    continue
                if x == SUCCESS:
                    if debugger:
                        debugger(self, x)
                    yield x
                    return
                assert x == FAILURE
                break

        # All children are failed
        if debugger:
            debugger(self, FAILURE)
        yield FAILURE

    def __or__(self, child):
        self.children.append(child)
        return self


class BeSeqence(BeComposite):
    def new_iterator(self, debugger, *args, **kwargs):
        for c in self.children:
            for x in c.new_iterator(debugger, *args, **kwargs):
                if x == RUNNING:
                    if debugger:
                        debugger(self, x)
                    yield x
                    continue
                if x == FAILURE:
                    if debugger:
                        debugger(self, x)
                    yield x
                    return
                assert x == SUCCESS
                break

        # all children are succeeded
        if debugger:
            debugger(self, SUCCESS)
        yield SUCCESS

    def __rshift__(self, child):
        self.children.append(child)
        return self


class BeDecorator(object):
    def __init__(self, decorator):
        self.decorator = decorator

    def __call__(self, node):
        assert isinstance(node, BeNode)
        return BeDecorated(self.decorator, node)

    def __pow__(self, node):
        return self(node)


class BeDecorated(BeNode):
    def __init__(self, decorator, node):
        super(BeDecorated, self).__init__()
        self.decorator = decorator
        self.node = node

    def new_iterator(self, debugger, *args, **kwargs):
        def node_wrapper(*a, **kw):
            return self.node.call_worker(debugger, *a, **kw)

        for x in self.decorator(node_wrapper, *args, **kwargs):
            if x == RUNNING:
                if debugger:
                    debugger(self, x)
                yield x
                continue
            assert x == FAILURE or x == SUCCESS
            if debugger:
                debugger(self, x)
            yield x
            return

        if debugger:
            debugger(self, SUCCESS)
        yield SUCCESS
