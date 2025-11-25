# sparv-sbx-wsd-rs

[![PyPI version](https://img.shields.io/pypi/v/sparv-sbx-wsd-rs.svg)](https://pypi.org/project/sparv-sbx-wsd-rs/)
[![PyPI license](https://img.shields.io/pypi/l/sparv-sbx-wsd-rs.svg)](https://pypi.org/project/sparv-sbx-wsd-rs/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sparv-sbx-wsd-rs.svg)](https://pypi.org/project/sparv-sbx-wsd-rs/)

[![Maturity badge - level 2](https://img.shields.io/badge/Maturity-Level%202%20--%20First%20Release-yellowgreen.svg)](https://github.com/spraakbanken/getting-started/blob/main/scorecard.md)
[![Stage](https://img.shields.io/pypi/status/sparv-sbx-wsd-rs.svg)](https://pypi.org/project/sparv-sbx-wsd-rs/)

[![CI(check)](https://github.com/spraakbanken/sparv-sbx-wsd-rs/actions/workflows/check.yml/badge.svg)](https://github.com/spraakbanken/sparv-sbx-wsd-rs/actions/workflows/check.yml)
[![CI(release)](https://github.com/spraakbanken/sparv-sbx-wsd-rs/actions/workflows/release.yml/badge.svg)](https://github.com/spraakbanken/sparv-sbx-wsd-rs/actions/workflows/release.yml)
[![CI(scheduled)](https://github.com/spraakbanken/sparv-sbx-wsd-rs/actions/workflows/rolling.yml/badge.svg)](https://github.com/spraakbanken/sparv-sbx-wsd-rs/actions/workflows/rolling.yml)
[![CI(test)](https://github.com/spraakbanken/sparv-sbx-wsd-rs/actions/workflows/test.yml/badge.svg)](https://github.com/spraakbanken/sparv-sbx-wsd-rs/actions/workflows/test.yml)

[sparv]: https://github.com/spraakbanken/sparv
[saldowsd-rs]: https://github.com/spraakbanken/saldowsd-rs
[saldowsd-pypi]: https://pypi.org/project/saldowsd

This plugin to [sparv] is a rewrite of the the internal module `wsd`, that use [saldowsd-rs] instead of `saldowsd.jar`.

The improvements to the internal module `wsd` are:

- Easier setup, the binary `saldowsd` is installed as a Python package from [PyPI][saldowsd-pypi], instead of manual install of `saldowsd.jar`.
- Faster analysis, `saldowsd-rs` is about 13% faster than `saldowsd.jar`.
- Uses less memory, `saldowsd-rs` uses about 35% less memory than `saldowsd.jar`.

## Faster than using `saldowsd.jar`

The running time for `sbx_wsd_rs` that uses `saldowsd-rs` is 12.8% faster than using Java version. See results from
running both annotations on `vivill` on our server `wombat`.

```bash
[username@wombat vivill]$ sparv run --stats

  Task                                                           Time taken   Percentage
  wsd:annotate                                                      0:11:25         1.3%
  sbx_wsd_rs:annotate                                               0:09:57         1.1%
```

## Memory usage

Loading models and running a simple example (not using Sparv for this). Rust version uses 35% less memory.
Measured with [`heaptrack`](https://github.com/KDE/heaptrack).

| Tool                  | Top-RSS |
| --------------------- | ------: |
| `saldowsd` (Rust)     |  914 Mb |
| `saldowsd.jar` (Java) |  1.4 Gb |

An example of the output from `Sparv` can be seen [here](./assets/small/bet-2018-2021-1-short_export.gold.xml).

The annotations are probalistic, so they always differ a bit (wsd.sense differs with itself for different runs).

Example of differences:

- anslag: `|anslag..1:0.993|anslag..2:0.004|anslag..3:0.004|` != `|anslag..1:0.992|anslag..3:0.004|anslag..2:0.004|`
- avvikelse: `|avvikelse..1:0.978|avvikelse..2:0.022|` != `|avvikelse..1:0.977|avvikelse..2:0.023|`
- utskottets: `|utskott..2:0.835|utskott..3:0.109|utskott..1:0.056|` != `|utskott..2:0.843|utskott..3:0.101|utskott..1:0.056|`
- särskilda: `|särskilja..1:0.587|särskild..1:0.413|` != `|särskilja..1:0.589|särskild..1:0.411|`

## Changelog

This project keeps a [changelog](./CHANGELOG.md).

## Minimum supported Python version

This library tries to support as many Python versions as possible.
When a Python version is added or dropped, this library's minor version is bumped.

- v0.1.0: Python 3.11

## License

This repository is licensed under the [MIT](./LICENSE) license.

## Development

### Development prerequisites

- [`uv`](https://docs.astral.sh/uv/)
- [`pre-commit`](https://pre-commit.org)

For starting to develop on this repository:

- Clone the repo `git clone https://github.com/spraakbanken/sparv-sbx-wsd-rs.git`
- Setup environment: `make dev`
- Install `pre-commit` hooks: `pre-commit install`

Do your work.

Tasks to do:

- Test the code with `make test` or `make test-w-coverage`.
- Test the examples with `make test-example-small`.
- Lint the code with `make lint`.
- Check formatting with `make check-fmt`.
- Format the code with `make fmt`.
- Type-check the code with `make type-check`.

This repo uses [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

### Release a new version

- Prepare the CHANGELOG: `make prepare-release` and then edit `CHANGELOG.md`.
- Add to git: `git add CHANGELOG.md`
- Commit with `git commit -m 'chore(release): prepare release'` or `cog commit chore 'prepare release' release`.
- Bump version (depends on [`bump-my-version](https://callowayproject.github.io/bump-my-version/))
  - install with `uv tool install bump-my-version`
  - Major: `make bumpversion part=major`
  - Minor: `make bumpversion part=minor`
  - Patch: `make bumpversion part=patch` or `make bumpversion`
- Push `main` and tags to GitHub: `git push main --tags` or `make publish`
  - GitHub Actions will build, test and publish the package to [PyPi](https://pypi.prg).
- Add metadata for [Språkbanken's resource](https://spraakbanken.gu.se/resurser)
  - Generate metadata: `make generate-metadata`
  - Upload the files from `examples/metadata/export/sbx_metadata/analysis` to <https://github.com/spraakbanken/metadata/tree/main/yaml/analysis>.
