"""Tests standard tap features using the built-in SDK tests library."""

# import datetime
import pytest

from singer_sdk.testing import get_standard_tap_tests

from tap_krow.tap import TapKrow

SAMPLE_CONFIG = {"api_key": "test"}


# Run standard built-in tap tests from the SDK:
@pytest.mark.skip(
    reason="""This test is attempting to call the real API, and failing due to the API key.
https://meltano.slack.com/archives/C01PKLU5D1R/p1639061700310500"""
)
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapKrow, config=SAMPLE_CONFIG)
    for test in tests:
        print(test.__name__)
        test()
