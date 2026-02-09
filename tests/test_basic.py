"""Basic test to verify setup works"""


def test_imports() -> None:
    """Test that we can import our package"""
    import codeflow

    assert codeflow is not None


def test_environment() -> None:
    """Test Python version"""
    import sys

    assert sys.version_info >= (3, 11)
