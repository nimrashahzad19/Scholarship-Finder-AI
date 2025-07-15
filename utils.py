# utils.py

def clean_text(text):
    return text.strip().replace("\n", " ")

def try_parse_number(s):
    try:
        return int(s.replace(",", ""))
    except:
        return None
