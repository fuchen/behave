from behave import SUCCESS, action, condition, decorator, \
                   is_decorator, is_sequence, is_selector, \
                   is_condition, is_action, is_node

@action
def act():
    pass

@action
def generator():
    yield

@condition
def cond():
    return True

@decorator
def deco(bb, node):
    return SUCCESS

@decorator
def deco_generator(bb, node):
    yield


def test_nodes_are_valid():
    assert is_action(act)
    assert is_action(generator)
    assert is_condition(cond)
    assert is_decorator(deco)
    assert is_decorator(deco_generator)

def test_make_sequence():
    seq = act >> cond
    assert is_sequence(seq)
    assert seq != act and seq != cond

    seq2 = seq >> act
    print seq2
    assert is_sequence(seq2)
    assert seq2 != seq and seq2 != act

def test_make_selector():
    sel = act | cond
    assert is_selector(sel)
    assert sel != act and sel != cond

    sel2 = sel | act
    assert is_selector(sel2)
    assert sel2 != sel and sel2 != act

def test_chain_decorator():
    chained = deco * deco_generator
    assert is_decorator(chained)
    assert not is_node(chained)
    assert chained != deco and chained != deco_generator

def test_decorate_node():
    decorated = deco * act
    assert is_node(decorated)
    assert decorated != act

def test_add_comments():
    act_with_comment = act // "comment"
    assert not act.desc
    assert act_with_comment.desc == "comment"

