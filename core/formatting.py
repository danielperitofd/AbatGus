from decimal import Decimal, InvalidOperation


LANGUAGE_FORMATS = {
    "pt-br": {"thousand": ".", "decimal": ","},
    "es": {"thousand": ".", "decimal": ","},
    "en": {"thousand": ",", "decimal": "."},
}

CURRENCY_FORMATS = {
    "BRL": {"symbol": "R$", "placement": "prefix", "locale": "pt-br"},
    "USD": {"symbol": "US$", "placement": "prefix", "locale": "en"},
    "EUR": {"symbol": "EUR", "placement": "prefix", "locale": "pt-br"},
}

MONTH_NAMES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Marco",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

UNIT_LABELS = {
    "UNIT": "Unidade",
    "KG": "kg",
    "LITER": "l",
    "SERVICE": "Servico",
}


def to_decimal(value):
    if value in (None, ""):
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def format_number(value, decimal_places=2, language_code="pt-br"):
    decimal_value = to_decimal(value).quantize(Decimal("1").scaleb(-decimal_places))
    locale_format = LANGUAGE_FORMATS.get((language_code or "pt-br").lower(), LANGUAGE_FORMATS["pt-br"])
    rendered = f"{decimal_value:,.{decimal_places}f}"
    rendered = rendered.replace(",", "TMP").replace(".", locale_format["decimal"]).replace("TMP", locale_format["thousand"])
    return rendered


def format_currency(value, currency_code="BRL", language_code="pt-br"):
    currency = CURRENCY_FORMATS.get(currency_code or "BRL", CURRENCY_FORMATS["BRL"])
    rendered = format_number(value, 2, currency.get("locale") or language_code)
    if currency["placement"] == "prefix":
        return f'{currency["symbol"]} {rendered}'
    return f'{rendered} {currency["symbol"]}'


def format_measure(value, unit, language_code="pt-br"):
    rendered = format_number(value, 2, language_code)
    return f"{rendered} {unit}"


def month_label(month):
    try:
        return MONTH_NAMES.get(int(month), str(month))
    except (TypeError, ValueError):
        return str(month or "-")


def week_label(week_number):
    try:
        return f"Semana {int(week_number)}"
    except (TypeError, ValueError):
        return str(week_number or "-")


def unit_label(unit_code):
    return UNIT_LABELS.get(str(unit_code or "").upper(), str(unit_code or "-"))
