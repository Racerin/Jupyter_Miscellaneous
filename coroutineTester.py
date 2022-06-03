def decoratorStartCoroutine(func):
    def start(*arg, **kwargs):
        cr = func(*arg, **kwargs)
        #cr.__next__()
        cr.send(None)      #option to prevous line
        return cr
    return start

@decoratorStartCoroutine
def coroutineShout2Pattern(str):
    print("Will print 'yield' when 'str' is found in 'yield'.")
    print("Initiation occured.")
    try:
        while True:
            line = yield
            if str in line:
                print(line, f"\nwith {str} found at index {line.index(str)}.", )
    except GeneratorExit:
        print("Going away. Goodnight")

def coroutinePlay():
    '''About 3 functions are running just for this;
    decorator - decoratorStartCoroutine,
    coroutine - coroutineShout2Pattern, and 
    coroutinePlay
    '''
    x = coroutineShout2Pattern("milk")
    x.send("shipping milk")
    x.send("shipping")
    x.send("sheep milk")

if __name__ = '__main__':
    pass