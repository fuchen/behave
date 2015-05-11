# behave: A behavior tree implementation in Python

With `behave`, you can define a behavior tree like this:

````
tree = (
    is_greater_than_10 >> wow_large_number
    | is_between_0_and_10 >> count_from_1
    | failer * repeat(3) * doomed
)

bb = tree.blackboard(10)
while bb.tick() == RUNNING:
    pass

````


### Import from behave:

````
from behave import condition, action, FAILURE
````

### Define condition nodes

Conditions are defined by functions return a `bool` value. The function can take any number of arguments.

````
@condition
def is_greater_than_10(x):
    return x > 10

@condition
def is_between_0_and_10(x):
    return 0 < x < 10

````

### Define action nodes

Action functions can return `SUCCESS`, `FAILURE`, `RUNNING` states. Return `None` will be treated as `SUCCESS`.

````
@action
def wow_large_number(x):
    print "WOW, %d is a large number!" % x

@action
def doomed(x):
    print "%d is doomed" % x
    return FAILURE
````

And you can define an action with a generator function:

* `yield FAILURE` fails the actions. 
* `yield` or `yield None` puts the action into `RUNNING` state.
* If the generator returns(stop iteration), action state will be set to `SUCCESS`

```
@action
def count_from_1(x):
    for i in range(1, x):
        print "count", i
        yield
    print "count", x

````

### Define a sequence

````
seq = is_greater_than_10 >> wow_large_number
````

### Define a selector

````
sel = is_greater_than_10 | is_between_0_and_10
````

### Decorate nodes

````
from behave import repeat, forever, succeeder

decorated_1 = forever(count_from_1)
decorated_2 = succeeder(doomed)
decorated_3 = repeat(10)(count_from_1)
````

For readability reason, you can also use chaining style:

````
from behave import repeat, forever, succeeder, failer

composite_decorator = repeat(3) * repeat(2)   # It's identical to repeat(6)

decorated_1 = forever * count_from_1
decorated_2 = succeeder * doomed
decorated_3 = repeat(10) * count_from_1
decorated_4 = failer * repeat(10) * count_from_1
````

### Put everything together

````
tree = (
    is_greater_than_10 >> wow_large_number
    | is_between_0_and_10 >> count_from_1
    | failer * repeat(3) * doomed
)
````

Every node is a tree itself. And a big tree is composed by many sub trees. To iterate the tree:

````
bb = tree.blackboard(5) # Creates an run instance

# Now let the tree do its job, till job is done
state = bb.tick()
print "state = %s\n" % state
while state == RUNNING:
    state = bb.tick()
    print "state = %s\n" % state
assert state == SUCCESS or state == FAILURE
````

Output:

````
count 1
state = Running

count 2
state = Running

count 3
state = Running

count 4
state = Running

count 5
state = Success
````

## Wait, did I mention debugger?

To debug the tree, you need to:

* Define a debugger function
* Create blackboard by calling `tree.debug(debugger, arg1, arg2...)` instead of `tree.blackboard(arg1, arg2...)`.

````
def my_debugger(node, state):
    print "[%s] -> %s" % (node.name, state)

bb = tree.debug(my_debugger, 5) # Creates an blackboard with debugger enabled

# Now let the tree do its job, till job is done
state = bb.tick()
print "state = %s\n" % state
while state == RUNNING:
    state = bb.tick()
    print "state = %s\n" % state
assert state == SUCCESS or state == FAILURE
````

Output:

````
[ is_greater_than_10 ] -> Failure
[ BeSeqence ] -> Failure
[ is_between_0_and_10 ] -> Success
count 1
[ count_from_1 ] -> Running
[ BeSeqence ] -> Running
[ BeSelect ] -> Running
state = Running

count 2
[ count_from_1 ] -> Running
[ BeSeqence ] -> Running
[ BeSelect ] -> Running
state = Running

count 3
[ count_from_1 ] -> Running
[ BeSeqence ] -> Running
[ BeSelect ] -> Running
state = Running

count 4
[ count_from_1 ] -> Running
[ BeSeqence ] -> Running
[ BeSelect ] -> Running
state = Running

count 5
[ count_from_1 ] -> Success
[ BeSeqence ] -> Success
[ BeSelect ] -> Success
state = Success

````

Too messy? Let put some comments into the tree:

````
tree = (
    (is_greater_than_10 >> wow_large_number) // "if x > 10, wow"
    | (is_between_0_and_10 >> count_from_1) // "if 0 < x < 10, count from 1"
    | failer * repeat(3) * doomed // "if x <= 0, doomed X 3, and then fail"
)
````

And make a little change to `my_debugger`:

````
def my_debugger(node, state):
    if node.desc:
        print "[%s] -> %s" % (node.desc, state)
````

Try it again:

````
[ if x > 10, wow ] -> Failure
count 1
[ if 0 < x < 10, count from 1 ] -> Running
state = Running

count 2
[ if 0 < x < 10, count from 1 ] -> Running
state = Running

count 3
[ if 0 < x < 10, count from 1 ] -> Running
state = Running

count 4
[ if 0 < x < 10, count from 1 ] -> Running
state = Running

count 5
[ if 0 < x < 10, count from 1 ] -> Success
state = Success
````

## Run Tests with [nose](https://nose.readthedocs.org/en/latest/)

````
nosetests test
````
