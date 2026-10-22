# Orhun Language (VS Code)

Syntax highlighting and snippets for the [Orhun](https://github.com/orhunlang/orhun)
programming language (v1.0.1).

## Features

- `.oh` language id and TextMate grammar
- Turkish-first keywords (`eğer`, `işlev`, `olsun`, …)
- English keyword aliases (`if`, `function`, `print`, …) highlighted
- ASCII comparison operators `== != < > <= >=` and unary `!`
- Beginner snippets (`yaz`, `işlev`, `eğer`, `deneme`, …)

## Install

From Marketplace (when published), or package locally:

```bash
cd tools/vscode-orhun
npm run package
# or: npx --yes @vscode/vsce package --no-dependencies
code --install-extension orhun-language-1.0.0.vsix
```

## Notes

- Diagnostics / LSP use the `orhun lsp --stdio` binary from PATH when available.
- This extension ships highlighting only; runtime behavior is defined by
  `docs/SPEC.md` in the main repository.
