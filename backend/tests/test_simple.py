"""
Simple tests to verify pytest setup
"""

import pytest
from app.main import app


def test_app_exists():
    """Test that the FastAPI app exists and has correct metadata"""
    assert app is not None
    assert app.title == "Talent Casting System API"
    assert app.version == "1.0.0"


def test_basic_python_functionality():
    """Test basic Python functionality to ensure test environment works"""
    assert 1 + 1 == 2
    assert "hello" + " " + "world" == "hello world"

    # Test list comprehension
    squares = [x**2 for x in range(5)]
    assert squares == [0, 1, 4, 9, 16]


@pytest.mark.asyncio
async def test_async_functionality():
    """Test async/await functionality"""
    async def async_add(a, b):
        return a + b

    result = await async_add(3, 4)
    assert result == 7


class TestMathOperations:
    """Test class to verify class-based test organization"""

    def test_addition(self):
        assert 5 + 3 == 8

    def test_multiplication(self):
        assert 4 * 6 == 24

    @pytest.mark.parametrize("input_val,expected", [
        (2, 4),
        (3, 9),
        (4, 16),
        (5, 25)
    ])
    def test_square_parameterized(self, input_val, expected):
        """Test parameterized test functionality"""
        assert input_val ** 2 == expected