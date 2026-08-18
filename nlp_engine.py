"""Grounded chat interpretation for JanSetu; it never invents scheme rules."""
import re

STATES = ["andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal", "delhi", "up", "mp", "wb"]
CORE_PROFILE_FIELDS = ("age", "gender", "income", "state", "category", "occupation", "education", "marital_status")
PROFILE_FIELD_LABELS = {"age": "age", "gender": "gender", "income": "annual family income", "state": "state/UT", "category": "category (SC/ST/OBC/EWS/General)", "occupation": "occupation", "education": "education level", "marital_status": "marital status"}
PROFILE_FIELD_LABELS_HI = {"age": "उम्र", "gender": "लिंग", "income": "परिवार की वार्षिक आय", "state": "राज्य/केंद्र शासित प्रदेश", "category": "श्रेणी (SC/ST/OBC/EWS/General)", "occupation": "व्यवसाय", "education": "शिक्षा स्तर", "marital_status": "वैवाहिक स्थिति"}
OCCUPATIONS = {"farmer": ["farmer", "kisan", "krishi", "agriculture"], "student": ["student", "chatra", "padhai", "college", "school"], "unemployed": ["unemployed", "berozgar", "no job", "jobless"], "business": ["business", "vyapari", "shopkeeper", "self employed", "vyapar"], "labourer": ["labour", "labourer", "mazdoor", "worker", "daily wage"], "employee": ["employee", "salaried", "service class", "naukri"]}
CATEGORY_KEYWORDS = {"SC": ["scheduled caste", "\\bsc\\b"], "ST": ["scheduled tribe", "\\bst\\b"], "OBC": ["other backward", "\\bobc\\b"], "EWS": ["economically weaker", "\\bews\\b"], "General": ["general category", "general caste", "\\bgeneral\\b"]}
EDUCATION_KEYWORDS = {"below_10th": ["below 10th", "8th pass", "primary"], "10th": ["10th", "matric", "dasvi"], "12th": ["12th", "intermediate", "barhavi"], "graduate": ["graduate", "graduation", "bachelor", "btech", "b.tech"], "postgraduate": ["postgraduate", "masters", "mtech", "phd"], "illiterate": ["illiterate", "anpadh", "no education"]}
SERVICE_ALIASES = {"PAN Card": ("pan card", "pan"), "Aadhaar Card": ("aadhaar", "aadhar"), "Passport": ("passport",), "Driving License": ("driving license", "driving licence"), "Voter ID Card": ("voter id", "voter card", "epic"), "Ration Card": ("ration card",), "Bank Account Opening": ("bank account", "jan dhan", "banking"), "Birth Certificate": ("birth certificate",), "Income Certificate": ("income certificate",), "Caste Certificate": ("caste certificate",), "e-Shram Registration": ("e-shram", "eshram")}
SCHEME_ALIASES = {"Central Sector Scheme of Scholarship for College and University Students": ("central sector scholarship", "csss"), "AICTE Pragati Scholarship": ("aicte pragati", "pragati scholarship"), "Top Class Education Scheme for SC Students": ("top class scholarship", "top class education")}


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def extract_entities(text: str) -> dict:
    t, entities = _norm(text), {}
    age_match = re.search(r"\b(\d{1,2})\s*(?:years?|yrs?|saal|yr)\b", t) or re.search(r"\bage\s*(?:is|:)?\s*(\d{1,2})\b", t)
    if age_match and 0 < int(age_match.group(1)) < 121:
        entities["age"] = int(age_match.group(1))
    # Commas and the rupee symbol are common in Indian income amounts.
    income_text = re.sub(r"(?<=\d),(?=\d)", "", t)
    income_match = re.search(r"(?:income|salary|kamata|kamaata)\D{0,18}(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|laakh)?", income_text) or re.search(r"\b(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|laakh)\b", income_text)
    if income_match:
        income = float(income_match.group(1))
        if len(income_match.groups()) > 1 and income_match.group(2): income *= 100000
        entities["income"] = income
    if any(k in t for k in ("female", "mahila", "woman", "ladki", "aurat")): entities["gender"] = "Female"
    elif any(k in t for k in ("male", "purush", " man ", "ladka", "aadmi")): entities["gender"] = "Male"
    elif any(k in t for k in ("transgender", "third gender", "kinnar")): entities["gender"] = "Transgender"
    for state in sorted(STATES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(state)}\b", t):
            entities["state"] = {"up": "Uttar Pradesh", "mp": "Madhya Pradesh", "wb": "West Bengal"}.get(state, state.title()); break
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(re.search(word, t) if word.startswith("\\b") else word in t for word in keywords): entities["category"] = category; break
    for occupation, keywords in OCCUPATIONS.items():
        if any(word in t for word in keywords): entities["occupation"] = occupation; break
    for education, keywords in EDUCATION_KEYWORDS.items():
        if any(word in t for word in keywords): entities["education"] = education; break
    if any(k in t for k in ("unmarried", "not married", "single", "kunwara", "kunwari")): entities["marital_status"] = "Unmarried"
    elif any(k in t for k in ("married", "shaadi shuda", "vivahit")): entities["marital_status"] = "Married"
    elif any(k in t for k in ("widow", "vidhwa")): entities["marital_status"] = "Widow"
    if any(k in t for k in ("disability", "divyang", "handicap", "viklang")): entities["disability"] = True
    for name, aliases in SERVICE_ALIASES.items():
        if any(re.search(rf"\b{re.escape(alias)}\b", t) for alias in aliases): entities["service_mentioned"] = name; break
    for name, aliases in SCHEME_ALIASES.items():
        if any(alias in t for alias in aliases): entities["scheme_mentioned"] = name; break
    if not entities.get("scheme_mentioned") and any(word in t for word in ("scholarship", "student scheme", "student yojana", "student scholarship", "chhatravritti", "छात्रवृत्ति")):
        entities["scheme_category"] = "Scholarship"
    return entities


def detect_intent(text: str) -> tuple:
    t, entities = _norm(text), extract_entities(text)
    if entities.get("service_mentioned"): return "ask_service", 0.95
    if any(word in t for word in ("documents", "document service", "certificate service", "कागज़ात", "दस्तावेज़")): return "open_services", 0.82
    if any(word in t for word in ("eligible", "eligibility", "patrata", "qualify", "kya main")): return "check_eligibility", 0.9
    if entities.get("scheme_mentioned") or entities.get("scheme_category") or any(word in t for word in ("scheme", "yojana", "yojna", "scholarship", "subsidy", "government benefit", "योजना")): return "ask_scheme", 0.9
    if any(word in t for word in ("application status", "track", "aavedan", "kaha tak pahuncha")): return "track_application", 0.85
    if any(word in t for word in ("my profile", "update profile", "profile details", "personal details")): return "open_profile", 0.85
    if any(word in t for word in ("notifications", "notification", "alerts")): return "open_notifications", 0.82
    if any(word in t for word in ("settings", "change language", "dark mode")): return "open_settings", 0.82
    if any(word in t for word in ("what can you do", "what do you do", "what is jansetu", "who are you", "which details", "what details", "why do you need")): return "basic_question", 0.85
    if re.search(r"\b(hi|hello|hey|namaste|namaskar|hii|helo|salaam)\b", t): return "greeting", 0.85
    if any(word in t for word in ("bye", "goodbye", "alvida", "phir milenge", "tata")): return "goodbye", 0.85
    if any(word in t for word in ("thanks", "thank you", "dhanyavad", "shukriya")): return "thanks", 0.85
    return ("provide_info", 0.75) if entities else ("unknown", 0.2)


def missing_profile_fields(profile_ctx: dict) -> list:
    return [field for field in CORE_PROFILE_FIELDS if profile_ctx.get(field) in (None, "")]


def _follow_up(profile_ctx: dict, language: str = "en") -> str:
    missing = missing_profile_fields(profile_ctx)
    if language == "hi":
        if not missing:
            return "आपकी आवश्यक प्रोफ़ाइल जानकारी पूरी है। अब मैं JanSetu में उपलब्ध योजनाओं से मिलान कर सकता हूँ।"
        labels = [PROFILE_FIELD_LABELS_HI[field] for field in missing]
        return "योजनाओं की सिफारिश दिखाने से पहले मुझे आपकी " + ", ".join(labels) + ". कृपया बाकी जानकारी एक संदेश में भेजें; पूरी पात्रता प्रोफ़ाइल मिलने के बाद ही मैं योजनाएँ दिखाऊँगा।"
    if not missing: return "Your core profile is complete. I can now match schemes using the information saved in JanSetu."
    labels = [PROFILE_FIELD_LABELS[field] for field in missing]
    return "Before I show scheme recommendations, I need your " + ", ".join(labels) + ". Send the remaining details in one message; I will check schemes only after this eligibility profile is complete."


def generate_response(intent: str, entities: dict, language: str = "en", profile_ctx: dict = None) -> str:
    profile_ctx = profile_ctx or {}
    # Eligibility recommendations must never be shown from a partial profile,
    # regardless of the selected chat language.
    if language == "hi" and intent in ("ask_scheme", "check_eligibility", "provide_info"):
        return _follow_up(profile_ctx, language="hi")
    if language == "hi":
        if intent == "ask_service": return f"{entities.get('service_mentioned', 'चुनी हुई सेवा')} का JanSetu मार्ग खोल रहा हूँ।"
        if intent in ("ask_scheme", "check_eligibility", "provide_info"): return "सही योजनाएँ दिखाने के लिए उम्र, वार्षिक आय, राज्य, श्रेणी और व्यवसाय चाहिए। उपलब्ध जानकारी के आधार पर योजनाएँ खोल रहा हूँ।"
        if intent == "track_application": return "आपके आवेदन Applications पेज में खोले जा रहे हैं।"
        if intent == "open_profile": return "आपकी प्रोफ़ाइल खोली जा रही है।"
        if intent == "open_services": return "सेवाओं का पेज खोला जा रहा है।"
        if intent == "open_notifications": return "आपकी सूचनाएँ खोली जा रही हैं।"
        if intent == "open_settings": return "सेटिंग्स खोली जा रही हैं।"
        if intent == "unknown": return "मेरे पास इसका सत्यापित उत्तर नहीं है। मैं JanSetu की योजनाओं, सेवाओं और आवेदनों में मदद कर सकता हूँ।"
    if intent == "greeting": return "Hi! I can help find schemes and guide you through JanSetu services. " + _follow_up(profile_ctx)
    if intent in ("ask_scheme", "check_eligibility", "provide_info"):
        saved = [PROFILE_FIELD_LABELS[key] for key in entities if key in PROFILE_FIELD_LABELS]
        return ("I’ve saved your " + ", ".join(saved) + ". " if saved else "") + _follow_up(profile_ctx)
    if intent == "ask_service":
        service = entities.get("service_mentioned")
        return f"Opening the JanSetu pathway for {service}." if service else "Tell me which JanSetu service you need, such as PAN Card, Aadhaar Card, Passport, or Income Certificate."
    if intent == "track_application": return "You can view the saved progress of your JanSetu applications in the Applications section."
    if intent == "open_profile": return "Opening your JanSetu profile so you can review or update your details."
    if intent == "open_services": return "Opening the JanSetu services page. Choose a service to see its full pathway."
    if intent == "open_notifications": return "Opening your notifications."
    if intent == "open_settings": return "Opening settings."
    if intent == "basic_question": return "JanSetu helps you compare the schemes in its catalogue and follow its listed public-service pathways. For recommendations it uses your age, annual income, state/UT, category and occupation. It only answers from information available in this app; confirm final eligibility, fees and deadlines on the official service or scheme page."
    if intent == "thanks": return "You’re welcome."
    if intent == "goodbye": return "Goodbye!"
    return "I don’t have verified information to answer that. I can help with a JanSetu scheme recommendation, a listed service pathway, or your saved application status."


def process_message(text: str, language: str = "en", profile_ctx: dict = None) -> dict:
    intent, confidence, entities = *detect_intent(text), extract_entities(text)
    merged_profile = dict(profile_ctx or {})
    for key in CORE_PROFILE_FIELDS:
        if key in entities: merged_profile[key] = entities[key]
    missing = missing_profile_fields(merged_profile)
    navigation = None
    if intent == "ask_service": navigation = {"type": "service", "label": "Open service pathway"}
    elif intent in ("ask_scheme", "check_eligibility", "provide_info") and not missing:
        navigation = {"type": "scheme", "label": "View matching schemes"}
    elif intent == "track_application": navigation = {"type": "applications", "label": "Open applications"}
    elif intent == "open_profile": navigation = {"type": "profile", "label": "Open profile"}
    elif intent == "open_services": navigation = {"type": "services", "label": "Open services"}
    elif intent == "open_notifications": navigation = {"type": "notifications", "label": "Open notifications"}
    elif intent == "open_settings": navigation = {"type": "settings", "label": "Open settings"}
    return {"intent": intent, "confidence": confidence, "entities": entities, "response": generate_response(intent, entities, language, merged_profile), "missing_profile_fields": missing, "navigation": navigation}
