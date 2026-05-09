# Список нецензурных слов (основные)
BAD_WORDS = [
    # Русские
    "блядь", "блять", "бля", "пизда", "пиздец", "пизд", "хуй", "хуйня", "хуета",
    "ёбаный", "ебаный", "ебать", "еблан", "ёблан", "ёб", "еб", "пиздить",
    "сука", "суки", "сучка", "залупа", "мудак", "мудила", "мудаки",
    "блядина", "шлюха", "шлюхи", "пиздюк", "пиздюки", "хуйло",
    "манда", "ёбнутый", "ёбнуть", "выёбываться", "разъёб",
    "ёбать", "наёбывать", "уёбок", "пиздобол", "хуесос",
    "долбоёб", "долбоеб", "пидор", "пидорас", "пидр",
    "залупа", "ёбаный", "бляха", "сблядовать",
    # Английские
    "fuck", "fucker", "fucking", "fucked", "fucks",
    "shit", "bitch", "asshole", "bastard", "cunt",
    "dick", "cock", "pussy", "whore", "slut",
    "nigger", "nigga", "faggot", "retard",
    "motherfucker", "bullshit", "jackass", "prick",
    "ass", "dumbass", "dipshit", "shithead",
]

def contains_bad_words(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    for word in BAD_WORDS:
        if word in text_lower:
            return True
    return False
