import re


splitter = re.compile('([.!?] *)')
placeholder = re.compile('{(.+?)}')
vowel = re.compile('^([aeiou])')


def capitalize(text: str):
    split = splitter.split(text)
    final_story = []
    for sentence in split:
        if len(sentence) < 2:
            final_story.append(sentence)
        else:
            final_story.append(sentence[0].upper() + sentence[1:])
    return ''.join(final_story)
