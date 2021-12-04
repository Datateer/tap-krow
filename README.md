# tap-krow

`tap-krow` is a Singer tap for the KROW API.

Built with the Meltano [SDK](https://gitlab.com/meltano/sdk) for Singer Taps.

Entity relationship diagram is available at https://dbdiagram.io/d/60b954d1b29a09603d17e3b3

## Installation

```bash
pipx install tap-krow
```

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-krow --about
```

api_key
: The KROW API key. This value is used to authenticate with the API by passing it to the header `Authentication: Bearer <api_key>`
api_url_base
: The KROW API base URL. Defaults to https://industry-staging.herokuapp.com/v1

### Source Authentication and Authorization

You can get an API key by contacting KROW

## Usage

You can easily run `tap-krow` by itself or in a pipeline using [Meltano](www.meltano.com).

### Executing the Tap Directly

```bash
tap-krow --version
tap-krow --help
tap-krow --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_krow/tests` subfolder and
then run:

```bash
poetry run pytest
```

You can also test the `tap-krow` CLI interface directly using `poetry run`:

```bash
poetry run tap-krow --help
```

### Manual test run

Create a config file that contains a `api_key` property, then run

```bash
poetry run tap-krow --config config.json
```

### Release new version

Workflows in the `.github` will create a new version number using Semantic Release.

Any commit that starts with `feat: ...` will create a new minor version (and any comment that starts with `fix: ...` will create a new minor version) when the commit is finally merged to main after a PR is approved and merged.

Then the new version is published to PyPI, available at [https://pypi.org/project/tap-krow/]().

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-krow
meltano install
```

Create a file `.env` with the contents:

```
export TAP_KROW_API_KEY=<api_key value here>
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-krow --version
# OR run a test `elt` pipeline:
meltano elt tap-krow target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
