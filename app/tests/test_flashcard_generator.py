import pandas as pd
from io import StringIO
import sys
import os
import vcr
import pytest
from unittest.mock import patch

# Add the app directory to the path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.flashcard_generator import generate_flashcards, get_openai_client

# Configure VCR
my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/vcr_cassettes',
    record_mode='once',
    match_on=['uri', 'method'],
    filter_headers=['authorization'],
    filter_query_parameters=['api_key'],
    # Filter sensitive information from the request body
    before_record_request=lambda request: request,
    # Filter sensitive information from the response
    before_record_response=lambda response: response
)

@my_vcr.use_cassette('generate_flashcards_basic.yaml')
def test_generate_flashcards_returns_csv_string():
    """Test that the function returns a string in CSV format"""
    result = generate_flashcards("Create 3 flashcards about Python")
    assert isinstance(result, str)
    
    # Verify it can be parsed as CSV
    try:
        df = pd.read_csv(StringIO(result))
        assert 'front' in df.columns
        assert 'back' in df.columns
    except Exception as e:
        pytest.fail(f"Failed to parse CSV: {e}")

@my_vcr.use_cassette('generate_flashcards_count_3.yaml')
def test_generate_flashcards_correct_count():
    """Test that the function returns exactly three flashcards when requested"""
    result = generate_flashcards("Create 3 flashcards about Python")
    
    # Parse the CSV and check row count
    df = pd.read_csv(StringIO(result))
    assert len(df) == 3, "Expected exactly 3 flashcards to be generated"

@my_vcr.use_cassette('generate_flashcards_count_7.yaml')
def test_generate_flashcards_larger_count():
    """Test that the function returns the correct number of flashcards when requesting a larger count"""
    requested_count = 7
    result = generate_flashcards(f"Create {requested_count} flashcards about JavaScript")
    
    # Parse the CSV and check row count
    df = pd.read_csv(StringIO(result))
    assert len(df) == requested_count, f"Expected exactly {requested_count} flashcards to be generated"

@my_vcr.use_cassette('generate_flashcards_no_empty.yaml')
def test_generate_flashcards_no_empty_rows():
    """Test that the function doesn't return any flashcards with empty front or back sides"""
    result = generate_flashcards("Create 5 flashcards about Python")
    
    # Parse the CSV
    df = pd.read_csv(StringIO(result))
    
    # Check for empty values in 'front' column
    empty_fronts = df['front'].isna() | (df['front'] == '')
    assert not any(empty_fronts), "Found flashcards with empty front sides"
    
    # Check for empty values in 'back' column
    empty_backs = df['back'].isna() | (df['back'] == '')
    assert not any(empty_backs), "Found flashcards with empty back sides" 