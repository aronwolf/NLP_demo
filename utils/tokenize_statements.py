import nltk

def tokenize(text):    
    token_array = []               
    if (isinstance(text, unicode)) or (isinstance(text, str)):
        token_list = token_factory(text)
        token_string = str(token_list)
        token_array.append(token_string)
        return token_array
    else:
        for line in text:
            token_list = token_factory(line)
            token_string = str(token_list)
            token_array.append(token_string)
        return token_array

def token_factory(text_line):    
    index_word_map = []

    lemmatizer = nltk.stem.WordNetLemmatizer()
    tokens = nltk.pos_tag(nltk.tokenize.word_tokenize(text_line))
    for t in range(len(tokens)):
        if "V" in tokens[int(t)][1]:
            token = lemmatizer.lemmatize(tokens[int(t)][0], 'v')
        else:
            token = lemmatizer.lemmatize(tokens[int(t)][0])

        index_word_map.append(token)
    return index_word_map
