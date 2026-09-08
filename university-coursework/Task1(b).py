def ends_with_ac_uk(string):
    """
    This function checks if the input string ends with the substring ".ac.uk".
    
    >>> ends_with_ac_uk("university.ac.uk")
    True
    >>> ends_with_ac_uk("icloud.com")
    False
    """
    return string.endswith(".ac.uk")

# Test cases
print(ends_with_ac_uk("university.ac.uk"))  # Expected: True
print(ends_with_ac_uk("example.com"))    # Expected: False
