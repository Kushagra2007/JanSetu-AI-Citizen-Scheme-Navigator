"""
Custom rule-based NLP engine for Hindi/English citizen-service chat.
No external APIs — pure regex + keyword matching.
"""
import re

STATES = [
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa",
    "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala",
    "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland",
    "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura",
    "uttar pradesh", "uttarakhand", "west bengal", "delhi", "up", "mp", "wb"
]

INTENT_KEYWORDS = {
    "greeting": ["hi", "hello", "hey", "namaste", "namaskar", "hii", "helo", "salaam"],
    "goodbye": ["bye", "goodbye", "alvida", "phir milenge", "tata"],
    "thanks": ["thanks", "thank you", "dhanyavad", "dhanyawad", "shukriya"],
    "ask_scheme": ["scheme", "yojana", "yojna", "scholarship", "subsidy", "benefit",
                   "sarkari yojana", "government scheme"],
    "ask_service": ["pan card", "passport", "aadhaar", "aadhar", "driving license",
                    "voter id", "ration card", "bank account", "banking", "service banwana"],
    "check_eligibility": ["eligible", "eligibility", "patrata", "qualify", "kya main"],
    "track_application": ["status", "track", "application status", "aavedan", "kaha tak pahuncha"],
    "document_query": ["document", "kagaz", "documents chahiye", "kya lagega"],
}

OCCUPATIONS = {
    "farmer": ["farmer", "kisan", "krishi", "agriculture"],
    "student": ["student", "chatra", "padhai", "college", "school"],
    "unemployed": ["unemployed", "berozgar", "no job", "jobless"],
    "business": ["business", "vyapari", "shopkeeper", "self employed", "vyapar"],
    "labourer": ["labour", "labourer", "mazdoor", "worker", "daily wage"],
    "employee": ["employee", "job", "naukri", "service class", "salaried"],
}

CATEGORY_KEYWORDS = {
    "SC": ["sc ", "scheduled caste", " sc"],
    "ST": ["st ", "scheduled tribe", " st"],
    "OBC": ["obc", "other backward"],
    "EWS": ["ews", "economically weaker"],
    "General": ["general category", "general caste"],
}

EDUCATION_KEYWORDS = {
    "below_10th": ["below 10th", "8th pass", "primary"],
    "10th": ["10th", "matric", "dasvi"],
    "12th": ["12th", "intermediate", "barhavi"],
    "graduate": ["graduate", "graduation", "bachelor", "b.a", "b.sc", "b.com", "btech", "b.tech"],
    "postgraduate": ["postgraduate", "masters", "m.a", "m.sc", "mtech", "phd"],
    "illiterate": ["illiterate", "anpadh", "no education"],
}


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def extract_entities(text: str) -> dict:
    t = _norm(text)
    entities = {}

    age_match = re.search(r"\b(\d{1,2})\s*(years|year|yrs|saal|yr)\b", t)
    if not age_match:
        age_match = re.search(r"\bage\s*(?:is|:)?\s*(\d{1,2})\b", t)
    if age_match:
        entities["age"] = int(age_match.group(1))

    income_match = re.search(r"(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|laakh)", t)
    if income_match:
        entities["income"] = float(income_match.group(1)) * 100000
    else:
        income_match2 = re.search(r"(?:income|salary|kamata|kamaata)\D{0,10}(\d{4,8})", t)
        if income_match2:
            entities["income"] = float(income_match2.group(1))

    if any(k in t for k in ["female", "mahila", "woman", "ladki", "aurat"]):
        entities["gender"] = "Female"
    elif any(k in t for k in ["male", "purush", "man ", "ladka", "aadmi"]):
        entities["gender"] = "Male"
    elif any(k in t for k in ["transgender", "third gender", "kinnar"]):
        entities["gender"] = "Transgender"

    for state in STATES:
        if state in t:
            entities["state"] = state.title()
            break

    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in t for kw in kws):
            entities["category"] = cat
            break

    for occ, kws in OCCUPATIONS.items():
        if any(kw in t for kw in kws):
            entities["occupation"] = occ
            break

    for edu, kws in EDUCATION_KEYWORDS.items():
        if any(kw in t for kw in kws):
            entities["education"] = edu
            break

    if any(k in t for k in ["married", "shaadi shuda", "vivahit"]):
        entities["marital_status"] = "Married"
    elif any(k in t for k in ["unmarried", "single", "kunwara", "kunwari"]):
        entities["marital_status"] = "Unmarried"
    elif any(k in t for k in ["widow", "vidhwa"]):
        entities["marital_status"] = "Widow"

    if any(k in t for k in ["disability", "divyang", "handicap", "viklang"]):
        entities["disability"] = True

    for svc_key in ["pan card", "aadhaar", "aadhar", "passport", "driving license",
                    "voter id", "ration card", "bank account"]:
        if svc_key in t:
            entities.setdefault("service_mentioned", []).append(svc_key)

    return entities


def detect_intent(text: str) -> tuple:
    t = _norm(text)
    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in t)
        if count:
            scores[intent] = count

    if scores:
        best_intent = max(scores, key=scores.get)
        confidence = min(0.6 + 0.1 * scores[best_intent], 0.95)
        return best_intent, confidence

    entities = extract_entities(t)
    if entities:
        return "provide_info", 0.7

    return "unknown", 0.3


def generate_response(intent: str, entities: dict, language: str = "en", profile_ctx: dict = None) -> str:
    profile_ctx = profile_ctx or {}
    hi = language == "hi"

    if intent == "greeting":
        return ("नमस्ते! मैं Citizen Service Navigator हूँ। मैं आपको सरकारी योजनाएं खोजने और "
                "सेवाओं (PAN, Aadhaar, Passport आदि) के लिए मदद कर सकता हूँ। आपकी उम्र, आय और राज्य बताएं।") if hi else \
            ("Hi! I'm your Citizen Service Navigator. I can help you find government schemes and "
             "guide you through services like PAN, Aadhaar, Passport, etc. Tell me your age, income, and state to get started.")

    if intent == "goodbye":
        return "अलविदा! फिर मिलेंगे।" if hi else "Goodbye! Feel free to come back anytime."

    if intent == "thanks":
        return "आपका स्वागत है!" if hi else "You're welcome! Happy to help."

    if intent == "ask_scheme":
        return ("मैंने आपकी प्रोफाइल के आधार पर योजनाओं की जांच शुरू कर दी है। कृपया 'Schemes' टैब देखें "
                "या मुझे अपनी उम्र, आय, राज्य और श्रेणी बताएं ताकि सही योजना सुझा सकूं।") if hi else \
            ("I can find schemes matching your profile. Please check the 'Schemes' tab, or tell me your "
             "age, income, state, and category so I can recommend the best matches.")

    if intent == "ask_service":
        return ("कौन सी सेवा चाहिए - PAN Card, Aadhaar, Passport, Driving License, Voter ID, Ration Card "
                "या Bank Account? मैं step-by-step प्रक्रिया दिखा सकता हूँ।") if hi else \
            ("Which service do you need — PAN Card, Aadhaar, Passport, Driving License, Voter ID, "
             "Ration Card, or Bank Account? I'll show you the step-by-step pathway.")

    if intent == "check_eligibility":
        return ("पात्रता जांचने के लिए मुझे आपकी उम्र, आय, राज्य, श्रेणी और व्यवसाय चाहिए। "
                "क्या आप ये बता सकते हैं?") if hi else \
            ("To check eligibility I need your age, income, state, category, and occupation. "
             "Can you share these details?")

    if intent == "track_application":
        return "आप अपनी सभी applications 'Applications' टैब में ट्रैक कर सकते हैं।" if hi else \
            "You can track all your applications in the 'Applications' tab with live status updates."

    if intent == "document_query":
        return "हर योजना/सेवा के लिए ज़रूरी दस्तावेज़ों की सूची उस पेज पर दी गई है, जिसे आप चेकलिस्ट की तरह पूरा कर सकते हैं।" if hi else \
            "Each scheme/service page lists required documents as a checklist you can track and complete."

    if intent == "provide_info":
        parts = []
        if "age" in entities:
            parts.append(f"age {entities['age']}")
        if "income" in entities:
            parts.append(f"income ₹{int(entities['income']):,}")
        if "state" in entities:
            parts.append(f"state {entities['state']}")
        if "category" in entities:
            parts.append(f"category {entities['category']}")
        if "occupation" in entities:
            parts.append(f"occupation {entities['occupation']}")
        detail = ", ".join(parts) if parts else "your details"
        return (f"धन्यवाद! मैंने {detail} नोट कर लिया है और आपकी प्रोफाइल अपडेट कर दी है। "
                f"अब मैं बेहतर योजनाएं सुझा सकता हूँ।") if hi else \
            (f"Got it! I've noted {detail} and updated your profile. "
             f"I can now recommend more accurate schemes for you.")

    return ("मुझे समझ नहीं आया, कृपया दोबारा बताएं। आप 'scheme', 'service' या अपनी जानकारी (उम्र, आय, राज्य) टाइप कर सकते हैं।") if hi else \
        ("I didn't quite catch that. Try asking about a 'scheme', a 'service', or share details like your age, income, or state.")


def process_message(text: str, language: str = "en", profile_ctx: dict = None) -> dict:
    intent, confidence = detect_intent(text)
    entities = extract_entities(text)
    response = generate_response(intent, entities, language, profile_ctx)
    return {
        "intent": intent,
        "confidence": confidence,
        "entities": entities,
        "response": response,
    }