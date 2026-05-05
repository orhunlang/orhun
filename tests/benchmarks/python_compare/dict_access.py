d = {}
i = 0
while i < 10000:
    d[str(i)] = i
    i += 1

total = 0
i = 0
while i < 10000:
    if str(i) in d:
        total += d[str(i)]
    i += 1

print(total)
