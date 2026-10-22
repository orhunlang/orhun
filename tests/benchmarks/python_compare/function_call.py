def increment(value: int) -> int:
    return value + 1


total = 0
i = 0
while i < 500_000:
    total += increment(i)
    i += 1

print(total)
