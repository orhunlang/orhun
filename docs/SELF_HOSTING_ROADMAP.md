# Orhun Self-Hosting Roadmap

Orhun'un uzun vadeli hedefi, C++ ile baslayan derleyici/runtime cekirdegini
asama asama Orhun kaynaklariyla ifade edilebilir hale getirmektir.

Bu hedef "hicbir teknolojiye fiziksel olarak dokunmamak" anlamina gelmez.
Her dil en altta isletim sistemi, donanim ABI'si ve bir ilk derleme zinciriyle
baslar. Orhun icin asil bagimsizlik hedefi sudur:

- Orhun programlari calismak icin Python, JavaScript ya da baska bir dil runtime'i
  gerektirmeyecek.
- Orhun derleyicisinin buyuyen bolumu Orhun ile yazilacak.
- C++ cekirdek zamanla bootstrap katmanina cekilecek.
- Son kullanici icin tek arac `orhun` olacak.

## Faz 0: C++ Cekirdegi Saglamlastirma

Durum: aktif; ana Windows ve POSIX test kosuculari her vaka icin timeout
uygular. Coverage kosuculari enstrumante binary'yi yeniden derlemeden ayni
vaka paketini calistirir; coverage kapisi varsayilan VM/derleyici cekirdegini
izler. Interpreter ve VM artik `bos`, mantik ve sayi turlerini ayri tasir;
esitlik, JSON, kati indeks ve donussuz islev semantigi ortak fixture'larda
eslenir. Global dongu govdelerindeki `olsun` baglari VM ile ayni global ortami
guncellerken, islev-ici iterasyon closure hucreleri taze kalir. Tam interpreter
parity sweep'i 153 korumali runtime ciktisinin tamamini hizli butcede birebir
eslestirir; development ve optimize release yapilarinda bilinen fark kalmamistir.
Duz islev cagrilari lexical golgeleme kontrolunu istisna olusturmadan yapar;
aday onerileri yalniz gercek eksik-ad hatalarinda hesaplanir. VM ve yorumlayici
ayni UTF-8 yakinlik hesabini ve yalniz erisilebilir adlari kullanir. Ayni tam
parite kapisi Windows, Linux ve macOS CI'da calisir.

`gorev` ilkelleri ve `paralel yap` planlari hem yorumlayici hem VM yolunda ayni
sozlesmeyle calisir. Coklu atama, hedef sayisini liste boyutuyla hicbir hedefi
yazmadan once esleyen operandli bytecode dogrulamasini iki derleyici yolunda da
uretir.

Hedefler:

- VM varsayilan yol olarak guvenilir kalacak.
- Interpreter fallback stable kanalda kapali kalacak.
- Test runner her vaka icin timeout uygulayacak.
- `ust`, varsayilan arguman, miras, hata modeli ve paket guvenligi gibi
  semantik noktalar kilitlenecek.
- Dil davranisi dokumanla sabitlenecek: soz dizimi, bytecode semantigi,
  standart kutuphane sozlesmesi.

Basari olcutu:

- Full test paketi takilmadan biter.
- `orhun doctor --json` stable kanalda makine-okur saglik raporu verir.
- Yeni ozellikler icin once test, sonra uygulama akisi korunur.

## Faz 1: Orhun Ile Standart Kutuphane

Durum: aktif; interpreter ve VM, Orhun-kaynakli modullerin global degerlerini
ve kardes islevlerini cagiran programdaki ayni adlardan ayirir. Modul-global
atamalar paylasilan modul nesnesinde kalir ve cagiran globaline sizmaz. Saf
Orhun `sonuc.oh` 0.2.0, `metin.oh` 0.4.0 ve `koleksiyon.oh` 0.6.0; sonuc
zincirleme, konum/doldurma ve secme/parcalama/duzlestirme yardimcilarini sistem
primitive'i olmadan sunar. `sozluk.oh` 0.1.0 da guvenli okuma, birlestirme,
secme ve callback tabanli donusturme islemlerini saf Orhun katmanina tasir.

Hedefler:

- Saf Orhun ile yazilmis `StdLib/orhun/` modulleri baslar.
- `sonuc`, metin yardimcilari, koleksiyon yardimcilari, paket manifest okuma
  ve surum karsilastirma, dil gelistirme yardimcilari gibi guvenli alanlar
  Orhun koduna tasinir.
- Orhun paket yardimcisi lock v1/v2/v3 satirlarini yapisal olarak cozer;
  SHA-256 ve dosya butunlugu denetimi sistem sinirinda kalirken gelecekteki
  Orhun kaynakli cozumleyici guvenli paket yolu kararlarini kendi verir.
  Tekrar eden paket adli lock kayitlari iki katmanda da reddedilir.
- Saf Orhun manifest/lock tutarlilik denetimi, her dogrudan bagimliligin
  benzersiz ve yapisal olarak gecerli bir lock kaydiyla sabitlenmesini ister.
  Sistem sinirindaki `paket dogrula` komutu da `orhun.yap` dogrudan
  bagimliliklarini ayni lock kapsamiyla karsilastirir.
- Paket bagimlilik grafi planlamasi saf Orhun kodunda eksik, tekrarli ve
  dongusel manifestleri reddederek bagimlilik-oncelikli karar verir.
- Surumlu bagimlilik istekleri saf Orhun kodunda en yuksek uyumlu adayla
  eslenir ve manifestteki dogrudan bagimliliklar ile tutarliligi denetlenir;
  manifest secimi acik kurali olmayan bagimliliklari da `*` ile kapsar;
  indirme ve dosya degisimi sistem sinirinda kalir. Cozumleme hatalari eksik
  paket adi ile uyumsuz bulunan surumleri de ayri ayri aciklar.
- C++ yerlesikleri sadece sistem siniri, dosya, FFI, ag ve VM primitive'leri
  gibi zorunlu noktalarda kalir.

Basari olcutu:

- Orhun kaynakli stdlib modulleri test paketinde C++ yerlesikleriyle birlikte
  calisir.
- Paket yoneticisi Orhun modullerini cozebilir.

## Faz 2: Orhun Ile Lexer ve Parser

Durum: aktif; lexer prototipi `orhun/lexer.oh` 0.8.0 ile `hata_sayisi`,
`token_sayisi`, `tokenlar`, token degeri, hata degeri ve UTF-8-aware token
araligi ozetlerini sagliyor. Lexer parity
7 basarili fixture, 3 hata fixture ve genis `tests/cases` token sweep
seviyesine tasindi; non-ASCII fixture'larda UTF-8 kod noktasi tabanli satir/sutun
parity saglandi. `her` anahtar kelimesi de Orhun kaynakli lexer sozlesmesine
eklendi. Basarili ve hatali lexer ozetleri `orhun-lexer-ir-v1` kimligini tasir;
token alanlari, konumlari, sayaclari ve son `DOSYA_SONU` kaydi saf Orhun
yardimcisiyla dogrulanabilir. Parser prototipi 175 basarili AST
fixture ve 63 hata fixture seviyesine tasindi.
`orhun-lex` ve `orhun-parse`, Orhun-yazili on ucu surumlu ve dogrulanmis JSON
olarak dogrudan CLI'dan calistirir; kaynak hatalarini yapisal IR'i bozmadan
cikis kodu 1 ile bildirir ve source/OBC modul politikalarini destekler.
`orhun/dil.oh` 0.11.0 token, imlec, tani ve AST dugumu yardimcilari saglayarak
Orhun ile yeni dil/DSL prototipleri yazmak icin ortak bir on-katman baslatti.
Imlec isaretleri secimli parse denemelerinin konum ve tanilarini geri alir;
token kumesi esleme ve acik senkronizasyon turlerine ilerleme ortak hata
kurtarma akislarini saf Orhun kodunda sunar.
Tani kayitlari ortak kod/konum bicimleyicileriyle yeni baslayanlara acik
mesajlar olarak sunulabilir; kaynak satiri ve sutun isareti de eklenebilir.
Aralik tani isaretleri, hata/uyari seviyesi ve Turkce ipuclari da bu ortak
sozlesmede bulunur. Imlecten bagimsiz tani listeleri de ayni bicimleyicilerle
sunulabilir; hata/uyari seviyesine gore sayilabilir, filtrelenebilir ve
ozetlenebilir. Token tabanli tanilar, UTF-8 kod noktasi uzunlugunu da otomatik
kullanir. AST dugumleri on-sirali duz listeye cevrilebilir, tur listeleri
toplanabilir, belirli dugum turleri filtrelenebilir ve agac derinligi/tur
sayilari ozetlenebilir.
Recursive block summary parity ve recursive expression child parity basladi.
`orhun/parser.oh` 0.28.0, lexer ozetini `orhun-lexer-ir-v1` sinirinda
dogruladiktan sonra token akisini tuketir; `Program` ve `Block` yapisal IR turlerini, parse sonuc
hata/token/komut sayisini ve komut turlerini, ifade satirlarini
ve alt ifade sayilarini, atama `bildirim` ve hedef
ozetlerini, coklu atama hedeflerini ve hedef sayisini, islev basligi parametre/varsayilan
sayilarini ve varsayilan arguman ozetlerini, islev/sinif/dis
islev/dahil_et/deneme-yakala baslik metadatasini, dis islev tip sayisini,
eger/surece kosul
ozetlerini, sinif ebeveyn varligini, blok sayisini, blok satirlarini ve blok
komut sayilarini, tekrarla sayi ozetlerini, `her ... icinde ...` degisken ve
kaynak ozetlerini,
anonim islev parametre ve varsayilan arguman ozetlerini, inline anonim islev
govde ifadesini, liste uretec degiskenini ve kosul varligini, sozluk
anahtarlarini, liste/sozluk oge sayilarini, dilim erisim sinir varligini,
paralel yap govde komut sayisini ve yapisal komutlarini, liste/sozluk literal postfix ozetlerini,
alan/ust erisim adlarini, islev cagri adlarini, yeni nesne sinif adlarini ve
arguman sayilarini, parse sonuc hata var/yok, hata mesaji, ortak tani listesi,
ifade satir araligi, komut satir araligi, ic ice bloklardaki tum komut satir
araliklari ve alt ifadeler/paralel komutlar dahil tum ifade satir araliklari
yardimcilarini C++ AST ile karsilastiriyor. Tum ifade araliklari tekli atama
hedeflerini ve isimli/isimsiz islev varsayilan degerlerini de kapsiyor. Ifade
agaci toplam sayi, sirali turler, tur sorgulari ve en buyuk derinlik olarak
ozetlenebiliyor. Komut agaci da ic ice bloklar ve ifade icindeki `paralel yap`
govdeleri dahil toplam sayi, sirali turler, tur sorgulari, satir araliklari ve
en buyuk derinlik olarak ozetlenebiliyor. Basarili ve hatali sonuclar
`orhun-parser-ir-v2` sozlesme kimligini ve dogrulanmis lexer IR kokenini
tasiyor; uyumluluk ve toplu IR ozeti saf Orhun yardimcilariyla sorgulanabiliyor.
Ham token girisi de ayni lexer dogrulama sinirindan geciyor.
Metin, sayi, mantik ve parantezli ifade gibi atomlardan sonra gelen indeks ve
dilim zincirleri de C++ AST'siyle ayni yapisal ozeti uretir.
Program/komut/blok/ifade baglantilari,
isimsiz varsayilanlar ve paralel govdeler 256 seviye sinirli recursive IR
dogrulamasindan gecirilebiliyor. Ifade/komut tur sayilari ve ture gore kaynak
araliklari, dogrulama durumuyla birlikte istege bagli IR kaynak indeksinde
toplanabiliyor.

Hedefler:

- Orhun kaynakli lexer prototipi yazilir.
- Orhun kaynakli parser prototipi AST veya ara temsil uretir.
- C++ lexer/parser ile Orhun lexer/parser ciktisi ayni testlerde
  karsilastirilir.
- C++ lexer token akisi `orhun lex --json` ile makine-okur hale gelir.
- C++ parser AST akisi `orhun parse --json` ile makine-okur hale gelir.
- Lexer parity fixture'lari `tests/lexer_parity/` altinda genisler.
- Parser AST fixture'lari `tests/ast_json/` altinda genisler.
- Orhun parser prototipi once ust seviye komut turlerinde C++ AST ile
  eslenir, sonra blok komut ozetlerine, ana ifade cocuklarina ve daha derin
  blok/ifade agaci detaylarina genisler.
- Hata fixture'lari satir, beklenen-token ipucu, taninmayan komut ve komut
  onerisi seviyesinde C++ parser ile eslenir.

Basari olcutu:

- En az 100 dil fixture'i iki parser yolunda ayni ara temsili uretir.
- Hata mesajlari Turkce ve ogretici kalir.
- Yerel gelistirmede `python tests/roadmap_smoke.py ./build/orhun_test`
  self-hosting, fixture, surum, lambda capture ve closure regresyon kontrollerini
  birlikte gecirir.

## Faz 3: Orhun Ile Bytecode Derleyici

Durum: aktif; C++ derleyici ciktisini artifact uretmeden cozumleyen
`orhun baytkod <dosya.oh> --json` parity yuzeyi ve sozlesme smoke testi
hazirlandi. `orhun/derleyici.oh` 0.33.0; parser girdisinde
`orhun-parser-ir-v2` sozlesmesini, lexer kokenini ve recursive yapi
dogrulamasini zorunlu tutar;
basarili bytecode nesnelerini `orhun-bytecode-ir-v1` sozlesmesiyle surumler ve
parser kokeni, opcode/operand/IP, sabit, sayim, islev metadata ve program sonu
yapisini C++ koprusunden once saf Orhun koduyla dogrular;
sabitler, bicimlendirilmis metinler,
global kimlik okuma/atama,
temel ikili/tekli islemler, liste/sozluk literal'leri, basit global islev
cagrilari, kisa devreli `ve`/`veya`, indeks/alan/guvenli alan okumalari,
`eger/degilse`, basit `surece`
ve `tekrarla` donguleri, `her ... icinde ...` liste donguleri ve `yazdir` icin opcode, operand, IP, kaynak satiri ve
sabit havuzu parity'si uretiyor.
Islev-ici `her` dongulerinin kaynak, indeks ve iterasyon degiskenleri de C++
derleyiciyle ayni yerel bildirim opcode'larini kullanir.
Zorunlu/varsayilan parametreli islev tanimlari, yerel tanim/okuma/yazma, acik/ortuk donus ve
`OP_ISLEV_OLUSTUR` local-ad metadata'si de ilk parity kapsaminda.
Dogudan literal sayi/metin/mantik islemleri ve tekli islemler C++ ile ayni
sabit katlama kurallarini uygular.
Sabit dogrulukla belirlenen `eger` dallari, `surece yanlis` ve sifir/negatif
`tekrarla` govdeleri bytecode uretmeden elenir.
Alan/indeks atamalari, dilim okumalari ve global/local coklu atamalar da
fixture parity kapsamindadir.
Noktali modul/islev cagrilari ile ifade ve komut bicimindeki `dahil_et`
derlemeleri de parity kapsamindadir.
`deneme/yakala` kontrol akisi ve global/local hata degiskeni baglama davranisi
da parity kapsamindadir.
`yeni` nesne olusturma ve ifade/komut bicimindeki `sor` cagrilari da parity
kapsamindadir.
Ic ice dongu baglamlari, `kir` atlamalari ve `devam` hedef/yama davranisi da
parity kapsamindadir.
Isimsiz islevler, ic ice isimli islevler, varsayilan argumanlar ve kararlı
`__anonim_islev_N` metadata adlariyla parity kapsamindadir. Dis yerel okuma ve
degistirme, C++ derleyicisiyle ayni isim tabanli opcode + VM yakalama
sozlesmesini uretir. Ic ice isimli islevler blok basinda yerel hucrelerini
hazirlar; global adlari sizdirmadan oz yineleme ve karsilikli oz yineleme yapar.
Filtreli/filtresiz liste uretecleri, kapasite ayirma optimizasyonu, gecici
degisken adlari ve islev-ici yerel metadata davranisiyla parity kapsamindadir.
Dis islev tanimlari ad, kutuphane, donus tipi ve parametre tipi listesiyle
mevcut FFI politika yuzeyine derlenir.
Alan tanimli siniflar, metodlar, temel kalitim kurulumu, `benim` alan
okuma/yazma ve `ust` metod cagrilari parity kapsamindadir. Metod metadata'si
baglam argumanlarini ve varsayilan parametre ofsetlerini C++ ile ayni uretir.
`paralel yap` adimlari yapisal parser IR'indan gorev plan sozluklerine
indirgenir ve parity kapsamindadir.
Compiler prototype smoke su anda 98 programda C++ bytecode ozetini birebir
eslestirir. Bu kapsam buyuk closure, OOP, varsayilan metod argumani ve
liste-ureteci/lambda/paralel-yap fixture'larini da dogrudan karsilastirir;
desteklenmeyen yapilar icin acik hata bekler.
Tum `tests/cases` derleyici sweep'i, C++ derleyicisinin kabul ettigi 162
programin tamaminda Orhun derleyicisinin bytecode ozetini birebir eslestirdigini
dogrular; C++ tarafindaki 2 bilincli hata fixture'i ayri izlenir.
`orhun baytkod-yurut <dosya.json>` koprusu, Orhun derleyicisinin cozumlenmis
bytecode ciktisini siki dogrulamadan sonra C++ VM'de calistirir. Bootstrap smoke
testi bicimlendirilmis metin, ic ice islev, OOP/ust ve hata yakalama programlarini
bu kopruyle yurutup dogrudan `vm-kati` ciktisiyla karsilastirir.
Deneysel `orhun orhun-vm <dosya.oh>` komutu ayni hatti ara JSON dosyasi olmadan
tek komutta calistirir.
Deneysel `orhun orhun-derle <dosya.oh> [cikti]` komutu Orhun derleyici yolundan
`.obc`, paketli calistirilabilir dosya ve metadata uretir; bootstrap testi C++
derleyici artifact'lariyla byte duzeyinde esitligi dogrular.

Hedefler:

- Orhun kaynakli derleyici bytecode uretmeye baslar.
- C++ VM ayni bytecode'u calistirir.
- C++ compiler ve Orhun compiler ciktisi fixture bazinda karsilastirilir.
- C++ compiler bytecode akisi `orhun baytkod --json` ile makine-okur kalir.

Basari olcutu:

- Temel dil, fonksiyonlar, listeler, sozlukler, siniflar ve hata modeli icin
  bytecode parity saglanir.

## Faz 4: Kendi Kendini Derleyen Orhun

Durum: basladi; `orhun orhun-derle StdLib/orhun/derleyici.oh <cikti>` calisir
ve C++ derleyicinin ayni kaynak icin urettigi `.obc` ile byte duzeyinde ayni
bootstrap artifact'ini uretir. Bu artifact henuz tek basina kaynak kabul eden
bagimsiz bir derleyici CLI'i degildir.
`ORHUN_MODULE_MODE=obc-only` ile onceden derlenmis Orhun
derleyici/parser/lexer modul zinciri `.oh` kaynaklari olmadan ve C++ kaynak
derleme fallback'i yapmadan calisir; eksik modul artifact'i acik hata verir.
`orhun-vm` ve `orhun-derle`, bu zinciri tek komutta secmek icin `--obc-only`
ve `--obc-first` CLI politikalarini destekler.
`orhun bootstrap-hazirla <dizin>`, lexer/parser/derleyici modulleri ile
derleyici CLI girisini kaynak dosyasi icermeyen bir toolchain klasorune ve
boyut/CRC32/SHA-256 tasiyan makine-okur manifeste donusturur.
`orhun bootstrap-dogrula <toolchain>`, manifest sozlesmesini, tam modul
listesini, payload boyut/CRC32/SHA-256 degerlerini ve OBC yapisini hedef
calistirmadan dogrular; derleme ve calistirma komutlari da once ayni denetimi
yapar.
`orhun bootstrap-derle <toolchain> <kaynak.oh> [cikti]`, hazirlanan toolchain'i
ortam degiskeni gerektirmeden kati `obc-only` modunda kullanir.
`orhun bootstrap-calistir <toolchain> <kaynak.oh>`, ayni zincirle hedefi
derleyip VM'de calistirir.
`orhun bootstrap-derleyici-paketle <toolchain> <cikti-dizini>`, kardes
toolchain'ini farkli calisma klasorlerinden otomatik bulan ve dogrulayan,
kaynak-kodsuz tasinabilir `orhun-derleyici` calistirilabilir dosyasini uretir.
Bu ilk bagimsiz derleyici CLI'i bytecode JSON uretir; `--derle` modu ayni
Orhun-yazili compiler zinciriyle byte-duzeyinde esit `.obc`, paketli
calistirilabilir dosya ve metadata artifact'larini dogrudan uretir. Artifact
isteginin kaynak/cikti argumanlarini ve `.obc`, paketli calistirilabilir,
metadata yollarindan olusan tam cikti planini artik Orhun-yazili
`derleyici_cli.oh` 0.6.0 cozer. Her cagri `orhun-compiler-cli-v1` sonuc zarfinda CLI
surumunu, islem turunu, cikis kodunu ve saf Orhun `cli_dogrulamasi` kaydini
tasir. Artifact plani ayrica `orhun-artifact-plan-v1` sozlesmesiyle surumlenir.
C++ cekirdegi CLI ve plan zarflarini bilinmeyen sozlesme, tutarsiz islem/durum,
basarisiz dogrulama, bos alan, beklenmeyen uzanti, kaynak adinda yol ayirici ve
cakisan cikti yollarina karsi dogruladiktan sonra yalniz OBC/paket
serilestirme ve dosya yazma koprusu olarak kalir. Artifact'lar once hedeflerinin
yanindaki benzersiz gecici dosyalara
yazilir; tumu hazirlanmadan yayinlanmaz ve hazirlama hatasi mevcut ciktilari
korur. Paketli C++ host `--derle` veya `--compile` komut adlarini bilmez; her
cagrinin yapilandirilmis cikis kodu ve artifact plani Orhun CLI bytecode'u
tarafindan uretilir. Compiler bundle kimligi dosya adina degil, dogrulanan
v2 bundle manifestine, embedded CLI payload boyut/CRC32/SHA-256 degerine ve
kardes v2 toolchain manifestindeki modullerinin boyut/CRC32/SHA-256
degerlerine dayanir. Eski v1 manifestleri dogrulanmaya devam eder.
`orhun bootstrap-yeniden-uret <tohum-toolchain> <cikti-dizini>`, tohum ile
asama 2'yi, asama 2 ile asama 3'u uretir ve son iki asamadaki dort artifact'in
byte duzeyinde ayni olmasini zorunlu tutar. Dolu cikti dizinini ezmez ve
basarili kapinin sonucunu dort artifact'in boyut/CRC32/SHA-256 kimligini
tasiyan `orhun-bootstrap-rebuild-v2` manifestiyle kaydeder.
`orhun bootstrap-yeniden-dogrula <toolchain>`, bu yeniden uretim kanitini ve
eslik eden strict toolchain manifestini daha sonra yeniden dogrular.
`sistem.argumanlar`, dogrudan, paketli ve bootstrap calistirma yollarinda ayni
program argumani sozlesmesini saglar; bagimsiz derleyici CLI'i bu primitive ile
kaynak/cikti yollarini okuyup tam artifact planini Orhun kodunda uretir.

Hedefler:

- Orhun compiler kaynagi Orhun ile derlenebilir.
- Release surecinde C++ bootstrap sadece ilk araci uretir.
- Sonraki asamada Orhun compiler kendi yeni surumunu uretebilir.
- CI tarafinda dogrulanan tasinabilir compiler bundle'lari surumlu, SHA-256
  dogrulamali ve GitHub/Sigstore build-provenance attestation'li release
  asset'lerine donusturulur; platform code-signing ayri bir katman olur.
- Release runtime'i `-O2 -DNDEBUG` ile uretilir ve arsivlenen ayni binary tam
  release kapisindan gecirilir.

Basari olcutu:

- `orhun derle compiler.oh` calisir.
- Uretilen derleyici ayni test paketini gecen bytecode veya native cikti uretir.

## Faz 5: AOT ve Native Cikti

Hedefler:

- VM varsayilan ve guvenilir yol olarak kalir.
- AOT backend opsiyonel hiz yolu olur.
- Once C veya LLVM IR gibi denetlenebilir bir ara cikti, sonra dogrudan native
  backend degerlendirilir.

Basari olcutu:

- CPU agir benchmarklarda VM'in ustune cikan AOT cikti alinabilir.
- AOT ciktisi Orhun'un guvenlik ve paket politikalarini bozmaz.

## Yakin Donem Sirasi

1. Repo hijyenini ve hizli, guvenilir CI kapilarini koru.
2. Saf Orhun stdlib cekirdegini genislet: metin, koleksiyon ve paket manifest
   yardimcilarini Orhun kaynaklarina tasi.
3. Lexer ve parser ara temsil sozlesmelerini self-hosting icin sabitle.
4. Surumlu ve provenance-attested kaynak-kodsuz derleyici/runtime arsivlerinin
   ustune platform code-signing ve yerel kurucu katmanlarini ekle.
5. Orhun ile yeni dil ve DSL yazmayi kolaylastiran ortak token, parser kurtarma,
   tani ve AST yardimcilarini genislet.
6. AOT denemelerini VM ve guvenlik sozlesmesini bozmadan baslat.
