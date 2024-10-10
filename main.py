import asyncio
import edge_tts
import io
import pygame
import speech_recognition as sr
from rich import print
from transformers import pipeline
import wikipedia
import random
import time

# Load the emotion detection model
emotion_pipeline = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

# Define jokes and motivational quotes
jokes = [
    "Why don’t skeletons fight each other? They don’t have the guts! 🤣",
    "I told my computer I needed a break, and now it won’t stop sending me Kit-Kats! 🍫",
    "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
    "I would tell you a joke about time travel, but you didn’t like it! 🕰️",
    "How does a penguin build its house? Igloos it together! 🐧",
    "I’m reading a book about anti-gravity. It’s impossible to put down! 📖",
    "What do you call fake spaghetti? An impasta! 🍝",
    "Why did the bicycle fall over? Because it was two-tired! 🚴",
    "I used to play piano by ear, but now I use my hands! 🎹",
    "What did the janitor say when he jumped out of the closet? Supplies! 🧹"
]

motivational_quotes = [
    "The harder you work for something, the greater you'll feel when you achieve it! 💪",
    "Don’t watch the clock; do what it does. Keep going! 🕒",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. 💪",
    "Great things never come from comfort zones. Push yourself! 🚀",
    "Don’t stop when you’re tired. Stop when you’re done! 🏁",
    "Believe you can and you're halfway there. 🌟",
    "Dream big and dare to fail. 🌠",
    "Challenges are what make life interesting, overcoming them is what makes life meaningful. 🌈",
    "Your limitation—it’s only your imagination. 🌟",
    "Push yourself, because no one else is going to do it for you! 💪"
]

# Function to fetch the audio bytes using Edge TTS
async def fetchAudio(text, assistantVoice="en-US-EricNeural", pitch='+0Hz', rate='+0%') -> bytes:
    try:
        communicate = edge_tts.Communicate(text, assistantVoice, pitch=pitch, rate=rate)
        audioBytes = b""
        async for element in communicate.stream():
            if element["type"] == 'audio':
                audioBytes += element["data"]
        return audioBytes
    except Exception as e:
        print(f"Error in fetching audio: {e}")
        return b""

# Text-to-speech function
async def textToSpeechBytes(text: str, assistantVoice="en-US-EricNeural") -> bytes:
    try:
        return await fetchAudio(text, assistantVoice)
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return b""

# Class to play audio
class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.channel = None
        self.sound = None

    def play(self, audio_bytes: bytes) -> None:
        audio_file = io.BytesIO(audio_bytes)
        self.sound = pygame.mixer.Sound(audio_file)

        if self.channel and self.channel.get_busy():
            self.channel.stop()

        self.channel = self.sound.play()

    def stop(self) -> None:
        if self.channel and self.channel.get_busy():
            self.channel.stop()

# Jarvis startup sequence
async def start_jarvis():
    player = AudioPlayer()
    intro_text = "Hey, thanks for waking me up. I am Jarvis, on duty."
    print(intro_text)
    audio_bytes = await textToSpeechBytes(intro_text)
    player.play(audio_bytes)

    # Wait until the introduction message finishes playing
    while player.channel and player.channel.get_busy():
        await asyncio.sleep(0.5)

# Emotion detection function
def detect_emotion(text):
    result = emotion_pipeline(text)
    return result[0]['label']

# Function to listen for voice input
def listen_to_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
            return ""

# Function to respond based on the detected emotion
def respond_based_on_emotion(emotion, is_factual=False):
    if is_factual:
        return ""

    responses = {
        'joy': f"That's fantastic! Keep the good vibes going! 😄 Here's something to make your day brighter: {random.choice(jokes)}",
        'sadness': f"Hey, I know things are tough right now, but here's a motivational thought: {random.choice(motivational_quotes)}",
        'anger': "Take a deep breath, relax, and let me know how I can help! 😊",
        'fear': "Everything will be okay. Just take it one step at a time! 💖",
        'surprise': "Wow, that sounds exciting! Tell me more about it! 🎉",
        'disgust': "Let's shift focus to something more positive. How can I assist you today?"
    }
    return responses.get(emotion, "I'm here to chat! How can I assist you today?")

# Wikipedia search function for answering factual questions
def get_wikipedia_answer(question):
    try:
        summary = wikipedia.summary(question, sentences=1)
        return summary
    except Exception as e:
        return "Sorry, I couldn't find any information on that."

# Main function
async def main():
    player = AudioPlayer()
    print("Listening...")

    is_speaking = False

    while True:
        while is_speaking:
            await asyncio.sleep(0.5)

        command = listen_to_voice()
        if command == "exit":
            print("Exiting the program...")
            break

        emotion = detect_emotion(command)
        is_question = any(command.startswith(starter) for starter in ["what", "who", "where", "when", "why"])

        if is_question:
            response_text = get_wikipedia_answer(command)
        elif emotion:
            emotion_response = respond_based_on_emotion(emotion, is_factual=False)
            response_text = emotion_response
        else:
            response_text = "I'm here to chat! How can I assist you today?"

        print(f"Jarvis: {response_text}")

        is_speaking = True

        audio_bytes = await textToSpeechBytes(response_text.replace("💖", "").replace("😄", "").replace("💪", ""))
        if audio_bytes:
            player.play(audio_bytes)

        while player.channel and player.channel.get_busy():
            await asyncio.sleep(0.5)

        is_speaking = False

# Start Jarvis and run the main loop
if __name__ == "__main__":
    asyncio.run(start_jarvis())  # Play the intro message
    try:
        asyncio.run(main())  # Start the main loop after intro
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")
