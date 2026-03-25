# # import pyttsx3

# # def text_to_speech_offline(text):
# #     """
# #     Converts the given text to speech offline using pyttsx3.
# #     """
# #     try:
# #         # Initialize the text-to-speech engine
# #         engine = pyttsx3.init()

# #         # Optional: Adjust speech properties (rate, volume, voice)
# #         # rate = engine.getProperty('rate')
# #         # engine.setProperty('rate', 150) # Speed in words per minute (WPM)
# #         # volume = engine.getProperty('volume')
# #         # engine.setProperty('volume', 0.9) # Volume (0.0 to 1.0)
# #         # voices = engine.getProperty('voices')
# #         # engine.setProperty('voice', voices[1].id) # Change index for different voices (e.g., male/female)

# #         # Queue the text for speaking
# #         engine.say(text)

# #         # Process and output the speech (speak it aloud)
# #         engine.runAndWait()

# #         # Stop the engine after speaking is done
# #         engine.stop()

# #     except Exception as e:
# #         print(f"Error: {e}")

# # # Example usage:
# # input_text = "Hello i am calling from rachagonda police station and this call is being done because we faund a parcel that was on your son's name and he will put in jail for 10 years. this is a warning you have to pay rupees 2lakhs to reduce the duration of the imprisonment and if you pay 5 lakhs you may be free without any jail. pay immediately  you wil be sent a link click on it and process the amount."
# # text_to_speech_offline(input_text)
# import pyttsx3

# def text_to_speech_file(text, filename="output.wav"):
#     try:
#         engine = pyttsx3.init()

#         # Save to file instead of speaking
#         engine.save_to_file(text, filename)
#         engine.runAndWait()

#         print(f"Saved audio to {filename}")

#     except Exception as e:
#         print(f"Error: {e}")

# # Example safe text
# input_text = "Hello i am calling from rachagonda police station and this call is being done because we faund a parcel that was on your son's name and he will put in jail for 10 years. this is a warning you have to pay rupees 2lakhs to reduce the duration of the imprisonment and if you pay 5 lakhs you may be free without any jail. pay immediately  you wil be sent a link click on it and process the amount."

# text_to_speech_file(input_text)

from pydub import AudioSegment

sound = AudioSegment.from_wav("output.wav")
sound.export("output.mp3", format="mp3")

print("Converted to MP3!")