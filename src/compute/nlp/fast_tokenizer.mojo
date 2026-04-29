fn tokenize_fast(text: String) -> Tensor[Int32]:
    # Mojo fast string manipulation for BERTopic tokenizer pre-processing
    let words = text.split(" ")
    let tokens = Tensor[Int32](words.size)
    for i in range(words.size):
        tokens[i] = words[i].length() # Mock hash/id assignment
    return tokens
