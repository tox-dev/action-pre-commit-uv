[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/tox-dev/action-pre-commit-uv/main.svg)](https://results.pre-commit.ci/latest/github/tox-dev/action-pre-commit-uv/main)
[![Build Status](https://github.com/tox-dev/action-pre-commit-uv/actions/workflows/main.yml/badge.svg)](https://github.com/tox-dev/action-pre-commit-uv/actions)

# tox-dev/action-pre-commit-uv

A GitHub action to run [pre-commit](https://pre-commit.com) using
[pre-commit-uv](https://github.com/tox-dev/pre-commit-uv).

### using this action

To use this action, make a file `.github/workflows/pre-commit.yml`. Here's a template to get started:

```yaml
name: pre-commit

on:
  pull_request:
  push:
    branches: [main]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: tox-dev/action-pre-commit-uv@v1
```

This does a few things:

- clones the code
- installs uv (if not already available)
- sets up the `pre-commit` cache

The action auto-detects the right invocation: if a `pyproject.toml` exists it uses `uv run`, otherwise it uses `uvx` for
isolated tool execution.

### controlling uv installation

By default (`uv-install: 'auto'`), the action detects whether uv is already available and only installs it if needed.
You can override this with `'true'` (always install) or `'false'` (never install):

```yaml
  - uses: astral-sh/setup-uv@v7
    with:
      version: 0.6.0
  - uses: tox-dev/action-pre-commit-uv@v1
    with:
      uv-install: 'false'
```

### using this action with custom invocations

By default, this action runs all the hooks against all the files. `extra_args` lets users specify a single hook id
and/or options to pass to `pre-commit run`.

Here's a sample step configuration that only runs the `flake8` hook against all the files (use the template above except
for the `pre-commit` action):

```yaml
  - uses: tox-dev/action-pre-commit-uv@v1
    with:
      extra_args: flake8 --all-files
```

### using this action in private repositories

prior to v3.0.0, this action had custom behaviour which pushed changes back to the pull request when supplied with a
`token`.

this behaviour was removed:

- it required a PAT (didn't work with short-lived `GITHUB_TOKEN`)
- properly hiding this `input` from the installation and execution of hooks is intractable in github actions (it is
  readily available as `$INPUT_TOKEN`)
- this meant potentially unvetted code could access the token via the environment

you can _likely_ achieve the same thing with an external action such as [git-auto-commit-action] though you may want to
take precautions to clear `git` hooks or other ways that arbitrary code execution can occur when running `git commit` /
`git push` (for example [core.fsmonitor]).

while unrelated to this action, [pre-commit.ci] avoids these problems by installing and executing isolated from the
short-lived repository-scoped [installation access token].

[core.fsmonitor]: https://github.blog/2022-04-12-git-security-vulnerability-announced/
[git-auto-commit-action]: https://github.com/stefanzweifel/git-auto-commit-action
[installation access token]: https://docs.github.com/en/rest/apps/apps#create-an-installation-access-token-for-an-app
[pre-commit.ci]: https://pre-commit.ci
