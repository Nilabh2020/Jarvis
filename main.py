import asyncio
import edge_tts
import io
import pygame
import speech_recognition as sr
from rich import print
from transformers import pipeline
import wikipedia
import random

emotion_pipeline = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

jokes = [
    "Why don’t skeletons fight each other? They don’t have the guts! 🤣",
    "I told my computer I needed a break, and now it won’t stop sending me Kit-Kats! 🍫",
    "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
    "Parallel lines have so much in common. It’s a shame they’ll never meet! 🤔",
    "Why don’t eggs tell jokes? Because they might crack up! 🥚",
    "I would tell you a chemistry joke, but I know I wouldn’t get a reaction. 🧪",
    "I’m reading a book on anti-gravity. It’s impossible to put down! 📚",
    "What do you call fake spaghetti? An impasta! 🍝",
    "Want to hear a joke about construction? I’m still working on it! 🏗️",
    "Did you hear about the mathematician who’s afraid of negative numbers? He’ll stop at nothing to avoid them. ➖",
    "Why couldn’t the bicycle stand up by itself? It was two-tired! 🚴‍♂️",
    "What did one ocean say to the other ocean? Nothing, they just waved! 🌊",
    "Why don’t some fish play basketball? Because they’re afraid of the net! 🐟",
    "How does a penguin build its house? Igloos it together! 🐧",
    "What do you call cheese that isn't yours? Nacho cheese! 🧀",
    "Why did the coffee file a police report? It got mugged! ☕",
    "What’s orange and sounds like a parrot? A carrot! 🥕",
    "Why did the golfer bring two pairs of pants? In case he got a hole in one! ⛳",
    "Why don’t programmers like nature? It has too many bugs! 🐛",
    "I ate a clock yesterday, it was very time-consuming! 🕰️",
]

motivational_quotes = [
    "The harder you work for something, the greater you'll feel when you achieve it! 💪",
    "Don’t watch the clock; do what it does. Keep going! 🕒",
    "Success is not the key to happiness. Happiness is the key to success! 🎯",
    "Believe you can and you’re halfway there! 🌟",
    "Your limitation—it’s only your imagination! 🚀",
    "Push yourself, because no one else is going to do it for you! 👊",
    "Dream it. Wish it. Do it! ✨",
    "Great things never come from comfort zones! 🏆",
    "Don’t stop when you’re tired. Stop when you’re done! 🛑",
    "Wake up with determination. Go to bed with satisfaction! 😌",
    "The way to get started is to quit talking and begin doing! 💡",
    "Little by little, day by day, what is meant for you will find its way! 🌿",
    "Success doesn’t come from what you do occasionally, it comes from what you do consistently! 🏅",
    "If you want to fly, you have to give up what weighs you down! 🦋",
    "You are capable of amazing things! 🌈",
    "Believe in yourself and all that you are! 💖",
    "Do something today that your future self will thank you for! 🕊️",
    "Difficult roads often lead to beautiful destinations! 🚴‍♂️",
    "You are braver than you believe, stronger than you seem, and smarter than you think! 🦸‍♂️",
    "Keep your face always toward the sunshine, and shadows will fall behind you! 🌞",
]

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

async def textToSpeechBytes(text: str, assistantVoice="en-US-EricNeural") -> bytes:
    try:
        return await fetchAudio(text, assistantVoice)
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return b""

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

def detect_emotion(text):
    result = emotion_pipeline(text)
    return result[0]['label']

def respond_based_on_emotion(emotion, is_factual=False):
    if is_factual:
        return ""

    responses = {
        'joy': f"That's fantastic! Keep the good vibes going! 😄 Here's something to make your day brighter: {random.choice(jokes)}",
        'sadness': f"Hey, I know things are tough right now, but here's a motivational thought: {random.choice(motivational_quotes)}",
        'anger': f"Whoa, deep breath. Let’s cool down. How about a quick laugh? {random.choice(jokes)}",
        'surprise': f"Whoa! Didn’t see that coming! Here’s a fun fact for you: {random.choice(jokes)}",
        'fear': f"I understand you’re feeling uneasy. Let’s stay calm. Here's some motivation: {random.choice(motivational_quotes)}",
        'love': f"Aww, love is in the air! Spread those good vibes! 💖",
    }
    return responses.get(emotion, "I'm here to chat! How can I assist you today?")

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

def get_wikipedia_answer(question):
    try:
        summary = wikipedia.summary(question, sentences=1)
        return summary
    except Exception as e:
        return "Sorry, I couldn't find any information on that."

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

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")
