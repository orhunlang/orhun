class Counter:
    def __init__(self, start):
        self.value = start
    def increment(self):
        self.value += 1
    def get(self):
        return self.value

c = Counter(0)
i = 0
while i < 1_000_000:
    c.increment()
    i += 1

print(c.get())
