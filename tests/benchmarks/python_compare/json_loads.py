import json

payload = '{"ad":"orhun","deger":42,"liste":[1,2,3,4,5],"ic":{"x":1,"y":2}}'
toplam = 0
for _ in range(8000):
    obj = json.loads(payload)
    toplam += obj["deger"]

print(toplam)
