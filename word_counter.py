import string

dictionary = dict()

with open("words.txt", "r", encoding="utf-8") as file:
    for line in file:
        words = line.split()

        for word in words:
            clean_word = word.strip(string.punctuation).lower()
            quantity = dictionary.setdefault(clean_word, 0)
            dictionary[clean_word] = quantity + 1

sorted_words = sorted(dictionary.items(), key=lambda item: item[1], reverse=True)

for word, count in sorted_words[:10]:
    print(f"Word: '{word}' --- Count: {count}")