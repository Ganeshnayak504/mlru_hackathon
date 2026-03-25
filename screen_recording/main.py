# # ============================================================
# #        DIGITAL ARREST SHIELD — Laptop Audio Detection
# #        Works on Windows | Uses Whisper + Local ML Model
# # ============================================================

# import pickle
# import warnings
# import threading
# import queue
# import time
# import tempfile
# import os
# import tkinter as tk
# from tkinter import font as tkfont
# import sounddevice as sd
# import numpy as np
# import scipy.io.wavfile as wav
# import whisper

# warnings.filterwarnings('ignore')

# # ── CONFIG ───────────────────────────────────────────────────
# MODEL_PATH    = "digital_arrest_model_final.pkl"
# SAMPLE_RATE   = 16000       # Whisper expects 16kHz
# CHUNK_SECONDS = 5           # record 5 seconds at a time
# WHISPER_MODEL = "small"     # small = better accuracy on 15GB RAM
# USE_API       = False       # True = use FastAPI, False = use local model
# API_URL       = "http://localhost:8000/classify"
# DEVICE_INDEX  = 1

# SCAM_PHRASES = [
#     "digital arrest", "arrest warrant", "cbi officer", "ed officer",
#     "ncb officer", "rbi official", "income tax officer", "cyber crime",
#     "transfer money", "upi transfer", "safe account", "pay immediately",
#     "do not tell anyone", "stay on call", "you are under arrest",
#     "case filed", "freeze your account", "jail", "digital arrest mein",
#     "turant transfer", "parivaar ko mat batana", "cbi", "enforcement directorate"
# ]

# # ── LOAD LOCAL MODEL ─────────────────────────────────────────
# print("=" * 55)
# print("     DIGITAL ARREST SHIELD — Starting Up")
# print("=" * 55)
# print("\n⏳ Loading ML model...")
# with open(MODEL_PATH, 'rb') as f:
#     model_data = pickle.load(f)

# ML_MODEL = model_data['model']
# TFIDF    = model_data['tfidf']
# print(f"✅ Model loaded — Accuracy: {model_data['accuracy']}")

# # ── LOAD WHISPER ─────────────────────────────────────────────
# print(f"\n⏳ Loading Whisper {WHISPER_MODEL} model...")
# whisper_model = whisper.load_model(WHISPER_MODEL)
# print(f"✅ Whisper loaded")
# print("\n✅ All systems ready!")
# print("=" * 55)

# # ── AUDIO QUEUE ──────────────────────────────────────────────
# audio_queue = queue.Queue()
# is_running  = True

# # ── CLASSIFY FUNCTION ────────────────────────────────────────
# def classify_text(text):
#     """
#     Takes text and returns classification result
#     Uses local model OR FastAPI depending on USE_API flag
#     """
#     if USE_API:
#         # ── API mode (when backend is ready) ──────────────────
#         import requests
#         try:
#             response = requests.post(
#                 API_URL,
#                 json={"text": text},
#                 timeout=5
#             )
#             return response.json()
#         except Exception as e:
#             print(f"API error: {e} — falling back to local model")

#     # ── Local model mode ──────────────────────────────────────
#     clean_text = text.lower()
#     vec        = TFIDF.transform([clean_text])
#     prediction = ML_MODEL.predict(vec)[0]
#     confidence = ML_MODEL.predict_proba(vec)[0][prediction] * 100

#     # Find triggered phrases
#     triggered = [
#         phrase for phrase in SCAM_PHRASES
#         if phrase in clean_text
#     ]

#     # Risk level
#     if prediction == 1 and confidence >= 70:
#         risk = "HIGH"
#     elif prediction == 1 and confidence >= 50:
#         risk = "MEDIUM"
#     else:
#         risk = "LOW"

#     return {
#         "label"            : "scam" if prediction == 1 else "normal",
#         "risk"             : risk,
#         "score"            : round(confidence / 100, 2),
#         "triggered_phrases": triggered,
#         "advice"           : "Hang up immediately. Do not transfer any money. Call 1930."
#                              if prediction == 1 else "No threat detected. Stay alert."
#     }

# # ── ALERT WINDOW ─────────────────────────────────────────────
# def show_alert(result, transcript):
#     """
#     Shows a popup alert window when scam is detected
#     RED  = SCAM detected
#     GREEN = Safe
#     """
#     alert = tk.Tk()
#     alert.title("Digital Arrest Shield")
#     alert.geometry("600x500")
#     alert.resizable(False, False)

#     is_scam = result['label'] == 'scam'

#     # Background color
#     bg_color   = "#FF3333" if is_scam else "#00AA44"
#     text_color = "#FFFFFF"

#     alert.configure(bg=bg_color)

#     # Title
#     title_font = tkfont.Font(family="Arial", size=22, weight="bold")
#     body_font  = tkfont.Font(family="Arial", size=12)
#     small_font = tkfont.Font(family="Arial", size=10)

#     if is_scam:
#         title_text = "⚠️  SCAM DETECTED!"
#     else:
#         title_text = "✅  No Threat Detected"

#     tk.Label(
#         alert,
#         text=title_text,
#         font=title_font,
#         bg=bg_color,
#         fg=text_color
#     ).pack(pady=20)

#     # Risk level
#     tk.Label(
#         alert,
#         text=f"Risk Level: {result['risk']}",
#         font=body_font,
#         bg=bg_color,
#         fg=text_color
#     ).pack()

#     # Confidence
#     tk.Label(
#         alert,
#         text=f"Confidence: {int(result['score'] * 100)}%",
#         font=body_font,
#         bg=bg_color,
#         fg=text_color
#     ).pack(pady=5)

#     # Transcript
#     tk.Label(
#         alert,
#         text="Detected Speech:",
#         font=body_font,
#         bg=bg_color,
#         fg=text_color
#     ).pack()

#     transcript_box = tk.Text(
#         alert,
#         height=4,
#         width=60,
#         font=small_font,
#         bg="#FFFFFF",
#         fg="#000000",
#         wrap=tk.WORD
#     )
#     transcript_box.insert(tk.END, transcript[:300])
#     transcript_box.config(state=tk.DISABLED)
#     transcript_box.pack(pady=5, padx=20)

#     # Triggered phrases
#     if result['triggered_phrases']:
#         tk.Label(
#             alert,
#             text=f"🚨 Detected: {', '.join(result['triggered_phrases'][:3])}",
#             font=small_font,
#             bg=bg_color,
#             fg=text_color,
#             wraplength=550
#         ).pack(pady=5)

#     # Advice
#     tk.Label(
#         alert,
#         text=result['advice'],
#         font=body_font,
#         bg=bg_color,
#         fg=text_color,
#         wraplength=550
#     ).pack(pady=10)

#     # Buttons
#     btn_frame = tk.Frame(alert, bg=bg_color)
#     btn_frame.pack(pady=10)

#     if is_scam:
#         # Call 1930 button
#         tk.Button(
#             btn_frame,
#             text="📞 Call 1930",
#             font=body_font,
#             bg="#FFFFFF",
#             fg="#FF3333",
#             width=15,
#             command=lambda: os.system("start tel:1930")
#         ).pack(side=tk.LEFT, padx=10)

#         # Report button
#         tk.Button(
#             btn_frame,
#             text="🌐 Report Crime",
#             font=body_font,
#             bg="#FFFFFF",
#             fg="#FF3333",
#             width=15,
#             command=lambda: os.system(
#                 "start https://cybercrime.gov.in"
#             )
#         ).pack(side=tk.LEFT, padx=10)

#     # Dismiss button
#     tk.Button(
#         btn_frame,
#         text="Dismiss",
#         font=body_font,
#         bg="#FFFFFF",
#         fg="#000000",
#         width=10,
#         command=alert.destroy
#     ).pack(side=tk.LEFT, padx=10)

#     # Auto close after 30 seconds
#     alert.after(30000, alert.destroy)
#     alert.lift()
#     alert.attributes('-topmost', True)
#     alert.mainloop()

# # ── AUDIO RECORDING THREAD ───────────────────────────────────
# def record_audio():
#     """
#     Continuously records system audio in chunks
#     Puts each chunk into the queue for processing
#     """
#     print("\n🎤 Recording started — listening for scam patterns...")
#     print("Press Ctrl+C to stop\n")

#     while is_running:
#         try:
#             # Record chunk
#             audio_chunk = sd.rec(
#                 int(CHUNK_SECONDS * SAMPLE_RATE),
#                 samplerate=SAMPLE_RATE,
#                 channels=2,
#                 dtype='float32',
#                 device=DEVICE_INDEX
#             )
#             sd.wait()

#             # Put in queue
#             audio_queue.put(audio_chunk)

#         except Exception as e:
#             print(f"Recording error: {e}")
#             time.sleep(1)

# # ── PROCESSING THREAD ─────────────────────────────────────────
# def process_audio():
#     """
#     Takes audio chunks from queue
#     Transcribes with Whisper
#     Classifies with ML model
#     Shows alert if scam detected
#     """
#     while is_running:
#         try:
#             # Get audio from queue
#             audio_chunk = audio_queue.get(timeout=1)

#             # Save to temp file
#             with tempfile.NamedTemporaryFile(
#                 suffix='.wav',
#                 delete=False
#             ) as tmp:
#                 tmp_path = tmp.name
#                 # wav.write(
#                 #     tmp_path,
#                 #     SAMPLE_RATE,
#                 #     (audio_chunk * 32767).astype(np.int16)
#                 # )
#                 mono_chunk = audio_chunk.mean(axis=1)
#                 wav.write(
#                     tmp_path,
#                     SAMPLE_RATE,
#                     (mono_chunk * 32767).astype(np.int16)
#                 )
#             # Transcribe with Whisper
#             result_whisper = whisper_model.transcribe(
#                 tmp_path,
#                 language=None,  # auto detect language
#                 task="transcribe"
#             )
#             transcript = result_whisper['text'].strip()

#             # Clean up temp file
#             os.unlink(tmp_path)

#             # Skip if empty or too short
#             if len(transcript) < 10:
#                 continue

#             print(f"📝 Heard: {transcript[:100]}...")

#             # Classify
#             result = classify_text(transcript)

#             print(f"🔍 Result: {result['label'].upper()} "
#                   f"({int(result['score']*100)}% confident) "
#                   f"Risk: {result['risk']}")

#             # Show alert if scam OR if high risk keywords found
#             if (result['label'] == 'scam' and result['score'] >=0.60 and 
#                 result['risk'] in ['HIGH','MEDIUM'] 
#                 and result['triggered_phrases']):
#                 print("🚨 SCAM DETECTED — Showing alert!")
#                 # Run alert in main thread
#                 threading.Thread(
#                     target=show_alert,
#                     args=(result, transcript),
#                     daemon=True
#                 ).start()

#         except queue.Empty:
#             continue
#         except Exception as e:
#             print(f"Processing error: {e}")

# # ── MAIN CONTROL PANEL ───────────────────────────────────────
# def show_control_panel():
#     """
#     Shows a simple control panel window
#     Start/Stop detection
#     """
#     root = tk.Tk()
#     root.title("Digital Arrest Shield")
#     root.geometry("400x300")
#     root.configure(bg="#1a1a2e")
#     root.resizable(False, False)

#     title_font  = tkfont.Font(family="Arial", size=16, weight="bold")
#     status_font = tkfont.Font(family="Arial", size=11)
#     btn_font    = tkfont.Font(family="Arial", size=12, weight="bold")

#     # Title
#     tk.Label(
#         root,
#         text="🛡️ Digital Arrest Shield",
#         font=title_font,
#         bg="#1a1a2e",
#         fg="#00ff88"
#     ).pack(pady=20)

#     # Status
#     status_var = tk.StringVar(value="● LISTENING ACTIVE")
#     tk.Label(
#         root,
#         textvariable=status_var,
#         font=status_font,
#         bg="#1a1a2e",
#         fg="#00ff88"
#     ).pack(pady=5)

#     # Mode
#     mode_text = "Mode: Local Model" if not USE_API else "Mode: API Connected"
#     tk.Label(
#         root,
#         text=mode_text,
#         font=status_font,
#         bg="#1a1a2e",
#         fg="#888888"
#     ).pack()

#     tk.Label(
#         root,
#         text=f"Whisper: {WHISPER_MODEL} | "
#              f"Chunk: {CHUNK_SECONDS}s",
#         font=status_font,
#         bg="#1a1a2e",
#         fg="#888888"
#     ).pack(pady=5)

#     tk.Label(
#         root,
#         text="Monitoring all system audio...",
#         font=status_font,
#         bg="#1a1a2e",
#         fg="#aaaaaa"
#     ).pack(pady=10)

#     # Stop button
#     def stop_detection():
#         global is_running
#         is_running = False
#         status_var.set("● DETECTION STOPPED")
#         root.configure(bg="#330000")
#         print("\n⛔ Detection stopped.")

#     tk.Button(
#         root,
#         text="⛔ Stop Detection",
#         font=btn_font,
#         bg="#FF3333",
#         fg="#FFFFFF",
#         width=20,
#         command=stop_detection
#     ).pack(pady=20)

#     root.mainloop()

# # ── ENTRY POINT ───────────────────────────────────────────────
# if __name__ == "__main__":

#     # Start recording thread
#     record_thread = threading.Thread(
#         target=record_audio,
#         daemon=True
#     )
#     record_thread.start()

#     # Start processing thread
#     process_thread = threading.Thread(
#         target=process_audio,
#         daemon=True
#     )
#     process_thread.start()

#     # Show control panel (this blocks until window closed)
#     show_control_panel()

#     print("\n👋 Digital Arrest Shield stopped. Stay safe!")

# ============================================================
#        DIGITAL ARREST SHIELD — Laptop Audio Detection
#        Works on Windows | Uses Whisper + Local ML Model
# ============================================================

import pickle
import warnings
import threading
import queue
import time
import tempfile
import os
import tkinter as tk
from tkinter import font as tkfont
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import whisper

warnings.filterwarnings('ignore')

# ── CONFIG ───────────────────────────────────────────────────
MODEL_PATH    = "digital_arrest_model_final.pkl"
SAMPLE_RATE   = 16000
CHUNK_SECONDS = 5           # ⬇ reduced from 5 → faster response
SCAM_THRESHOLD = 60
WHISPER_MODEL = "small"
USE_API       = False
API_URL       = "http://localhost:8000/classify"
DEVICE_INDEX  = 1

# ── PHRASE LISTS ─────────────────────────────────────────────
# HIGH priority — any ONE of these alone triggers alert
# HIGH_PRIORITY_PHRASES = [
#     "digital arrest",
#     "you are under arrest",
#     "cbi officer",
#     "ed officer",
#     "ncb officer",
#     "enforcement directorate",
#     "cyber crime police",
#     "arrest warrant",
#     "digital arrest mein",
#     "turant transfer",
#     "turant upi",
#     "parivaar ko mat batana",
#     "jail bhej denge",
#     "do not tell anyone",
#     "freeze your account",
#     "safe account transfer",
# ]

# MEDIUM priority — need 2+ of these to trigger alert
# # MEDIUM_PRIORITY_PHRASES = [
#     "pay immediately",
#     "transfer money",
#     "upi transfer",
#     "case filed",
#     "stay on call",
#     "income tax",
#     "rbi official",
#     "money laundering",
#     "pay two lakh",
#     "pay 2 lakh",
#     "imprisonment",
#     "warrant",
#     "drug",
#     "illegal",
#     "account freeze",
#     "legal action",
#     "court order",
#     "police station",
# ]

# ── PHRASE LISTS ─────────────────────────────────────────────
# HIGH priority — any ONE of these alone triggers alert
HIGH_PRIORITY_PHRASES = [
    "digital arrest",
    "you are under arrest",
    "cbi officer",
    "ed officer",
    "ncb officer",
    "enforcement directorate",
    "cyber crime police",
    "arrest warrant",
    "digital arrest mein",
    "turant transfer",
    "turant upi",
    "parivaar ko mat batana",
    "jail bhej denge",
    "do not tell anyone",
    "freeze your account",
    "safe account transfer",
    "crime branch",
    "supreme court order",
]

# MEDIUM priority — need 2+ of these to trigger alert
MEDIUM_PRIORITY_PHRASES = [
    "pay immediately",
    "transfer money",
    "upi transfer",
    "case filed",
    "stay on call",
    "income tax",
    "rbi official",
    "money laundering",
    "pay two lakh",
    "pay 2 lakh",
    "2 lakhs",
    "2 lex",       # Common Whisper phonetic error for "lakhs"
    "2 lakh",
    "2 yahara",    # Caught from your specific logs
    "two lakhs",
    "imprisonment",
    "warrant",
    "drug",
    "illegal",
    "account freeze",
    "legal action",
    "police station",
    "settlement",
    "penalty",
    "duration",
]

# ── LOAD LOCAL MODEL ─────────────────────────────────────────
print("=" * 55)
print("     DIGITAL ARREST SHIELD — Starting Up")
print("=" * 55)
print("\n⏳ Loading ML model...")
with open(MODEL_PATH, 'rb') as f:
    model_data = pickle.load(f)

ML_MODEL = model_data['model']
TFIDF    = model_data['tfidf']
print(f"✅ Model loaded — Accuracy: {model_data['accuracy']}")

# ── LOAD WHISPER ─────────────────────────────────────────────
print(f"\n⏳ Loading Whisper {WHISPER_MODEL} model...")
whisper_model = whisper.load_model(WHISPER_MODEL)
print(f"✅ Whisper loaded")
print("\n✅ All systems ready!")
print("=" * 55)

# ── AUDIO QUEUE ──────────────────────────────────────────────
audio_queue = queue.Queue()
is_running  = True

# ── SMART CLASSIFY FUNCTION ──────────────────────────────────
# def classify_text(text):
#     """
#     3-layer detection:
#     1. HIGH priority phrases  → instant trigger (any 1 match)
#     2. MEDIUM priority phrases → trigger on 2+ matches
#     3. ML model score         → trigger if score >= 65%
#     Final score = boosted combination of all three
#     """
#     clean = text.lower()

#     # Layer 1 & 2 — phrase matching
#     high_hits   = [p for p in HIGH_PRIORITY_PHRASES   if p in clean]
#     medium_hits = [p for p in MEDIUM_PRIORITY_PHRASES if p in clean]
#     all_triggered = high_hits + medium_hits

#     # Layer 3 — ML model (always get scam probability column)
#     vec     = TFIDF.transform([clean])
#     ml_conf = ML_MODEL.predict_proba(vec)[0][1] * 100

#     # Boosted score
#     boosted_score = ml_conf
#     if high_hits:
#         boosted_score = max(boosted_score, 50) + min(len(high_hits) * 25, 50)
#     if len(medium_hits) >= 2:
#         boosted_score += min(len(medium_hits) * 10, 30)
#     boosted_score = min(boosted_score, 99)

#     # Final decision
#     is_scam = (
#         len(high_hits) >= 1      or
#         len(medium_hits) >= 2    or
#         boosted_score >= SCAM_THRESHOLD
#     )

#     # Risk level
#     if is_scam and boosted_score >= 75:
#         risk = "HIGH"
#     elif is_scam and boosted_score >= 55:
#         risk = "MEDIUM"
#     elif is_scam:
#         risk = "LOW"
#     else:
#         risk = "NONE"

#     advice = (
#         "Hang up immediately. Do not transfer any money. Call 1930."
#         if is_scam else
#         "No threat detected. Stay alert and never share personal details."
#     )

#     return {
#         "label"            : "scam" if is_scam else "normal",
#         "risk"             : risk,
#         "score"            : round(boosted_score / 100, 2),
#         "triggered_phrases": all_triggered,
#         "advice"           : advice,
#         "ml_score"         : round(ml_conf, 1),
#     }

def classify_text(text):
    """
    3-layer detection:
    1. HIGH priority phrases  → instant trigger (any 1 match)
    2. MEDIUM priority phrases → trigger on 2+ matches
    3. ML model score          → trigger if score >= SCAM_THRESHOLD
    """
    clean = text.lower()

    # Layer 1 & 2 — phrase matching
    high_hits   = [p for p in HIGH_PRIORITY_PHRASES   if p in clean]
    
    # Catching "Digital... Arrest" even if Whisper splits them
    if "digital" in clean and "arrest" in clean and "digital arrest" not in high_hits:
        high_hits.append("digital+arrest")

    medium_hits = [p for p in MEDIUM_PRIORITY_PHRASES if p in clean]
    all_triggered = high_hits + medium_hits

    # Layer 3 — ML model score
    vec     = TFIDF.transform([clean])
    ml_conf = ML_MODEL.predict_proba(vec)[0][1] * 100

    # Boosted score logic
    boosted_score = ml_conf
    if high_hits:
        # If a high priority phrase is found, we ensure a high score
        boosted_score = max(boosted_score, 80) + (len(high_hits) * 5)
    elif len(medium_hits) >= 2:
        # If multiple medium phrases are found, we ensure a medium/high score
        boosted_score = max(boosted_score, 65) + (len(medium_hits) * 5)
    
    boosted_score = min(boosted_score, 99) # Cap at 99%

    # Final decision using the threshold
    is_scam = (
        len(high_hits) >= 1      or
        len(medium_hits) >= 2    or
        boosted_score >= SCAM_THRESHOLD
    )

    # Risk level assignment
    if not is_scam:
        risk = "NONE"
    elif boosted_score >= 80 or len(high_hits) >= 1:
        risk = "HIGH"
    else:
        risk = "MEDIUM"

    advice = (
        "Hang up immediately. Do not transfer any money. Call 1930."
        if is_scam else
        "No threat detected. Stay alert and never share personal details."
    )

    return {
        "label"            : "scam" if is_scam else "normal",
        "risk"             : risk,
        "score"            : round(boosted_score / 100, 2),
        "triggered_phrases": all_triggered,
        "advice"           : advice,
        "ml_score"         : round(ml_conf, 1),
    }

# ── ALERT COOLDOWN ────────────────────────────────────────────
alert_shown    = False
alert_cooldown = 30   # seconds before next alert can show

def reset_cooldown():
    global alert_shown
    time.sleep(alert_cooldown)
    alert_shown = False

# ── ALERT WINDOW ─────────────────────────────────────────────
def show_alert(result, transcript):
    global alert_shown
    alert_shown = True

    alert = tk.Tk()
    alert.title("⚠️ Digital Arrest Shield — SCAM DETECTED")
    alert.geometry("620x520")
    alert.resizable(False, False)

    is_scam    = result['label'] == 'scam'
    bg_color   = "#CC0000" if is_scam else "#006633"
    text_color = "#FFFFFF"
    alert.configure(bg=bg_color)

    title_font = tkfont.Font(family="Arial", size=22, weight="bold")
    body_font  = tkfont.Font(family="Arial", size=12)
    small_font = tkfont.Font(family="Arial", size=10)

    title_text = (
        f"⚠️  SCAM DETECTED — {result['risk']} RISK"
        if is_scam else "✅  No Threat Detected"
    )

    tk.Label(alert, text=title_text,
             font=title_font, bg=bg_color, fg=text_color).pack(pady=15)

    tk.Label(alert,
             text=f"Score: {int(result['score']*100)}%  |  ML Score: {result['ml_score']}%",
             font=body_font, bg=bg_color, fg=text_color).pack()

    tk.Label(alert, text="Detected Speech:",
             font=body_font, bg=bg_color, fg=text_color).pack(pady=(10, 2))

    transcript_box = tk.Text(alert, height=4, width=65,
                             font=small_font, bg="#FFFFFF",
                             fg="#000000", wrap=tk.WORD)
    transcript_box.insert(tk.END, transcript[:300])
    transcript_box.config(state=tk.DISABLED)
    transcript_box.pack(padx=20)

    if result['triggered_phrases']:
        tk.Label(alert,
                 text="🚨 Triggered: " + ", ".join(result['triggered_phrases'][:5]),
                 font=small_font, bg=bg_color, fg="#FFFF00",
                 wraplength=580).pack(pady=8)

    tk.Label(alert, text=result['advice'],
             font=body_font, bg=bg_color, fg=text_color,
             wraplength=580).pack(pady=5)

    btn_frame = tk.Frame(alert, bg=bg_color)
    btn_frame.pack(pady=15)

    if is_scam:
        tk.Button(btn_frame, text="📞 Call 1930",
                  font=body_font, bg="#FFFFFF", fg="#CC0000", width=15,
                  command=lambda: os.system("start tel:1930")
                  ).pack(side=tk.LEFT, padx=8)

        tk.Button(btn_frame, text="🌐 Report Crime",
                  font=body_font, bg="#FFFFFF", fg="#CC0000", width=15,
                  command=lambda: os.system("start https://cybercrime.gov.in")
                  ).pack(side=tk.LEFT, padx=8)

    tk.Button(btn_frame, text="Dismiss",
              font=body_font, bg="#FFFFFF", fg="#000000", width=10,
              command=lambda: [alert.destroy(),
                               threading.Thread(target=reset_cooldown, daemon=True).start()]
              ).pack(side=tk.LEFT, padx=8)

    alert.after(30000, lambda: [alert.destroy(),
                                threading.Thread(target=reset_cooldown, daemon=True).start()])
    alert.lift()
    alert.attributes('-topmost', True)
    alert.mainloop()

# ── AUDIO RECORDING THREAD ───────────────────────────────────
def record_audio():
    print("\n🎤 Recording started — listening for scam patterns...")
    print(f"Chunk size: {CHUNK_SECONDS}s | Device: {DEVICE_INDEX}\n")

    while is_running:
        try:
            audio_chunk = sd.rec(
                int(CHUNK_SECONDS * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=2,
                dtype='float32',
                device=DEVICE_INDEX
            )
            sd.wait()
            audio_queue.put(audio_chunk)
        except Exception as e:
            print(f"Recording error: {e}")
            time.sleep(1)

# ── PROCESSING THREAD ─────────────────────────────────────────
def process_audio():
    while is_running:
        try:
            audio_chunk = audio_queue.get(timeout=1)

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path   = tmp.name
                mono_chunk = audio_chunk.mean(axis=1)
                wav.write(tmp_path, SAMPLE_RATE,
                          (mono_chunk * 32767).astype(np.int16))

            result_whisper = whisper_model.transcribe(
                tmp_path, language=None, task="transcribe"
            )
            transcript = result_whisper['text'].strip()

            try:
                os.unlink(tmp_path)
            except:
                pass

            if len(transcript) < 8:
                continue

            result = classify_text(transcript)

            # Terminal output
            label_str = "🚨 SCAM  " if result['label'] == 'scam' else "✅ NORMAL"
            print(f"{label_str} | {int(result['score']*100):3d}% | "
                  f"ML:{result['ml_score']:5.1f}% | "
                  f"Risk:{result['risk']:6s} | "
                  f"{transcript[:70]}")

            if result['triggered_phrases']:
                print(f"         ↳ Phrases: {result['triggered_phrases']}")

            # Trigger alert
            if (result['label'] == 'scam'
                    and result['risk'] in ['HIGH', 'MEDIUM']
                    and not alert_shown):
                print("🚨 ALERT TRIGGERED!")
                threading.Thread(
                    target=show_alert,
                    args=(result, transcript),
                    daemon=True
                ).start()

        except queue.Empty:
            continue
        except Exception as e:
            print(f"Processing error: {e}")

# ── MAIN CONTROL PANEL ───────────────────────────────────────
def show_control_panel():
    root = tk.Tk()
    root.title("Digital Arrest Shield")
    root.geometry("420x320")
    root.configure(bg="#0a0f1e")
    root.resizable(False, False)

    title_font  = tkfont.Font(family="Arial", size=16, weight="bold")
    status_font = tkfont.Font(family="Arial", size=11)
    btn_font    = tkfont.Font(family="Arial", size=12, weight="bold")

    tk.Label(root, text="🛡️  Digital Arrest Shield",
             font=title_font, bg="#0a0f1e", fg="#00ff88").pack(pady=20)

    status_var = tk.StringVar(value="● LISTENING ACTIVE")
    tk.Label(root, textvariable=status_var,
             font=status_font, bg="#0a0f1e", fg="#00ff88").pack()

    tk.Label(root,
             text=f"Whisper: {WHISPER_MODEL}  |  Chunk: {CHUNK_SECONDS}s  |  Device: {DEVICE_INDEX}",
             font=status_font, bg="#0a0f1e", fg="#555577").pack(pady=4)

    tk.Label(root, text="Monitoring all system audio...",
             font=status_font, bg="#0a0f1e", fg="#aaaaaa").pack(pady=8)

    tk.Label(root,
             text="Alert triggers on HIGH or MEDIUM risk scam phrases",
             font=status_font, bg="#0a0f1e", fg="#888866",
             wraplength=380).pack(pady=4)

    def stop_detection():
        global is_running
        is_running = False
        status_var.set("● DETECTION STOPPED")
        root.configure(bg="#1a0000")
        print("\n⛔ Detection stopped.")

    tk.Button(root, text="⛔  Stop Detection",
              font=btn_font, bg="#CC0000", fg="#FFFFFF",
              width=20, command=stop_detection).pack(pady=20)

    root.mainloop()

# ── ENTRY POINT ───────────────────────────────────────────────
if __name__ == "__main__":
    record_thread = threading.Thread(target=record_audio, daemon=True)
    record_thread.start()

    process_thread = threading.Thread(target=process_audio, daemon=True)
    process_thread.start()

    show_control_panel()

    print("\n👋 Digital Arrest Shield stopped. Stay safe!")