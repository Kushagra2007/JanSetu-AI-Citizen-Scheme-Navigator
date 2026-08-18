from nlp_engine import _follow_up, detect_intent, extract_entities, process_message


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


def test_extract_income_with_indian_number_format():
    entities = extract_entities("My annual family income is ₹2,00,000")
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


def test_incomplete_profile_requests_only_missing_fields():
    result = process_message("I am 25 years old and earn 2 lakh", profile_ctx={})
    assert result["missing_profile_fields"] == ["gender", "state", "category", "occupation", "education", "marital_status"]
    assert "state/UT" in result["response"]
    assert result["navigation"] is None


def test_service_catalogue_entity_is_recognised():
    result = process_message("How can I get an income certificate?")
    assert result["intent"] == "ask_service"
    assert result["entities"]["service_mentioned"] == "Income Certificate"


def test_student_scholarship_opens_scholarship_navigation():
    complete_profile = {"age": 20, "gender": "Female", "income": 200000, "state": "Bihar", "category": "OBC", "occupation": "student", "education": "12th", "marital_status": "Unmarried"}
    result = process_message("I need a student scholarship", profile_ctx=complete_profile)
    assert result["entities"]["scheme_category"] == "Scholarship"
    assert result["navigation"]["type"] == "scheme"


def test_last_required_detail_triggers_schemes_only_after_profile_is_complete():
    partial_profile = {"age": 20, "gender": "Female", "income": 200000, "state": "Bihar", "category": "OBC", "occupation": "student", "education": "12th"}
    result = process_message("I am unmarried", profile_ctx=partial_profile)
    assert result["missing_profile_fields"] == []
    assert result["navigation"]["type"] == "scheme"


def test_hindi_follow_up_requires_the_remaining_profile_details():
    profile = {"age": 25}
    assert "परिवार की वार्षिक आय" in _follow_up(profile, language="hi")


def test_hindi_scheme_reply_is_returned_in_hindi():
    result = process_message("मुझे योजना चाहिए", language="hi")
    assert "योजनाएँ" in result["response"]
