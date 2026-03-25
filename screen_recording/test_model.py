import pickle

with open('digital_arrest_model_final.pkl', 'rb') as f:
    d = pickle.load(f)

model = d['model']
tfidf = d['tfidf']

print("=" * 60)
print("     MODEL DETECTION TEST")
print("=" * 60)

tests = [
    # These MUST be detected as SCAM
    "digital arrest case filed against you pay two lakhs",
    "i found drugs pay immediately to avoid jail",
    "cbi officer calling you are under arrest transfer money",
    "just pay two lakhs to the number imprisonment 7 years",
    "you are under digital arrest do not tell anyone",
    "turant upi transfer karo parivaar ko mat batana",
    "enforcement directorate officer freeze your account",
    "safe account transfer money stay on call",
    # These should be NORMAL
    "hello how are you doing today",
    "what is the weather like tomorrow",
    "i want to order food from the restaurant",
]

print("\nRESULTS:")
print("-" * 60)
for t in tests:
    vec  = tfidf.transform([t.lower()])
    pred = model.predict(vec)[0]
    conf = model.predict_proba(vec)[0][pred] * 100
    label = "SCAM  " if pred == 1 else "NORMAL"
    flag  = "✅" if (pred == 1 and "normal" not in t[:5]) else ("✅" if pred == 0 else "❌")
    print(f"[{label}] {int(conf):3d}%  {flag}  {t[:55]}")

print("-" * 60)
print("\nDone! Share the output above.")
