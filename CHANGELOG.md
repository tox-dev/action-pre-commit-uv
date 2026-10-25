# Changelog

<!-- towncrier release notes start -->

<a name="release-v1-1-0"></a>

## v1.1.0 (2026-10-10)

<a name="release-v1-1-0-added"></a>

### Added

- Run pre-commit with Python 3.15 in project and isolated tool environments
  ([#38](https://github.com/tox-dev/action-pre-commit-uv/pull/38)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-v1-0-5"></a>

## v1.0.5 (2026-07-21)

<a name="release-v1-0-5-added"></a>

### Added

- Keep the `v1` and `v1.0` tags pointed at the latest stable release
  ([#29](https://github.com/tox-dev/action-pre-commit-uv/pull/29),
  [#30](https://github.com/tox-dev/action-pre-commit-uv/pull/30)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-v1-0-4"></a>

## v1.0.4 (2026-05-27)

<a name="release-v1-0-4-added"></a>

### Added

- Add the `uv-install` input and select `uvx` when the checkout has no project
  ([#24](https://github.com/tox-dev/action-pre-commit-uv/pull/24)) by [@gaborbernat](https://github.com/gaborbernat).

<a name="release-v1-0-4-fixed"></a>

### Fixed

- Skip installing uv when it is already available ([#23](https://github.com/tox-dev/action-pre-commit-uv/pull/23)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-1-0-3"></a>

## 1.0.3 (2025-08-25)

<a name="release-1-0-3-changes"></a>

### Changes

- Publish the action under a unique GitHub Marketplace name
  ([#8](https://github.com/tox-dev/action-pre-commit-uv/pull/8)) by [@hugovk](https://github.com/hugovk).

<a name="release-v1-0-2"></a>

## v1.0.2 (2025-01-26)

<a name="release-v1-0-2-changes"></a>

### Changes

- Pass `--no-sync` to `uv run` ([#4](https://github.com/tox-dev/action-pre-commit-uv/pull/4)) by
  [@zeevro](https://github.com/zeevro).

<a name="release-v1-0-1"></a>

## v1.0.1 (2024-10-23)

<a name="release-v1-0-1-changes"></a>

### Changes

- Set up uv with `astral-sh/setup-uv` ([#2](https://github.com/tox-dev/action-pre-commit-uv/pull/2)) by
  [@hugovk](https://github.com/hugovk).

<a name="release-v1-0-1-added"></a>

### Added

- Cache pre-commit environments ([#3](https://github.com/tox-dev/action-pre-commit-uv/pull/3)) by
  [@gaborbernat](https://github.com/gaborbernat).

<a name="release-v1-0-0"></a>

## v1.0.0 (2024-10-23)

<a name="release-v1-0-0-added"></a>

### Added

- Run pre-commit through pre-commit-uv.
