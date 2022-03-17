#!/usr/bin/env python3
def main():
    import sys
    line = "to change and we're gonna quit like I'm I'm sorry So "
    allowable_phrase = ["feel like", "felt like",
                        "was like", " it's like", " it like",
                        "I'm like", "you're like", "You're like",
                        "He's like", "he's like",
                        "She's like", "she's like"]

    remove_words = [" Uh ", " uh ", " Uh, ", " uh, ",
                    " Um ", " um ", " Um, ", " um, "]

    for word in remove_words:
        if word in line:
            if "," in word:
                line = line.replace(word, ", ")
            else:
                line = line.replace(word, word[-1])


    delim = "like"
    print(line.split(delim))

    split = [phrase+delim for phrase in line.split(delim) if phrase]
    if line.split(delim)[-1] != '':
        split[-1] = split[-1].replace("like","")

    result = []
    print(split)
    for chunk in split:
        check_allowed = [a for a in allowable_phrase if a in chunk]
        if len(check_allowed) == 0:
            chunk = chunk.replace(" like","")
        result += chunk

    separator = ""
    final = separator.join(result)
    if final:
        if final[0] == " " and len(final)>1:
            final = final[1:]
        final = final[0].capitalize() + final[1:]

    if " so" in final[-4:] or " So" in final[-4:]:
        final = final[:-4] + final[-4:].replace("so","").replace("So","")
    print("\nFinal Result:")
    print(final)

if __name__ == '__main__':
    main()
