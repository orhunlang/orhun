import json

veri = {"ad": "orhun", "deger": 42, "liste": [1, 2, 3, 4, 5]}
cozulmus = {"deger": 0}
for _ in range(3000):
    metin = json.dumps(veri)
    cozulmus = json.loads(metin)

print(cozulmus["deger"])
