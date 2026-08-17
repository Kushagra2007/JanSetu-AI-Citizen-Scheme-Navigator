from nlp_engine import detect_intent, extract_entities, process_message


def test_greeting_intent():
    intent, conf = detect_intent("Hello there")
    assert intent == "greeting"


def test_hindi_greeting():
    intent, conf = detect_intent("namaste")
    assert intent == "greeting"


def test_ask_scheme_intent():
    intent, _ = detect_intent("I want to know about yojana for farmers")
    assert intent == "ask_scheme"


def test_ask_service_intent():
    intent, _ = detect_intent("How do I get a PAN card")
    assert intent == "ask_service"


def test_extract_age_entity():
    entities = extract_entities("I am 25 years old")
    assert entities.get("age") == 25


def test_extract_income_lakh():
    entities = extract_entities("My income is 2 lakh per year")
    assert entities.get("income") == 200000.0


def test_extract_gender():
    entities = extract_entities("I am a female farmer")
    assert entities.get("gender") == "Female"
    assert entities.get("occupation") == "farmer"


def test_extract_category():
    entities = extract_entities("I belong to OBC category")
    assert entities.get("category") == "OBC"


def test_process_message_full():
    result = process_message("I am 30 years old farmer from Bihar with income 1 lakh", language="en")
    assert result["intent"] in ("provide_info", "ask_scheme")
    assert result["entities"]["age"] == 30
    assert result["entities"]["occupation"] == "farmer"
    assert result["entities"]["state"] == "Bihar"


def test_unknown_intent():
    intent, conf = detect_intent("asdkjaslkdj random text 123")
    assert intent == "unknown"