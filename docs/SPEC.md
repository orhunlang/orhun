# Orhun Language Specification

This document is the living language contract for Orhun. It describes the
behavior that the current runtime should preserve while the project moves from a
C++ bootstrap implementation toward self-hosting.

Status: draft, pre-1.0.

## Design Goals

Orhun is designed to be:

- Turkish-first by default.
- Readable for beginners without hiding professional language features.
- Runtime-independent from Python, JavaScript, or other high-level language
  runtimes.
- VM-first, with a path toward self-hosting and optional native output later.
- Strict about safety-sensitive areas such as shell execution, FFI, and package
  verification.

## Source Files

- Orhun source files use the `.oh` extension.
- Source text is UTF-8.
- Turkish characters are valid in keywords and identifiers.
- Newlines are significant.
- Indentation creates blocks.
- `#` starts a line comment that continues until the end of the line.

Example:

```orhun
# Bu bir yorumdur.
ad olsun "Orhun"
yazdır ad
```

## Keywords

Current Turkish keywords:

```text
yazdır olsun eğer ise değilse doğru yanlış tekrarla kez sor her
işlev dış_işlev döndür dahil_et sürece eşit eşit_değil büyük küçük
ve veya değil tip yeni benim deneme yakala kır devam ust için içinde
paralel yap
```

Compatibility alias:

```text
dis_islev
```

In Turkish strict mode, compatibility aliases are rejected.

Strict mode is enabled with:

```bash
orhun --turkce-kati dosya.oh
```

or:

```bash
ORHUN_TURKCE_KATI=1 orhun dosya.oh
```

## Identifiers

Identifiers may start with:

- `_`
- ASCII letters
- Turkish letters: `ç Ç ğ Ğ ı I İ ö Ö ş Ş ü Ü`

After the first character, digits are also allowed.

Examples:

```orhun
öğrenciSayısı olsun 42
sınıfAdı olsun "Matematik"
```

## Values

The current runtime value model contains:

- `bos`
- numbers
- booleans
- strings
- lists
- dictionaries
- functions
- native functions
- classes
- instances
- bound methods

Boolean literals:

```orhun
doğru
yanlış
```

`bos`, booleans, and numbers are distinct runtime types in both execution
engines. In particular, `doğru eşit 1` and `yanlış eşit 0` are false even
though booleans may be converted to `1` and `0` by numeric operators. JSON
conversion preserves this distinction: `bos` maps to `null`, booleans map to
JSON booleans, and numbers remain JSON numbers.

## Truthiness

Values considered false:

- `bos`
- `yanlış`
- number `0`
- empty string
- empty list
- empty dictionary

All other values are considered true.

## Variables And Assignment

Variable definition and reassignment use `olsun`.

```orhun
ad olsun "Orhun"
puan olsun 100
puan olsun puan + 1
```

`=` is supported as assignment compatibility syntax in current builds. Inside
functions, `=` updates an existing local binding when one exists; otherwise it
writes the global binding. Use `olsun` to create or update the current
function's local binding.
That lookup is limited to the current function frame: loop blocks can update a
local declared by the same function, while a called function cannot overwrite
the caller's same-named local merely by declaring its own binding.
All function reads and `=` writes use lexical scope in both runtimes. A call
can see its own locals, explicit closure captures, module bindings, and globals,
but it cannot read or mutate an unrelated local belonging only to its caller.
An unresolved name therefore continues as a module/global lookup instead of
falling through into the dynamic call stack.

Multiple assignment and destructuring are supported by the current test suite.

```orhun
a, b olsun [1, 2]
```

The number of assignment targets must exactly match the source list length.
Both runtimes reject missing and surplus values before writing any target.

## Operators

Arithmetic operators are `+`, `-`, `*`, `/`, and `%`. Modulo uses the same
zero-divisor error contract in the interpreter and VM. `ve` and `veya` are
short-circuit boolean operators in both runtimes. They return normalized boolean
results and do not evaluate the right operand when the left operand determines
the result.

Equality is type-sensitive except for the interpreter's internal integer and
decimal number representations, which compare by numeric value. Boolean and
`bos` values never compare equal to a number. List and string indexes require
the numeric runtime type, so a boolean cannot be used as an implicit index.

## Printing

`yazdır` evaluates an expression and writes its text form. `yaz` is the short
beginner-friendly command alias; it behaves the same as `yazdır` without making
`yaz` a reserved word, so `yaz olsun "değer"` is still a normal assignment.

```orhun
yaz "Merhaba"
yazdır "Merhaba"
yazdır 40 + 2
```

Current display behavior:

- `bos` prints as `bos`.
- Booleans print as `1` and `0` for interpreter/VM parity.
- Lists and dictionaries print in structural form.

`listeye_ekle(liste, deger)` mutates the supplied list in both the interpreter
and VM. The equivalent method form is `liste.ekle(deger)`.

## Input

`sor` prompts the user and returns one input line. `oku` is the beginner-friendly
function alias for the same behavior.

```orhun
ad olsun oku("Adın? ")
yaz "Merhaba, " + ad
```

## Ranges

`aralik` creates a list of numbers without requiring a module import. The
Turkish spelling `aralık` is also available. It accepts one, two, or three
arguments:

```orhun
yaz aralik(5)          # [0, 1, 2, 3, 4]
yaz aralik(1, 5)       # [1, 2, 3, 4]
yaz aralık(5, 1, -2)   # [5, 3]
```

An `adim` value of `0` returns an empty list, matching the current
`orhun/temel.oh` helper behavior.

## Control Flow

### If

```orhun
eğer puan büyük 50 ise:
    yazdır "geçti"
değilse:
    yazdır "kaldı"
```

### Repeat

```orhun
tekrarla 3 kez:
    yazdır "Orhun"
```

The colon after `kez` is optional for compatibility with existing fixtures.

### While

```orhun
i olsun 0
sürece i küçük 3:
    yazdır i
    i olsun i + 1
```

### For Each

```orhun
meyveler olsun ["elma", "armut", "kiraz"]
her meyve içinde meyveler:
    yaz meyve
```

`her <ad> içinde <liste>:` iterates over list values. The iterable expression is
evaluated once before the loop starts. The loop variable is bound for each
iteration, and `kır` / `devam` work against the nearest loop.

### Loop Control

```orhun
kır
devam
```

`kır` exits the nearest loop. `devam` continues the nearest loop.

## Functions

Functions use `işlev`.

```orhun
işlev topla(a, b):
    döndür a + b

yazdır topla(2, 3)
```

Function, method, and constructor calls may span multiple lines. Newlines and
indentation inside the argument list are layout only, and a trailing comma
before `)` is allowed. Parenthesized expressions may also span multiple lines.

```orhun
sonuc olsun topla(
    2,
    3,
)
```

Default arguments are supported.

```orhun
işlev selam(ad olsun "dünya"):
    döndür "Merhaba, " + ad
```

Required parameters may not appear after default-valued parameters.

A function or anonymous function that reaches the end without `döndür`
returns `bos`. Side-effect helpers such as `listeye_ekle`, `dosya.yaz`, and
`bekle` follow the same no-value contract in the interpreter and VM.

Named functions, methods, anonymous functions, and external-function
declarations may split their parameter lists across multiple lines. A trailing
comma before `)` is allowed, and a default value may begin on the next line.

```orhun
işlev selamla(
    ad,
    selam olsun
        "Merhaba",
):
    yazdır selam + ", " + ad
```

Anonymous functions are supported by the current parser/runtime.

```orhun
iki_kat olsun işlev(x): x * 2
yazdır iki_kat(4)
```

Call lookup is lexical. A callable stored in a local or captured binding wins
over a same-named module, global, or built-in function. The same rule applies
to the root of a dotted call, so a local `metin` value can intentionally shadow
the built-in `metin` module.

Named functions declared inside another function are local bindings; they do
not overwrite a same-named global function. Direct nested declarations in the
same block receive shared cells before their function objects are created, so
self-recursion and mutual recursion work while returned closures keep those
cells alive. Re-entering a loop block creates fresh cells for that iteration.

## Collections

Lists:

```orhun
sayılar olsun [1, 2, 3]
yazdır sayılar[0]
yaz ilk(sayılar)
yaz son(sayılar)
yaz dolu_mu(sayılar)
sayılar.ekle(4)
sayılar.sil(1)
```

List methods `ekle(deger)`, `sil(indeks)`, and `uzunluk()` return or inspect
the same mutable list in both execution engines. `ekle` and `sil` return the
list, allowing a mutation to be used in a larger expression.

Dictionaries:

```orhun
kullanıcı olsun {"ad": "Ali", "yaş": 28}
yazdır kullanıcı.ad
yazdır kullanıcı["ad"]
yazdır kullanıcı.anahtarlar()
yazdır kullanıcı.degerler()
yazdır kullanıcı.uzunluk()
```

Dictionary methods `anahtarlar()`, `degerler()`, `sil(anahtar)`, and
`uzunluk()` have the same behavior in the interpreter and VM. A real field with
one of these names takes precedence over the built-in method.

String methods `buyuk()`, `kucuk()`, `parcala(ayirici)`, and `uzunluk()` are
also available with matching interpreter and VM behavior.
`icerir(kaynak, aranan)` and `metin.icerir(kaynak, aranan)` require both
arguments to be strings; implicit collection or number stringification is not
performed.

List and dictionary literals may span multiple lines. Newlines and indentation
inside the literal are layout only, and a trailing comma before `]` or `}` is
allowed.

List and string indices must be zero-or-positive integers. Dictionary index
reads and writes require string keys. The interpreter and VM reject fractional,
negative, and implicitly converted index values instead of rounding them.

```orhun
ayarlar olsun {
    "ad": "orhun",
    "portlar": [
        8080,
        8081,
    ],
}
```

Index and slice access may also span multiple lines.

```orhun
orta olsun sayılar[
    1:
    3
]
```

Inside an open `()`, `[]`, or `{}` delimiter, an expression may continue on
the next line after a binary or unary operator. Outside delimiters, a newline
still ends the expression.

```orhun
toplam olsun (
    10 +
    20 *
    2
)
```

Postfix chains may also continue on the next line inside an open delimiter.
This includes field access, safe field access, calls, indexes, and slices.

```orhun
deger olsun (
    kutu
    .oku(
    )
)
```

Blank lines and `#` comments are layout wherever multiline delimiter layout is
allowed. They do not terminate calls, collection literals, continued
expressions, or postfix chains.

```orhun
sonuc olsun topla(
    # First value
    2,

    # Second value
    3,
)
```

List comprehensions are supported.

```orhun
sonuç olsun [x * 2 için x içinde [1, 2, 3]]
```

The source after `içinde` must evaluate to a list. Interpreter and VM paths
reject non-list sources with the same runtime contract.

Collection helpers:

- `ilk(liste, [yedek])` returns the first item. Empty lists require `yedek`.
- `son(liste, [yedek])` returns the last item. Empty lists require `yedek`.
- `bos_mu(deger)` / `boş_mu(deger)` checks whether a string, list, or
  dictionary is empty.
- `dolu_mu(deger)` checks whether a string, list, or dictionary has at least
  one item.

## Classes

Classes use `tip`.

```orhun
tip Selamlayici:
    işlev selam(ad olsun "dünya"):
        döndür "Merhaba, " + ad

s olsun yeni Selamlayici()
yazdır s.selam()
```

Inheritance:

```orhun
tip A:
    işlev değer():
        döndür 1

tip B(A):
    işlev değer():
        döndür ust.değer() + 1
```

Inside methods:

- `benim` refers to the receiver.
- `ust` refers to the parent method context.

For inherited method calls, `ust` must resolve relative to the class that owns
the currently executing method, not merely the runtime class of the instance.

## Error Handling

Runtime errors can be handled with `deneme` / `yakala`.

```orhun
deneme:
    yazdır 42?.ad
yakala hata:
    yazdır hata
```

Interpreter and VM diagnostics use the same generated anonymous-function names,
current source lines, and stack-frame order. A caught error preserves that stack
trace so logging it has the same result in both execution paths.

The standard result-value helper is exposed as `sonuc`.

```orhun
başarılı olsun sonuc.ok(42)
hatalı olsun sonuc.hata("olmadı")
```

## Safe Access

Safe access uses `?.`.

```orhun
kullanıcı olsun {"ad": "Ali"}
yazdır kullanıcı?.ad
yazdır kullanıcı?.profil?.yaş
```

If the left side is `bos` or missing in a safe chain, the result is `bos`.
Invalid non-object access still produces a runtime error.

## Modules And Includes

`dahil_et` loads another Orhun file.

```orhun
matematik olsun dahil_et "matematik.oh"
```

Lookup order:

1. The requested path exactly as written.
2. Each root in `ORHUN_STDLIB_PATH`.
3. A sibling `StdLib/` directory beside the running `orhun` executable.
4. The local development standard library roots `StdLib/` and `stdlib/`.

Resolved module paths are canonicalized and cached for the lifetime of the
interpreter or VM. Repeating `dahil_et` with equivalent paths returns the same
module object without rerunning its top-level code, so mutable exported values
are shared between import aliases. Nested module functions retain their own
module variables and sibling-function namespace in both the interpreter and
VM; same-named caller globals cannot shadow them. Module initialization can
read built-ins but not caller-owned globals. Assigning a module global from a
module function updates the exported module object without overwriting the
caller's global, including names first created after import. Exported anonymous
and nested functions retain the lexical module environment. Imports executed
inside a function still initialize the module in an isolated module scope
rather than writing into the caller's locals. An A -> B -> A dependency is
rejected with an explicit circular-module error instead of recursing forever.

Official Orhun-source standard modules live under `StdLib/orhun/` and are
included by their library-relative path:

```orhun
temel olsun dahil_et "orhun/temel.oh"
sonuc_yardimci olsun dahil_et "orhun/sonuc.oh"
koleksiyon olsun dahil_et "orhun/koleksiyon.oh"
metin_yardimci olsun dahil_et "orhun/metin.oh"
paket_yardimci olsun dahil_et "orhun/paket.oh"
dil_yardimci olsun dahil_et "orhun/dil.oh"
lexer olsun dahil_et "orhun/lexer.oh"
```

`orhun/sonuc.oh` provides explicit `ok`/`hata` records and composable helpers.
In addition to `haritala` and `zincirle`, `hata_haritala`, `kurtar`,
`birlestir`/`birleştir`, and `tumunu_birlestir`/`tümünü_birleştir` support
error transformation, recovery, and fail-fast result aggregation.

`orhun/koleksiyon.oh` includes beginner-friendly list helpers such as
`haritala`, `filtrele`, `katla`, `benzersiz`, `numaralandir`, and
`eslestir`/`eşleştir`. `numaralandir(liste, [baslangic])` returns
`[sira, deger]` pairs, and `eslestir(sol, sag)` returns pairs up to the
shorter list. `toplam(liste, [baslangic])` accumulates values with `+`.
`en_kucuk`/`en_küçük` and `en_buyuk`/`en_büyük` return their explicit fallback
value for an empty list. `ilk`, `son`, and `indeks` provide fallback-aware
lookup; `al` and `atla` select list regions; `parcalara_ayir`/
`parçalara_ayır` and `duzlestir`/`düzleştir` handle nested list shapes.
`birlesim`/`birleşim`, `kesisim`/`kesişim`, and `fark` provide stable-order
set-like operations, while `sirala`/`sırala` returns an ascending copy without
mutating the input list.

`orhun/metin.oh` includes beginner-friendly string helpers such as `say`,
`on_eki_kaldir`/`ön_eki_kaldır`, and `son_eki_kaldir`/`son_eki_kaldır`.
`say` counts non-overlapping occurrences and returns zero for an empty search
string. Prefix and suffix removal return the original string when it does not
match. `ilk_konum` and `son_konum` perform fallback-aware searches;
`sol_doldur`, `sag_doldur`/`sağ_doldur`, and `ortala` produce text with an
exact requested width even when the fill text contains multiple characters.

`orhun/sozluk.oh` provides safe lookup, copying, merging, key selection and
exclusion, plus callback-based value mapping and key filtering. These helpers
are written in Orhun and build on `orhun/koleksiyon.oh` rather than adding new
runtime primitives.

`orhun/paket.oh` includes package manifest helpers such as `coz`,
`coz_ve_dogrula`, `dogrula`, `bagimliliklar`, `bagimli_mi`, and
`ad_gecerli_mi`. Manifest package names and dependency names should contain
only letters, digits, `_`, `.`, and `-`; the special names `.` and `..` are
invalid. Manifest versions are validated as
Semantic Versioning 2.0 versions by the Orhun-written `surum_gecerli_mi`
helper, including prerelease and build identifiers. `surum_ayristir` returns a
result record whose value separates a valid version into numeric `ana`, `yan`,
and `duzeltme` fields plus `on_surum` and `yapi` strings. `surum_karsilastir`
returns an error result for an invalid input, otherwise its result value is
`-1`, `0`, or `1` according to Semantic Versioning precedence. Build metadata
does not affect precedence; a release has higher precedence than its matching
prerelease. `surum_uyumlu_mu(surum, kural)` accepts exact versions plus `*`,
`=`, `>`, `>=`, `<`, `<=`, `^`, and `~` rules, and returns a result record
whose value is a boolean. Range operands must be complete valid Semantic
Versioning versions; combined ranges are intentionally not yet part of this
small manifest-helper contract.

The same module includes a self-hosted structural parser for `orhun.lock`
records: `kilit_satirini_coz`, `kilit_dosyasini_coz`, `kilit_kaydi_metni`, and
`kilit_dosyasi_metni`. It accepts compatible v1, v2, and v3 records and rejects
unsafe package names, incomplete v3 commit/content fields, and invalid source
refs before a future Orhun-written resolver touches a package path. Cryptographic
digest calculation and filesystem-content verification remain native runtime
responsibilities for now.

`bagimlilik_plani(manifestler)` validates each manifest, rejects duplicate
package definitions, missing direct dependencies, and cycles, then returns a
stable dependency-first package-name order. This keeps graph planning in
Orhun source while package download, hashing, and filesystem mutation remain
behind explicit runtime commands.

`bagimlilik_istegi(ad, kural)` represents a versioned package request.
`en_uygun_bagimlilik` chooses the highest valid candidate matching that
Semantic Versioning rule, while `bagimlilikleri_sec` resolves a unique request
set and rejects duplicate requests or missing compatible candidates.
`bagimlilik_aday_surimleri` exposes the valid candidate versions for a request;
an unsuccessful selection distinguishes a missing package name from an
incompatible version rule and lists the available versions in the latter case.
Manifest validation rejects duplicate direct dependency names before version
selection or lock coverage is evaluated.
Both the C++ package boundary and `kilit_dosyasini_coz` reject duplicate
package names in `orhun.lock`, preventing an ambiguous lock record from being
installed, validated, updated, or removed.
`manifest_kilit_bagimliliklarini_dogrula(manifest, kilit_kayitlari)` verifies
that every direct manifest dependency has a valid, unique lock record before a
future Orhun-written resolver downloads or changes package files.
The native `orhun paket dogrula` command applies the same direct-dependency
coverage check to the current `orhun.yap` and `orhun.lock` files.
Manifests can carry an optional `bagimlilik_istekleri` list of `{ad, kural}`
records. Every request must name a direct `bagimliliklar` entry, have a valid
rule, and occur only once.
`manifest_bagimliliklarini_sec(manifest, adaylar)` resolves a validated
manifest's direct dependencies; entries without an explicit request use `*`.

`orhun/dil.oh` includes language-development helpers for Orhun-source
compiler and DSL prototypes. It exposes token records (`token`, `dosya_sonu`,
`hata_token`, `token_mi`), token-stream cursors (`imlec`, `simdiki`, `onceki`,
`ilerle`, `bitti_mi`, `esles`, `bekle`), diagnostics (`tani`, `tani_ekle`),
and AST builders (`dugum`, `yaprak`, `program`, `dugum_sayisi`,
`dugum_turleri`). ASTs can also be traversed with
`dugumleri_duzlestir`, `dugum_turlerini_duzlestir`,
`dugumleri_filtrele`, `dugum_turu_var_mi`, `dugum_derinligi`,
`dugum_turu_sayisi`, and `dugum_ozeti` for small compiler and DSL passes.
`bekle` returns the standard `sonuc` result shape, so callers
can keep parser errors explicit without throwing. Diagnostics can be rendered
consistently with `tani_konumu`, `tani_bicimlendir`, and
`tanilari_bicimlendir`; standalone diagnostic arrays can use
`tani_listesi_bicimlendir` and `tani_listesi_kaynak_bicimlendir`. Diagnostic
arrays can also be inspected with `tani_listesi_seviyeleri`, counted with
`tani_listesi_seviye_sayisi`, filtered with
`tani_listesi_seviyeye_gore_filtrele`, and summarized with
`tani_listesi_ozeti`. Callers can also inspect `tani_kodlari` or query an
expected code through `tani_kodu_var_mi`. `tani_kaynak_bicimlendir` adds the
matching source line and a column marker for teaching-oriented command-line
and DSL diagnostics, including valid blank source lines. `tani_araligi` marks
a multi-character source range with `^~~`, while `tani_uyarisi` produces a
non-fatal warning record. `tani_ipucu_ekle` attaches an actionable Turkish
hint without changing the diagnostic code or source location.
`token_uzunlugu` and `token_tanisi` derive an UTF-8-aware source range from a
token, so lexer and parser prototypes do not need to repeat column arithmetic.

The public package and module system is still evolving. Pre-1.0 code should keep
module behavior covered by tests.

`orhun paket kaldir <paket_adi>` and its Turkish-character alias
`orhun paket kaldır <paket_adi>` remove only a validated direct
`lib/<paket_adi>` directory. A successful removal also removes the matching
`orhun.lock` record and the exact dependency entry from the `bagimliliklar`
section of `orhun.yap`. Lock verification and lock updates reject invalid
package names before resolving their corresponding `lib` paths. Removal
preflights every existing lock record before deleting the package directory.

On Windows, Orhun reads the native wide-character command line and converts
every argument to UTF-8 before CLI dispatch or exposure through
`sistem.argumanlar`. Turkish aliases, paths, and program arguments therefore do
not depend on the active ANSI code page.

## Concurrency

Task primitives are available through `gorev`.

`paralel yap` is the language-level syntax for starting supported task plans.

```orhun
g1 olsun paralel yap:
    bekle(0)
    bekle(0)

g2 olsun paralel yap: bekle(0)
sonuçlar olsun gorev.hepsi_bekle([g1, g2])
```

The current `paralel yap` implementation is intentionally narrow and should be
expanded only with tests. The tree-walking interpreter and bytecode VM both
lower it to the same `gorev.baslat_plan` contract.

## Standard Modules

Current built-in module surfaces include:

- `dosya`
- `internet`
- `json`
- `metin`
- `regex`
- `tarih`
- `veritabani`
- `sunucu`
- `sistem`
- `sonuc`
- `gorev`
- `ffi`
- `orhun/temel.oh`
- `orhun/sonuc.oh`
- `orhun/koleksiyon.oh`
- `orhun/sozluk.oh`
- `orhun/metin.oh`
- `orhun/paket.oh`
- `orhun/dil.oh`
- `orhun/lexer.oh`
- `orhun/parser.oh`
- `orhun/derleyici.oh`
- `orhun/derleyici_cli.oh`

Safety-sensitive modules must keep policy checks enabled by default.

Global numeric primitives include `tam(x)` (truncate toward zero) and
`taban(x)` (floor). Both runtimes also retain the variadic ASCII compatibility
call `yazdir(...)`; Turkish `yazdır`/`yaz` remains the documented default.

`sistem.argumanlar` is a list containing only the arguments passed after the
program source or runtime command. The runtime executable and source path are
not included. Global Orhun options such as `--turkce-kati` are interpreted only
when they appear before the command/source, so the same text can still be a
program argument after it. Direct source execution, `vm`, `vm-kati`, `yorumla`,
`obc`, packaged executables, `orhun-vm -- <arguments>`, and
`bootstrap-calistir` expose the same argument list.

## Orhun-Source Language Toolkit

`orhun/dil.oh` is the shared Orhun-source language-development toolkit. It is
intended for small compilers, educational DSLs, and future self-hosting pieces
that need common token, cursor, diagnostic, and AST conventions.

Example:

```orhun
dil olsun dahil_et "orhun/dil.oh"
tokenlar olsun [dil.token("AD", "merhaba", 1, 1), dil.dosya_sonu(1, 8)]
imlec olsun dil.imlec(tokenlar)
ad olsun dil.bekle(imlec, "AD", "", "ad bekleniyor")
ast olsun dil.program([dil.yaprak("SelamKomutu", ad.deger.deger, ad.deger)])
yazdır dil.token_degerleri(tokenlar)
yazdır dil.hata_var_mi(imlec)
yazdır dil.tani_listesi_ozeti(imlec.hatalar)
```

The module is intentionally small and pure Orhun. Its helpers do not replace
the production lexer or parser; they give Orhun programs a stable starting
point for building language tools with explicit diagnostics.

## Orhun-Source Lexer Prototype

`orhun/lexer.oh` exposes the first self-hosting lexer prototype. Its public
entry point is:

```orhun
lexer olsun dahil_et "orhun/lexer.oh"
sonuc olsun lexer.ozetle("yazdır \"Merhaba\"\n")
tokenlar olsun sonuc.tokenlar
yazdır lexer.degerleri(tokenlar)
yazdır lexer.lexer_ir_dogrula(sonuc)
```

Each token is a dictionary with `tur`, `deger`, `satir`, and `sutun` fields.
`ozetle(kaynak)` returns a dictionary with `ir_sozlesmesi`, `hata_sayisi`,
`token_sayisi`, and `tokenlar`, matching the C++ `lex --json` health shape used
by parity tests plus the additive `orhun-lexer-ir-v1` boundary.
`lexer_ir_uyumlu_mu` checks that boundary, while `lexer_ir_dogrula` verifies
token fields, positions, counts, error counts, and the final end-of-file token
before other Orhun-written tools consume the stream. `lexer_ir_gecerli_mi` and
`lexer_ir_ozeti` expose compact forms. Lexer-prefixed names keep this module's
helpers distinct when it is included by the parser.
Helper
functions expose token types, token values, UTF-8-aware token lengths, inclusive
source ranges (`satir`, `baslangic_sutun`, `bitis_sutun`, `uzunluk`), first
error token, error presence, error count, and error-token values.
The current prototype recognizes keywords, identifiers, numbers, decimals,
strings, one-character operators, indentation, LF newlines, end-of-file, and
error tokens. It is a parity target for the C++ lexer, not yet the production
lexer.

Lexer parity fixtures live in `tests/lexer_parity/` and are compared against the
C++ lexer through `tests/lexer_parity_smoke.py`. The same smoke can sweep the
runtime case suite with `--fixtures tests/cases` to guard token type, value,
line, and column parity across broader language examples.
Fixtures that intentionally exercise lexer errors use `# parity: allow-errors`;
for those cases the smoke compares error counts and token shape while leaving
the exact diagnostic text free for clearer Turkish wording.
Fixtures with non-ASCII source text compare token values and character-based
line/column positions. The Orhun-source lexer keeps byte offsets internally but
uses UTF-8 code-point counts when advancing diagnostic columns.
The runtime primitive `metin.utf8_uzunluk(metin)` exposes the same code-point
counting rule to Orhun-source tooling.

## Orhun-Source Parser Prototype

`orhun/parser.oh` exposes the first self-hosting parser prototype. Its public
entry point is:

```orhun
parser olsun dahil_et "orhun/parser.oh"
sonuc olsun parser.ozetle("yazdır \"Merhaba\"\n")
yazdır parser.hata_var_mi(sonuc)
yazdır parser.komut_satir_araligi(sonuc.komutlar[0]).satir_sayisi
yazdır parser.ifade_satir_araligi(sonuc.komutlar[0].ifade_ozeti).satir_sayisi
yazdır uzunluk(parser.tum_ifade_satir_araliklari(sonuc))
yazdır parser.ifade_agaci_ozeti(sonuc)
yazdır uzunluk(parser.tum_komut_satir_araliklari(sonuc))
yazdır parser.komut_agaci_ozeti(sonuc)
yazdır parser.ir_dogrula(sonuc)
yazdır parser.ir_ozeti(sonuc)
yazdır parser.ir_indeksi(sonuc)
yazdır parser.hata_tanilari(sonuc)
```

`ozetle(kaynak)` first builds and validates an `orhun-lexer-ir-v1` summary,
then passes its token stream to the parser. `ozetle_lexer_sonucu(lexer_sonucu)`
exposes that checked boundary for bootstrap tools and tests; incompatible or
malformed lexer IR becomes a normal Turkish parser error result.

The current prototype exposes a `Program` root and `Block` structural nodes,
and every success or error result carries the versioned
`ir_sozlesmesi: "orhun-parser-ir-v2"` boundary plus `lexer_ir_sozlesmesi` and
`lexer_ir_gecerli` provenance. Successful results require validated
`orhun-lexer-ir-v1` input. `ir_uyumlu_mu` checks the parser contract without
throwing on missing fields. `ir_dogrula` recursively checks program counts,
ordered command kinds, lexer provenance, command/expression links, blocks,
anonymous defaults, and parallel bodies with a 256-level depth limit;
`ir_gecerli_mi` is its boolean shorthand. `ir_ozeti` exposes the contract,
validation state, parse status, top-level count, and expression/command tree
metrics. The Orhun-written compiler runs this structural validation and
rejects malformed or unknown parser IR before compiling commands. The
prototype then summarizes command node kinds,
line numbers, primary expression summaries (`tur`, `satir`, `op`, `ayrinti`,
`alt_sayisi`, `altlar`), recursive expression children, assignment metadata,
total child-block counts, child block line numbers and command counts,
recursive child block command summaries, result command kinds, and
command/error and token counts. Helper functions can derive inclusive command
and expression line ranges (`baslangic_satir`, `bitis_satir`, `satir_sayisi`).
`tum_ifade_satir_araliklari` walks assignment targets, named and anonymous
function defaults, expression children, nested command blocks, and
`paralel yap` commands; its entries also carry the expression `tur`. Assignment
targets precede assigned values, named defaults precede body commands, and
anonymous defaults precede body expressions. Recursive command ranges walk
nested blocks and expression-contained `paralel yap` bodies; every entry also
carries the command `tur`. These helpers operate on the structural summary
without rewriting its command or expression nodes. `ifade_sayisi`, `ifade_turleri`,
`ifade_turu_sayisi`, and `ifade_turu_var_mi` expose query-friendly metrics.
`ifade_derinligi` measures one expression tree, while
`tum_ifade_derinligi` and `ifade_agaci_ozeti` report the maximum depth across
the complete parse result. The corresponding `komut_sayisi`, `komut_turleri`,
`komut_turu_sayisi`, `komut_turu_var_mi`, `komut_derinligi`,
`tum_komut_derinligi`, and `komut_agaci_ozeti` helpers expose the same metrics
for the recursive command tree, including parallel bodies.
`ifade_tur_sayilari` and `komut_tur_sayilari` return type-count dictionaries;
`ifade_turu_araliklari` and `komut_turu_araliklari` filter recursive source
ranges by type. `ir_indeksi` combines validation state, both type-count maps,
and both ordered range lists into an opt-in source index for linters, editors,
and compiler passes. Parse failures can
also be exposed as diagnostic dictionaries through `hata_tanisi` and
`hata_tanilari`, using the same `kod`, `mesaj`, `satir`, `sutun`, `uzunluk`,
`seviye`, and `ipucu` fields as the language-development helpers. The
structural summary is compared against the C++ parser AST through
`tests/parser_prototype_smoke.py`. Current coverage includes 174 successful AST
fixtures and 63 parser error fixtures. Command metadata covers declaration
assignment forms, assignment targets, multiple-assignment targets/counts,
function/class/external-function headers, class parent presence,
parameter/default counts, external-function type counts, includes,
and try/catch error variables. Control-flow metadata covers `eğer`/`sürece`
condition summaries, `tekrarla` count summaries, and `her ... içinde ...`
loop variable/source summaries. Expression metadata covers
anonymous function parameter/default counts, parameters/defaults,
inline anonymous function body summaries,
list-comprehension variables and condition presence, list/dictionary item
counts, dictionary literal keys, slice-bound presence, and `paralel yap` body
command counts. Error parity covers missing `ise`,
missing `kez`, missing control-flow conditions/counts,
missing assignment/return expression operands, required header names/colons,
malformed external-function, `deneme/yakala`, anonymous-function, `yeni`,
postfix, safe-access, collection/list-comprehension, and `paralel yap`
expressions, unknown command typos such as `yzdır 1`, and non-trailing required
parameters after default values. Those error fixtures also compare the reported line, expected-token
hint, unknown command name, and typo suggestion against the C++ parser. It is
not yet the production parser. Parser result helpers expose command kinds,
error presence, and the current error message.

## Orhun-Source Compiler Prototype

`orhun/derleyici.oh` is the first Orhun-written bytecode compiler prototype.
It consumes the structural IR from `orhun/parser.oh` and emits the same decoded
bytecode shape exposed by C++ `baytkod --json`.

Successful decoded bytecode objects carry the versioned
`ir_sozlesmesi: "orhun-bytecode-ir-v1"` boundary in both compiler paths. The
Orhun-written compiler result also carries `parser_ir_sozlesmesi`,
`parser_ir_gecerli`, and `ir_dogrulamasi`. Its pure-Orhun
`bytecode_ir_dogrula` helper checks parser provenance, result state, opcode
membership, U16 operands, exact instruction positions and widths, constants,
function/local-name metadata, counts, and terminal `OP_BOS` / `OP_DON`
instructions before the C++ bootstrap bridge consumes the result.

The initial supported subset contains number, string, and boolean constants,
global identifier reads and assignments, basic binary and unary operations,
list and dictionary literals, simple global function calls, index access,
field and safe-field reads, `eğer/değilse`, basic `sürece` loops, `her ... içinde ...`
loops, and `yazdır`. Counted `tekrarla ... kez` loops are also covered by
compiler parity.
Functions with required/default parameters and local assignments, explicit/implicit
returns, and function-creation/local-name metadata are covered by the initial
function subset. Nested named functions and returned functions are also covered.
Direct literal number, string, boolean, and unary expressions follow the C++
compiler's initial constant-folding rules.
Constant-truthiness branches and loops follow the C++ compiler's initial
dead-code elimination behavior.
Field/index assignments, slice reads, and global/local multiple assignments are
covered by compiler parity.
Dotted module/function calls and expression/command forms of `dahil_et` are
covered by compiler parity.
`deneme/yakala` control flow and global/local caught-error bindings are covered
by compiler parity.
`yeni` object construction and expression/command forms of `sor` are covered by
compiler parity.
Nested loop contexts and `kır`/`devam` jump patching are covered by compiler
parity.
Anonymous functions and nested named functions are covered by compiler parity,
including default arguments, deterministic `__anonim_islev_N` metadata names,
and captured outer-local reads/writes through the same name-based bytecode and
VM capture-cell contract used by the C++ compiler.
Filtered and unfiltered list comprehensions are covered by compiler parity,
including deterministic temporary names, the unfiltered reserve optimization,
and function-local temporary metadata.
External function declarations are covered by compiler parity and lower to the
existing `ffi_dis_islev_tanimla` policy surface with their library, return type,
and parameter type list.
Classes containing field declarations, methods, and inheritance setup are
covered by compiler parity. Method metadata includes `benim`/`üst` context
arguments and default-parameter local offsets; field reads/writes and super
method calls are also covered.
Interpolated strings, escaped braces, and constant truthiness folding are
covered by compiler parity.
`paralel yap` expressions are covered by compiler parity. The Orhun parser IR
exposes their structural `paralel_komutlar`, which the compiler lowers to the
same task-plan dictionaries and `gorev.baslat_plan` call as the C++ compiler.
`tests/compiler_prototype_smoke.py` compares opcode names, instruction pointers,
source lines, operands, constant-pool entries, and aggregate counts against the
C++ compiler. It includes focused generated programs plus larger checked-in
closure, OOP, default-method, and list-comprehension fixtures. Unsupported
constructs return an explicit error instead of silently emitting incorrect
bytecode. It is not yet the production compiler.

## CLI Contract

Important commands:

```bash
orhun dosya.oh
orhun yorumla dosya.oh
orhun vm-kati dosya.oh
orhun doctor
orhun doctor --json
orhun fmt dosya.oh
orhun lint dosya.oh
orhun lex dosya.oh --json
orhun parse dosya.oh --json
orhun baytkod dosya.oh --json
orhun hiz dosya.oh --json
orhun lsp --stdio
```

The LSP completion provider returns language keywords plus common built-in
functions and modules such as `yaz`, `oku`, `aralik`, `ilk`, `son`, `json`,
`dosya`, and Orhun-source helpers such as `numaralandir`, `eslestir`,
`token_araligi`, `ifade_satir_araligi`, `tum_ifade_satir_araliklari`,
`ifade_agaci_ozeti`, `komut_satir_araligi`,
`tum_komut_satir_araliklari`, `komut_agaci_ozeti`, `ir_uyumlu_mu`,
`ir_dogrula`, `ir_gecerli_mi`, `ir_ozeti`, `ir_indeksi`, `hata_tanilari`, and
`tani_listesi_bicimlendir`, `tani_listesi_ozeti`, plus AST helpers such as
`dugum_turu_var_mi` and `dugum_ozeti`.
Signature help also includes common built-in and Orhun-source helper
signatures, including `aralik([baslangic], bitis, [adim])` and
`numaralandir(liste, [baslangic])`, plus the lexer/parser/diagnostic helper
signatures documented above.
Hover uses the same signature table for known built-in and Orhun-source helper
functions when the symbol is not a local definition.
Workspace file URIs use UTF-8 percent encoding for reserved and non-ASCII path
bytes. On Windows, indexed workspace files are reported with long paths rather
than legacy 8.3 short paths, and UNC paths retain their file-URI authority.

Stable channel defaults:

- VM fallback is off.
- Shell command execution is restricted.
- FFI defaults to allowlist policy.
- Package sources are allowlist-checked.
- `doctor --json` reports `version`, `build`, `commit`, `channel`, `layout`,
  `executable`, `sibling_stdlib_path`, `fallback_default`, `fallback_source`,
  `ci_profiles`, `security_mode`, `checks`, and `status`. A healthy source
  checkout reports `layout: "source_checkout"`; a healthy portable runtime
  with a sibling `StdLib` reports `layout: "runtime_bundle"`. An incomplete
  standalone layout reports `status: "warning"` and exits with code `2`.
- `lex --json` exposes the C++ lexer token stream for self-hosting parity
  checks. Its JSON payload contains `dosya`, `hata_sayisi`, and `tokenlar`.
- `parse --json` exposes the C++ parser AST for self-hosting parity checks.
  Its JSON payload contains `dosya`, `durum`, `hata_sayisi`, and `ast`.
  The `ast` root is a `Program` node with nested command and expression nodes.
  `Atama` and `CokluAtama` nodes include `bildirim`: `true` for the `olsun`
  form and `false` for `=` compatibility assignment.
  Orhun's parser prototype parity also checks field names through `alan`,
  super access method names through `metod`, function-call names through `ad`,
  new-object class names through `sinif`, and argument counts through
  `arguman_sayisi`.
  Parser AST JSON fixtures live in `tests/ast_json/` and are checked through
  `tests/ast_json_smoke.py`.
- `orhun-lex <file.oh>` runs the Orhun-written lexer and emits a validated
  `orhun-lexer-ir-v1` JSON summary. It exits with status 1 for source lexer
  errors while keeping the emitted IR structurally valid.
- `orhun-parse <file.oh>` runs the checked Orhun-written lexer/parser chain and
  emits a validated `orhun-parser-ir-v2` JSON summary carrying lexer-contract
  provenance. Parser or lexer errors produce status 1 and a normal Turkish
  parser error result.
- Both Orhun frontend commands accept `--source`, `--obc-first`, and
  `--obc-only` module-loading policies.
- `baytkod --json` exposes the C++ compiler output as a decoded, machine-readable
  bytecode contract for self-hosting parity checks. Its successful payload
  identifies the inner object as `orhun-bytecode-ir-v1` and contains bytecode
  size, instruction and constant counts, decoded instructions, source lines,
  operands, and primitive constants. `OP_ISLEV_OLUSTUR`
  instructions also expose function name/constant, arity, entry IP, local count,
  context argument count, and local-name mappings. Compiler errors return exit
  code `1`, set `durum` to `fail`, and leave `bytecode` as `null`. The English
  `bytecode` command is a compatibility alias. This is an inspection and parity
  surface; it does not write build artifacts.
- `baytkod-yurut <dosya.json>` validates and executes the decoded bytecode
  contract through the C++ VM. It accepts the full successful compiler payload
  or its inner `bytecode` object. A present bytecode IR contract must be
  `orhun-bytecode-ir-v1`; contract-free legacy inputs remain readable. Unknown
  opcodes, missing fields, invalid operand widths, mismatched instruction
  positions/counts, and malformed function metadata are rejected before
  execution. `bytecode-run` is the English compatibility alias.
- `obc-dogrula <file.obc> [metadata.json]` validates the serialized OBC
  structure and its metadata contract without executing it. New
  `orhun-obc-v2` metadata records payload size, CRC32, and SHA-256.
  `orhun-obc-v1` metadata remains verifiable through size and CRC32.
  `obc-verify` is the English compatibility alias.
- Newly generated packaged executables use an `ORHNPKG2` trailer containing
  payload size, CRC32, and SHA-256. `paketli-dogrula <packaged-file>` validates
  the trailer and embedded OBC without executing it; `packaged-verify` is its
  English compatibility alias. Legacy `ORHNPKG1` packages remain readable.
- `orhun-vm <dosya.oh>` is the experimental single-command bootstrap path. It
  compiles the target through `orhun/derleyici.oh`, validates the decoded
  bytecode contract, and executes it through the C++ VM. `bootstrap-vm` is the
  English compatibility alias.
- `orhun-derle <dosya.oh> [cikti]` compiles through the Orhun-written compiler
  and writes the same `.obc`, packaged executable, and metadata artifacts as
  `derle`. `bootstrap-compile` is the English compatibility alias.
- The guarded bootstrap path can compile `StdLib/orhun/derleyici.oh` itself
  into an `.obc` artifact byte-identical to the C++ compiler output. This is a
  self-source bootstrap milestone, not yet a standalone compiler CLI.
- VM module loading defaults to `ORHUN_MODULE_MODE=source`. Explicit
  `obc-first` mode loads a sibling `.obc` module when available and otherwise
  falls back to source compilation. Explicit `obc-only` mode requires the
  corresponding `.obc`, does not require a sibling `.oh`, and rejects missing
  precompiled modules without C++ compiler fallback. The guarded bootstrap
  test runs the Orhun compiler/parser/lexer module chain source-free in
  `obc-only` mode.
- `orhun-vm` and `orhun-derle` accept `--source`, `--obc-first`,
  `--obc-only`, or `--modul-modu=<mode>` to select the policy for that process.
- `bootstrap-hazirla <directory>` writes source-free `lexer.obc`,
  `parser.obc`, `derleyici.obc`, and `derleyici_cli.obc` artifacts plus a
  size/CRC32/SHA-256-bearing `orhun-bootstrap-v2`
  `bootstrap.manifest.json`. `orhun-bootstrap-v1` manifests remain verifiable.
  `bootstrap-prepare` is its compatibility alias.
- `bootstrap-dogrula <toolchain-directory>` validates the manifest contract,
  exact module set, payload sizes, CRC32 values, and OBC structure without
  compiling or executing a target. `bootstrap-verify` is its compatibility
  alias. Bootstrap build and run commands perform the same validation first.
- `bootstrap-derle <toolchain-directory> <source.oh> [output]` consumes a
  prepared toolchain in strict `obc-only` mode without environment-variable
  setup. `bootstrap-build` is its compatibility alias.
- `bootstrap-calistir <toolchain-directory> <source.oh>` compiles and executes
  through the same prepared strict toolchain. `bootstrap-run` is its
  compatibility alias.
- `bootstrap-derleyici-paketle <toolchain-directory> <output-directory>`
  creates a source-free portable compiler bundle containing an
  `orhun-derleyici` executable and its sibling `StdLib` toolchain.
  `bootstrap-compiler-bundle` is its compatibility alias. The executable
  validates and activates the sibling strict toolchain automatically, then
  emits Orhun compiler bytecode JSON for the source path passed as its first
  program argument. `orhun-derleyici --derle <source.oh> [output]` uses the
  same Orhun-written compiler and the runtime serialization bridge to emit
  `.obc`, packaged executable, and metadata artifacts directly. Source/output
  argument parsing and the complete artifact output plan are produced by
  `orhun/derleyici_cli.oh`. Every invocation emits an
  `orhun-compiler-cli-v1` envelope containing the CLI implementation version,
  operation (`bytecode`, `artifact`, or `kullanim`), structured exit code, and
  a pure-Orhun `cli_dogrulamasi` record. The validator cross-checks operation,
  result state, bytecode IR provenance, artifact presence, and error state.
  Successful artifact operations contain the `.obc`, packaged executable,
  metadata paths, and metadata source name in an `orhun-artifact-plan-v1`
  plan. The C++ bootstrap runtime independently rejects unknown CLI or plan
  contracts, inconsistent result/exit/operation state, failed validation,
  empty fields, unexpected output suffixes, source names containing path
  separators, and colliding output paths before its OBC/package serialization
  bridge writes anything. Existing non-file targets are also rejected. Valid
  outputs are first written to unique sibling staging files;
  existing outputs are preserved and staged files are cleaned if any artifact
  cannot be produced. The packaged host does not dispatch individual
  compiler command names; it consumes the structured exit code and optional
  artifact plan returned by Orhun CLI bytecode. At startup it strictly
  validates the `orhun-bootstrap-compiler-bundle-v2` manifest, embedded CLI
  payload size/CRC32/SHA-256, and sibling toolchain path. V1 bundle manifests
  remain verifiable. Compiler-bundle identity does not depend on the executable
  filename, so a valid bundle executable may be renamed.
- `bootstrap-derleyici-dogrula <bundle-directory>` validates the complete
  portable compiler bundle without executing compiler CLI bytecode.
  `bootstrap-compiler-verify` is its compatibility alias.
- `bootstrap-yeniden-uret <seed-toolchain> <output-directory>` performs a
  reproducible three-stage bootstrap gate: the seed builds stage 2, stage 2
  builds stage 3, and every stage-2/stage-3 OBC artifact must be byte-identical.
  It refuses non-empty output directories and writes
  an `orhun-bootstrap-rebuild-v2` `bootstrap-rebuild.manifest.json` containing
  size, CRC32, and SHA-256 identity for every compiler module after success.
  `bootstrap-rebuild` is its compatibility alias.
- `bootstrap-yeniden-dogrula <toolchain-directory>` validates the rebuild-v2
  evidence and the companion strict toolchain without rebuilding it.
  `bootstrap-rebuild-verify` is its compatibility alias.

## Compatibility Rules

Until `1.0`, Orhun may change quickly, but changes should follow these rules:

- Turkish-first keywords and diagnostics stay central.
- Existing passing fixtures should remain valid unless there is a documented
  migration.
- Stable channel changes should be additive whenever possible.
- Safety defaults should not be weakened.
- Any behavior needed for self-hosting must be documented here before it is
  depended on by Orhun-written tooling.

## Closure Capture Status

Nested functions and anonymous functions are parsed and callable. The
interpreter (`orhun yorumla`), default runner, and `vm-kati` keep returned
closures' captured local variables alive. The promoted closure fixture is
`tests/cases/closure_missing_feature.oh`, guarded by
`tests/known_gap_smoke.py` and `tests/interpreter_closure_smoke.py`.

The intended capture model is documented in `docs/CLOSURE_CAPTURE_PLAN.md`.

Target closure semantics:

- Nested named functions and anonymous functions use lexical scope.
- A name declared as a parameter or local in the current function shadows outer
  bindings with the same name.
- A referenced name that is not local to the nested function is captured from
  the nearest enclosing function scope when such a binding exists.
- Closure construction captures only scopes visible to the defining function;
  locals belonging solely to a function farther down the dynamic call stack are
  never captured.
- Global bindings are not copied into closure environments; they remain global
  lookups.
- Captured locals live as long as any closure that references them.
- Multiple closures created during the same outer function call share the same
  mutable capture cell for each captured binding.
- Separate calls to the same outer function create separate capture cells.
- A new local binding created inside a loop iteration should have an independent
  capture cell for closures produced in that iteration.
- The interpreter and VM must agree before closure capture is considered part of
  the stable language contract.

## Self-Hosting Implications

This specification is the baseline for future Orhun-written components:

1. Standard library modules written in Orhun.
2. Lexer prototype written in Orhun.
3. Parser prototype written in Orhun.
4. Bytecode compiler written in Orhun.
5. Orhun compiler capable of compiling itself.

When implementation behavior and this document diverge, either the implementation
or the specification must be updated in the same development cycle.
