def fib_iter(n):
    a = 0
    b = 1
    i = 0
    while i < n:
        temp = a
        a = b
        b = temp + b
        i += 1
    return a

total = 0
for _ in range(50_000):
    total += fib_iter(70)

print(total)
