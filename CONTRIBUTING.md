# Contributing

Open a pull request for changes to the Action. Run `prek run --all-files` before pushing changes.

## Release notes

Add a Markdown file under `changelog.d` for a change Action users should know about. Name it `+topic.feature.md`,
`+topic.change.md`, `+topic.bugfix.md`, or `+topic.doc.md`. Other supported categories are `breaking`, `security`,
`performance`, `deprecation`, `removal`, and `packaging`. One pull request can have several fragments. Describe the
change from the user's point of view; do not add a fragment for CI or dependency maintenance alone.

Do not write credits into a fragment. The release tooling links a named fragment to its squash-merged pull request and
credits the authors and `Co-authored-by` co-authors of that commit. You do not need a pull request number when creating
the file. If the pull request has no user-facing change, apply the `skip news` label; the required news check reruns
when the label changes. Automation pull requests without a fragment get that label automatically. A bot pull request
that supplies a fragment still has it validated.

## Releases

Maintainers dispatch **Prepare release** on `main` and choose `auto`, `major`, `minor`, or `patch`. `auto` uses the
pending fragment categories. The workflow calculates a `v`-prefixed tag, builds the changelog, runs
`release-creator contributors` to list first-time contributors from the commit authors and co-authors, runs `prek`, and
validates the patch before a repository-scoped GitHub App pushes the release commit and tag. The tag workflow creates a
GitHub Release from the tagged changelog and advances the floating `v1` and `v1.0` tags when appropriate.

## Tests

Add a test for every new feature and bug fix. A change without a test needs a reason in the pull request description.

The tests are the self-test jobs of the CI workflow in `.github/workflows/main.yml`. Each job runs the Action from the
pull request in a different setup: a directory with a Python project, a directory without one, and a runner where uv is
already installed. Cover a new input or code path with a new job or a new step in an existing one. The jobs run on every
pull request and on pushes to `main` and to branches named `test-me-*`.
