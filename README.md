# tap-clickcast

`tap-clickcast` is a Singer tap for AppCast's Clickcast API.

Built with the Meltano [SDK](https://gitlab.com/meltano/sdk) for Singer Taps. More information about Clickcast API can be found at https://api.clickcast.cloud/clickcast/home#/

## Installation

```bash
pipx install tap-clickcast
```

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-clickcast --about
```

partner_token
: The Clickcast API Partner Token. This value is used to authenticate with the API by passing it to the header `X-Partner-Token`
api_url_base
: The Clickcast API base URL. Defaults to https://api.clickcast.cloud/clickcast/api

### Source Authentication and Authorization

You can generate a Partner Token at https://api.clickcast.cloud/clickcast/home#/tokens

## Usage

You can easily run `tap-clickcast` by itself or in a pipeline using [Meltano](www.meltano.com).

### Executing the Tap Directly

```bash
tap-clickcast --version
tap-clickcast --help
tap-clickcast --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_clickcast/tests` subfolder and
then run:

```bash
poetry run pytest
```

You can also test the `tap-clickcast` CLI interface directly using `poetry run`:

```bash
poetry run tap-clickcast --help
```

### Manual test run

Create a config file that contains a `partner_token` property, then run

```bash
poetry run tap-clickcast --config config.json
```

### Release new version

Workflows in the `.github` will create a new version number using Semantic Release.

Any commit that starts with `feat: ...` will create a new minor version (and any comment that starts with `fix: ...` will create a new minor version) when the commit is finally merged to main after a PR is approved and merged.

Then the new version is published to PyPI, available at [https://pypi.org/project/tap-clickcast/]().

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
cd tap-clickcast
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-clickcast --version
# OR run a test `elt` pipeline:
meltano elt tap-clickcast target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
