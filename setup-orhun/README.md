# setup-orhun

GitHub Action that installs a verified [Orhun](https://github.com/orhunlang/orhun)
toolchain from GitHub Releases and adds it to `PATH`.

## Usage

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: orhunlang/orhun/setup-orhun@v1.0.0
        with:
          version: "1.0.0"
      - run: orhun surum
      - run: orhun examples/merhaba.oh
```

## Inputs

| Name | Default | Description |
| --- | --- | --- |
| `version` | `1.0.0` | Orhun version tag without the leading `v` |
| `artifact` | `runtime` | `runtime` or `compiler` release archive |
| `token` | _(empty)_ | Optional GitHub token for API rate limits |
| `cache` | `true` | Reserved for archive caching |

## Outputs

| Name | Description |
| --- | --- |
| `orhun-path` | Absolute path to the installed executable |
| `version` | Installed version string |

## What it installs

Downloads `orhun-<artifact>-<version>-<os>-<arch>.tar.gz` from
`https://github.com/orhunlang/orhun/releases/download/v<version>/`,
verifies `SHA256SUMS` when published, extracts under `~/.local/share/orhun`,
and links `orhun` into `~/.local/bin`.

## Marketplace checklist

- [x] `action.yml` with `name`, `description`, `author`, `branding`
- [x] Composite `runs` steps with explicit `shell`
- [x] Documented inputs/outputs
- [x] Example workflow
- [x] LICENSE from repository root
- [ ] Publish via GitHub Marketplace submission form (maintainer action)

## Security

Release archives are checksum-verified when `SHA256SUMS` is present. Prefer
pinned tags (`@v1.0.0`) over `@main` in production workflows.
