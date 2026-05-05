import math


def nbody_run(step_count: int, dt: float) -> float:
    x = [0.0, 1.0, -1.0]
    y = [0.0, 0.5, -0.5]
    z = [0.0, -0.25, 0.25]
    vx = [0.0, 0.1, -0.1]
    vy = [0.0, -0.05, 0.05]
    vz = [0.0, 0.02, -0.02]
    m = [1.0, 0.8, 1.2]

    for _ in range(step_count):
        for i in range(3):
            for j in range(i + 1, 3):
                dx = x[j] - x[i]
                dy = y[j] - y[i]
                dz = z[j] - z[i]
                dist2 = dx * dx + dy * dy + dz * dz + 0.01
                inv = 1.0 / math.sqrt(dist2)
                inv3 = inv * inv * inv

                fx = dx * inv3
                fy = dy * inv3
                fz = dz * inv3

                vx[i] += fx * dt * m[j]
                vy[i] += fy * dt * m[j]
                vz[i] += fz * dt * m[j]

                vx[j] -= fx * dt * m[i]
                vy[j] -= fy * dt * m[i]
                vz[j] -= fz * dt * m[i]

        for i in range(3):
            x[i] += vx[i] * dt
            y[i] += vy[i] * dt
            z[i] += vz[i] * dt

    sig = 0.0
    for i in range(3):
        sig += x[i] * 1.7 + y[i] * 2.3 + z[i] * 2.9
        sig += vx[i] * 0.7 + vy[i] * 1.1 + vz[i] * 1.3

    return sig * 1_000_000.0


print(nbody_run(300, 0.01))
