Exit code: 0
Wall time: 0.8 seconds
Output:
# Orhun Standard Library

`StdLib/` contains standard library pieces that ship with the Orhun runtime.

- `Sunucu.h` carries the native HTTP server boundary used by built-in modules.
- `orhun/` contains modules written in Orhun itself.

The Orhun-source modules are the first step toward self-hosting. They should use
ordinary `.oh` syntax, avoid privileged native behavior, and stay covered by the
fixture test suite.

Example:

```orhun
temel olsun dahil_et "orhun/temel.oh"
yazdır temel.ilk([1, 2, 3], 0)

sonuc_yardimci olsun dahil_et "orhun/sonuc.oh"
yazdır sonuc_yardimci.deger_yada(sonuc_yardimci.ok(42), 0)
yazdır sonuc_yardimci.dene(işlev(): 7).deger

koleksiyon olsun dahil_et "orhun/koleksiyon.oh"
yazdır koleksiyon.benzersiz([1, 2, 1, 3])

metin_yardimci olsun dahil_et "orhun/metin.oh"
yazdır metin_yardimci.kirp("  Orhun  ")

paket_yardimci olsun dahil_et "orhun/paket.oh"
yazdır paket_yardimci.coz_ve_dogrula("{\"ad\":\"ornek\",\"surum\":\"0.1.0\"}").ok
yazdır paket_yardimci.surum_gecerli_mi("1.2.3-beta.1+build.5")
yazdır paket_yardimci.surum_karsilastir("1.2.3-beta.1", "1.2.3").deger
yazdır paket_yardimci.surum_uyumlu_mu("1.4.0", "^1.2.3").deger
yazdır paket_yardimci.kilit_dosyasini_coz("ornek|yerel|hash|v2").deger[0].ad
yazdır paket_yardimci.bagimlilik_plani([{"ad":"ana","surum":"1.0.0"}]).deger

lexer olsun dahil_et "orhun/lexer.oh"
sonuc olsun lexer.ozetle("yazdır \"Merhaba\"\n")
yazdır sonuc.tokenlar[0].tur
yazdır lexer.degerleri(sonuc.tokenlar)

dil olsun dahil_et "orhun/dil.oh"
tokenlar olsun [dil.token("AD", "merhaba", 1, 1), dil.dosya_sonu(1, 8)]
imlec olsun dil.imlec(tokenlar)
ad olsun dil.bekle(imlec, "AD", "", "ad bekleniyor")
yazdır dil.program([dil.yaprak("Selam", ad.deger.deger, ad.deger)]).tur
yazdır dil.token_degerleri(tokenlar)
yazdır dil.hata_var_mi(imlec)
yazdır dil.tanilari_bicimlendir(imlec)

parser olsun dahil_et "orhun/parser.oh"
parse_sonuc olsun parser.ozetle("yazdır \"Merhaba\"\n")
yazdır parser.hata_var_mi(parse_sonuc)
```

Module lookup checks the requested path first, then searches the standard
library roots. `ORHUN_STDLIB_PATH` can add custom roots. A runtime release also
discovers the sibling `StdLib/` directory beside its `orhun` executable, while
the local `StdLib/` directory remains available during development.

