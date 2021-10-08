from string import digits
import re
from datetime import datetime


regex = re.compile('[-@_!#$%^&*()<>?/}{~:]')
deposit_imp_keywords = ["Bank", "LTD", "LIC", "HDFC"]


def removeSpecialCharacters(value):
    return re.sub(r"[^a-zA-Z]+", " ", value)


def removeNumbers(value):
    remove_digits = str.maketrans('', '', digits)
    return value.translate(remove_digits)


def extractSpecialWords(value):
    newValue = []
    if "/" in value:
        words = value.strip().split("/")
        for word in words:
            if len(word) > 0 and str(word)[0].isupper() and str(word).replace(" ", "").isalpha() and regex.search(
                    word) is None:
                newValue.append(word)
    else:
        words = value.strip().split(" ")
        for word in words:
            if str(word)[0].isupper() and str(word).isalpha():
                newValue.append(word)
    return " ".join(newValue)


def getTime(str_time):
    try:
        if 'T' in str_time:
            str_time = datetime.strptime(str_time.split("T")[0], "%Y-%m-%d").date()
        elif '-' in str_time:
            str_time = datetime.strptime(str_time, "%Y-%m-%d").date()
        else:
            str_time = None
    except Exception as e:
        str_time = None
    return str_time