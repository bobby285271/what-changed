def print_trivial(txt: str, file: str):
    oup = open(file, 'a', encoding='utf-8')
    oup.write(txt[1:] + "\n")  # Ignore the first '@'.
    oup.close()
