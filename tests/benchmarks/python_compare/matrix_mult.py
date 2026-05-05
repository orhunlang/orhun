def matrix_new(n, d):
    rows = []
    for _ in range(n):
        rows.append([d] * n)
    return rows

def matrix_mul(a, b):
    n = len(a)
    c = matrix_new(n, 0)
    for i in range(n):
        for j in range(n):
            total = 0
            for k in range(n):
                total += a[i][k] * b[k][j]
            c[i][j] = total
    return c

size = 50
a = matrix_new(size, 2)
b = matrix_new(size, 3)
res = matrix_mul(a, b)
print(res[0][0])
