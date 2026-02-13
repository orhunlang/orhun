# Orhun VS Code Desteği

Bu klasör, Orhun (`.oh`) dosyaları için temel VS Code dil desteğini içerir:

- Sözdizimi renklendirme (`syntaxes/orhun.tmLanguage.json`)
- Dil davranışları (`language-configuration.json`)
- Snippet seti (`snippets/orhun.code-snippets`)

## Yerel Kurulum

1. VS Code eklenti klasörüne kopyalayın:
   - Windows: `%USERPROFILE%\\.vscode\\extensions\\orhun-language`
2. VS Code'u yeniden başlatın.

Alternatif olarak bu klasörü bir `.vsix` paketine dönüştürmek için `vsce` kullanabilirsiniz.

## Kapsam

Bu sürüm MVP düzeyindedir:

- Anahtar kelime renklendirme
- String/interpolasyon (`{degisken}`) vurgusu
- Blok/döngü/snippet şablonları

LSP (otomatik tamamlama, tanıma gitme, canlı diagnostics) sonraki aşamadır.
