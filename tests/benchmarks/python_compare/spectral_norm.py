import math


def A(i: int, j: int) -> float:
    s = i + j
    return 1.0 / ((s * (s + 1)) / 2 + i + 1)


def mul_A(v: list[float]) -> list[float]:
    n = len(v)
    out = [0.0] * n
    for i in range(n):
        total = 0.0
        for j in range(n):
            total += A(i, j) * v[j]
        out[i] = total
    return out


def mul_At(v: list[float]) -> list[float]:
    n = len(v)
    out = [0.0] * n
    for i in range(n):
        total = 0.0
        for j in range(n):
            total += A(j, i) * v[j]
        out[i] = total
    return out


def mul_AtA(v: list[float]) -> list[float]:
    return mul_At(mul_A(v))


def spectral_norm(n: int) -> float:
    u = [1.0] * n
    for _ in range(10):
        v = mul_AtA(u)
        u = mul_AtA(v)

    vbv = 0.0
    vv = 0.0
    for i in range(n):
        vbv += u[i] * v[i]
        vv += v[i] * v[i]

    sigma = math.sqrt(vbv / vv)
    return sigma * 1_000_000.0


print(spectral_norm(55))
