from behave import SUCCESS, FAILURE, RUNNING, BehaveException, \
                   action, condition


class Counter(object):
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

    def __eq__(self, other):
        if isinstance(other, Counter):
            return self.count == other.count
        return other == self.count

    def __ne__(self, other):
        return not self == other


@action
def act_success():
    return SUCCESS

@action
def act_fail():
    return FAILURE

@action
def act_running():
    return RUNNING

# general
def test_node_can_run_with_arguments():
    count = Counter()

    @action
    def act(a, b, c):
        assert a == 1
        assert b == "b"
        assert c == "named arg"
        count.inc()

    bb = act.blackboard(1, "b", c="named arg")

    assert count == 0
    bb.tick()
    assert count == 1, "act should be called once"

def test_should_raise_if_tick_after_succeeded():
    @action
    def act():
        pass

    bb = act.blackboard()
    assert bb.tick() == SUCCESS
    try:
        bb.tick()
        assert False, "should raise exception"
    except BehaveException:
        pass

def test_should_raise_if_tick_after_failed():
    @action
    def act():
        return FAILURE

    bb = act.blackboard()
    assert bb.tick() == FAILURE
    try:
        bb.tick()
        assert False, "should raise exception"
    except BehaveException:
        pass


# action

def test_action_can_succeed():
    @action
    def act():
        return SUCCESS

    bb = act.blackboard()
    assert bb.tick() == SUCCESS

def test_action_return_none_can_succeed():
    @action
    def act():
        pass

    bb = act.blackboard()
    assert bb.tick() == SUCCESS

def test_action_can_fail():
    @action
    def act():
        return FAILURE

    bb = act.blackboard()
    assert bb.tick() == FAILURE

def test_action_can_be_running():
    @action
    def act():
        return RUNNING

    bb = act.blackboard()
    assert bb.tick() == RUNNING

def test_action_can_be_running_and_then_success():
    state = RUNNING
    @action
    def act():
        return state

    bb = act.blackboard()
    assert bb.tick() == RUNNING
    state = SUCCESS
    assert bb.tick() == SUCCESS

def test_generator_action_can_be_running_then_succeed():
    @action
    def act():
        yield

    bb = act.blackboard()
    assert bb.tick() == RUNNING
    assert bb.tick() == SUCCESS

def test_generator_action_can_be_running_then_fail():
    @action
    def act():
        yield
        yield FAILURE

    bb = act.blackboard()
    assert bb.tick() == RUNNING
    assert bb.tick() == FAILURE

# condition

def test_condition_can_succeed():
    @condition
    def cond():
        return True

    bb = cond.blackboard()
    assert bb.tick() == SUCCESS

def test_condition_can_fail():
    @condition
    def cond():
        return False

    bb = cond.blackboard()
    assert bb.tick() == FAILURE



# sequence

def test_sequence_run_children_in_order():
    count1 = Counter()
    count2 = Counter()

    @action
    def act1():
        assert count2 == 0
        count1.inc()

    @action
    def act2():
        count2.inc()

    seq = act1 >> act2
    bb = seq.blackboard()
    assert bb.tick() == SUCCESS
    assert count1 == 1 and count2 == 1

def test_sequence_fail_immediately_when_child_fail():
    count1 = Counter()
    count2 = Counter()

    @action
    def act1():
        count1.inc()
        return FAILURE

    @action
    def act2():
        count2.inc()

    seq = act1 >> act2
    bb = seq.blackboard()
    assert bb.tick() == FAILURE
    assert count1 == 1 and count2 == 0

def test_sequence_can_succeed():
    seq = act_success >> act_success
    bb = seq.blackboard()
    assert bb.tick() == SUCCESS

def test_sequence_can_fail():
    seq = act_fail >> act_success
    bb = seq.blackboard()
    assert bb.tick() == FAILURE

    seq = act_success >> act_fail
    bb = seq.blackboard()
    assert bb.tick() == FAILURE

def test_sequence_can_be_running_then_succeed():
    state = RUNNING
    @action
    def act():
        return state

    seq = act >> act_success

    bb = seq.blackboard()
    assert bb.tick() == RUNNING
    state = SUCCESS
    assert bb.tick() == SUCCESS

def test_sequence_can_be_running_then_fail():
    state = RUNNING
    @action
    def act():
        return state

    seq = act >> act_success

    bb = seq.blackboard()
    assert bb.tick() == RUNNING
    state = FAILURE
    assert bb.tick() == FAILURE


# selector

def test_selector_run_children_in_order():
    count1 = Counter()
    count2 = Counter()

    @action
    def act1():
        assert count2 == 0
        count1.inc()
        return FAILURE

    @action
    def act2():
        count2.inc()
        return FAILURE

    sel = act1 | act2
    bb = sel.blackboard()
    assert bb.tick() == FAILURE
    assert count1 == 1 and count2 == 1

def test_selector_succeed_immediately_when_child_succeed():
    count1 = Counter()
    count2 = Counter()

    @action
    def act1():
        count1.inc()
        return SUCCESS

    @action
    def act2():
        count2.inc()

    sel = act1 | act2
    bb = sel.blackboard()
    assert bb.tick() == SUCCESS
    assert count1 == 1 and count2 == 0

def test_selector_can_succeed():
    seq = act_success | act_success
    bb = seq.blackboard()
    assert bb.tick() == SUCCESS

    seq = act_success | act_fail
    bb = seq.blackboard()
    assert bb.tick() == SUCCESS

def test_selector_can_fail():
    sel = act_fail | act_fail
    bb = sel.blackboard()
    assert bb.tick() == FAILURE

def test_selector_can_be_running_then_succeed():
    state = RUNNING
    @action
    def act():
        return state

    sel = act | act_fail

    bb = sel.blackboard()
    assert bb.tick() == RUNNING
    state = SUCCESS
    assert bb.tick() == SUCCESS

def test_selector_can_be_running_then_fail():
    state = RUNNING
    @action
    def act():
        return state

    sel = act | act_fail

    bb = sel.blackboard()
    assert bb.tick() == RUNNING
    state = FAILURE
    assert bb.tick() == FAILURE

