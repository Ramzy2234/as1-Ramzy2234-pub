import re

# Function to count every single tokens within the text
def countTokens(text):
    # Tokenize the text using basic expressions to match words
    tokens = re.findall(r'\b\w+\b', text.lower())
    return len(tokens)

# Function to count the frequency of a specific token (case-insensitive)
def countToken(text, token):
    # Change text and token to lowercase and count occurrences of the token
    text = text.lower()
    token = token.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens.count(token)

# Function to calculate the normalized frequency of a particular token (case-insensitive)
def normalisedFrequency(text, token):
    # Tokenize the text and change it to lowercase
    tokens = re.findall(r'\b\w+\b', text.lower())
    total_tokens = len(tokens)
    token_count = tokens.count(token.lower())
    # Revert normalized frequency
    return token_count / total_tokens if total_tokens > 0 else 0

# Function to count the number of sentences within the text
def sentenceCount(text):
    # Break apart the text by sentence-ending punctuation (period, exclamation, or question mark)
    sentences = re.split(r'[.!?](?:\s|$)', text.strip())
    # Filter out empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)

# Function to get a list of sentences containing a particular token (case-insensitive)
def sentencesContaining(text, token):
    token = token.lower()
    # Split the text into sentences through period, exclamation, or question mark
    sentences = re.split(r'[.!?](?:\s|$)', text.strip())
    # Revert sentences including the token (case-insensitive)
    return [sentence.strip() for sentence in sentences if token in sentence.lower()]

# Main function to input the file
def processFile():
    # Get file name from the user
    filename = input("Enter the name of the text file: ").strip()

    try:
        # Open file and look at the content
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Show total number of tokens
        print(f"Total number of tokens: {countTokens(text)}")
        
        # Ask user for a token to search 
        token_to_search = input("Enter a token to search: ").strip()
        
        # Display frequency count for the token
        print(f"Frequency of '{token_to_search}': {countToken(text, token_to_search)}")
        
        # Display normalized frequency count for the token
        print(f"Normalized frequency of '{token_to_search}': {normalisedFrequency(text, token_to_search):.6f}")
        
        # Display number of sentences
        print(f"Number of sentences: {sentenceCount(text)}")
        
        # Show sentences containing the token
        sentences_with_token = sentencesContaining(text, token_to_search)
        if sentences_with_token:
            print(f"Sentences containing the token '{token_to_search}':")
            for sentence in sentences_with_token:
                print(f"- {sentence}")
        else:
            print(f"No sentences found containing the token '{token_to_search}'.")

    except FileNotFoundError:
        print(f"The file '{filename}' does not exist. Please check the file path and try again.")

# Run the program
if __name__ == "__main__":
    processFile()