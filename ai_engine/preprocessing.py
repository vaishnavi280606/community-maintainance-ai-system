import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

# Download required NLTK resources
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('stopwords')
    nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text: str) -> str:
    """
    Preprocess constraint text for NLP tasks.
    1. Lowercase
    2. Remove punctuation
    3. Remove extra whitespace
    4. Remove stopwords
    5. Lemmatize
    """
    if not isinstance(text, str):
        return ""
        
    # Lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove numbers (optional, but usually good for issue classification unless specific models are important)
    text = re.sub(r'\d+', '', text)
    
    # Tokenize and remove stopwords and Lemmatize
    tokens = text.split()
    cleaned_tokens = [
        lemmatizer.lemmatize(word) 
        for word in tokens 
        if word not in stop_words and len(word) > 1
    ]
    
    # Rejoin
    return ' '.join(cleaned_tokens)
