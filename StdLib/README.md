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
yazdır paket_yardimci.en_uygun_bagimlilik({"ad":"ag","kural":"^1.0.0"}, [{"ad":"ag","surum":"1.2.0"}]).deger.surum
adaylar olsun [{"ad":"ag","surum":"1.1.0"}, {"ad":"ag","surum":"2.0.0"}]
yazdır paket_yardimci.bagimlilik_aday_surimleri({"ad":"ag","kural":"^1.0.0"}, adaylar)
yazdır paket_yardimci.dogrula({"ad":"ana","surum":"1.0.0","bagimliliklar":["ag"],"bagimlilik_istekleri":[{"ad":"ag","kural":"^1.0.0"}]}).ok
yazdır paket_yardimci.dogrula({"ad":"ana","surum":"1.0.0","bagimliliklar":["ag","ag"]}).ok
yazdır paket_yardimci.kilit_dosyasini_coz("ag|yerel|hash|v2\nag|yerel|hash|v2").ok
kilitler olsun paket_yardimci.kilit_dosyasini_coz("ag|yerel|hash|v2").deger
yazdır paket_yardimci.manifest_kilit_bagimliliklarini_dogrula({"ad":"ana","surum":"1.0.0","bagimliliklar":["ag"]}, kilitler).ok
yazdır paket_yardimci.manifest_bagimliliklarini_sec({"ad":"ana","surum":"1.0.0","bagimliliklar":["ag"]}, [{"ad":"ag","surum":"1.2.0"}]).deger[0].surum

lexer olsun dahil_et "orhun/lexer.oh"
sonuc olsun lexer.ozetle("yazdır \"Merhaba\"\n")
yazdır sonuc.tokenlar[0].tur
yazdır lexer.degerleri(sonuc.tokenlar)
yazdır lexer.token_araligi(sonuc.tokenlar[1]).uzunluk

dil olsun dahil_et "orhun/dil.oh"
tokenlar olsun [dil.token("AD", "merhaba", 1, 1), dil.dosya_sonu(1, 8)]
imlec olsun dil.imlec(tokenlar)
ad olsun dil.bekle(imlec, "AD", "", "ad bekleniyor")
yazdır dil.program([dil.yaprak("Selam", ad.deger.deger, ad.deger)]).tur
agac olsun dil.program([dil.dugum("Selam", ad.deger.deger, [], 1, 1)])
yazdır dil.dugum_turlerini_duzlestir(agac)
yazdır dil.dugum_turu_var_mi(agac, "Selam")
yazdır dil.dugum_ozeti(agac)
yazdır dil.token_degerleri(tokenlar)
yazdır dil.hata_var_mi(imlec)
yazdır dil.tanilari_bicimlendir(imlec)
yazdır dil.tani_listesi_bicimlendir(imlec.hatalar)
yazdır dil.tani_listesi_ozeti(imlec.hatalar)
yazdır dil.tani_kaynak_bicimlendir(dil.tani("ornek", "mesaj", 1, 2), "ab")
aralikli olsun dil.tani_araligi("ornek", "gecersiz bolum", 1, 2, 2)
yazdır dil.tani_kaynak_bicimlendir(aralikli, "abc")
kimlik_tanisi olsun dil.token_tanisi("tanimsiz_ad", "ad tanimli degil", dil.token("AD", "deger", 1, 1))
yazdır dil.tani_bicimlendir(kimlik_tanisi)

parser olsun dahil_et "orhun/parser.oh"
parse_sonuc olsun parser.ozetle("yazdır \"Merhaba\"\n")
yazdır parser.hata_var_mi(parse_sonuc)
yazdır parser.komut_satir_araligi(parse_sonuc.komutlar[0]).satir_sayisi
yazdır parser.ifade_satir_araligi(parse_sonuc.komutlar[0].ifade_ozeti).satir_sayisi
yazdır uzunluk(parser.tum_ifade_satir_araliklari(parse_sonuc))
yazdır parser.ifade_agaci_ozeti(parse_sonuc)
yazdır uzunluk(parser.tum_komut_satir_araliklari(parse_sonuc))
yazdır parser.komut_agaci_ozeti(parse_sonuc)
yazdır parser.ir_dogrula(parse_sonuc)
yazdır parser.ir_ozeti(parse_sonuc)
yazdır json.yaz(parser.hata_tanilari(parse_sonuc))
```

Module lookup checks the requested path first, then searches the standard
library roots. `ORHUN_STDLIB_PATH` can add custom roots. A runtime release also
discovers the sibling `StdLib/` directory beside its `orhun` executable, while
the local `StdLib/` directory remains available during development.
