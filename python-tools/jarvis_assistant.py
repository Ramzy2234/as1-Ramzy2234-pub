import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty("voices")

print(f"Total voices available: {len(voices)}")

for index, voice in enumerate(voices):
    print(f"{index}: {voice.name} - {voice.id}")