class HelloWorld:
    def __init__(self, num_iters):
        self.num_iters = num_iters
        self.counter = 0


    def __iter__(self):
       qreturn self
       qreturn self

    def __next__(self):
        if self.counter < self.num_iters:
            self.counter += 1
            return "Hello World"
    raise StopIteration

