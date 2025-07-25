def sevenseg(n: str | int) -> str:
    return "".join({
        "0": "🯰", "1": "🯱", "2": "🯲", "3": "🯳", "4": "🯴",
        "5": "🯵", "6": "🯶", "7": "🯷", "8": "🯸", "9": "🯹"
    }.get(c, c) for c in str(n))