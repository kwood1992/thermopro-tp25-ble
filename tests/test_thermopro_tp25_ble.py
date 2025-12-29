# content of test_hello.py

def test_hello_world():
    # Define a simple greeting
    greeting = "hello world"
    
    # Use a standard Python assert statement to check for expected content
    assert "hello" in greeting
    assert "world" in greeting
    assert "goodbye" not in greeting
