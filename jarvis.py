import speech_recognition as sr
import webbrowser
import requests
import pyttsx3
from pytube import Search
import openai
import datetime
import os
import json
# object for speech recognition and tex to speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()
COMMANDS_FILE = "commands.json"
# API Keys
OPENAI_API_KEY = "your-api-key-here"
WEATHER_API_KEY = "your-weather-api-key"
NEWS_API_KEY = "your-news-api-key"
DEFAULT_COMMANDS = {
    "search": ["search for","search ", "what's the meaning of", "who is", "how to", "tell me about"],
    "weather": ["what's the weather like", "weather report"],
    "news": ["latest news", "news update" , "news"],
    "reminder": ["set a reminder", "remind me","can you remind me about"],
    "get_reminder": ["what are my reminders", "show reminders"],
    "greet": ["say hello", "introduce yourself"],
    "calculate" : ["what's", "calculate"],
    "open" : ["open" ,],
    "play" : ["play " , "youtube"],
    "command" : ["change command"]
}

# Load or initialize command mappings
def load_commands():
    if os.path.exists(COMMANDS_FILE):
        with open(COMMANDS_FILE, "r") as file:
            return json.load(file)
    return DEFAULT_COMMANDS


commands = load_commands()
print(commands.values())
reminders = []

def change_command(command):
    for key, phrases in commands.items():
        for phrase in phrases:
            if command.startswith(phrase):
                old_c = command[len(phrase):].strip()
                break
    key_to_update = None
    for key, values in commands.items():
        if old_c in values:
            key_to_update = key
            break

    if key_to_update:
        speak("Say the new command")
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            new_command = recognizer.recognize_google(audio).lower()
            print(f"new command : {new_command}")

        # Update the command list
        commands[key_to_update].remove(old_c)
        commands[key_to_update].append(new_command)

        # Save back to file
        with open(COMMANDS_FILE, "w") as file:
            json.dump(commands, file, indent=4)

        speak(f"Command changed to {new_command}")
    else:
        speak("Command not found in list.")


def speak(text):
    # Converts text to speech.
    engine.say(text)
    engine.runAndWait()

def ai_process(command):
    # Processes the command using OpenAI GPT.
    openai.api_key = OPENAI_API_KEY

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a virtual assistant like Google Assistant or Siri."},
                {"role": "user", "content": command}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Error in AI processing: {e}"

def get_weather(command):
    # Fetches weather news for a specified city
    city = None
    for phrase in commands["weather"]:
        if command.startswith(phrase):
            city = command[len(phrase):].strip()
            break
    if city:
        try:
            city = command.split("in")[-1].strip()
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url).json()

            if response["cod"] == 200:
                temp = response["main"]["temp"]
                description = response["weather"][0]["description"]
                speak(f"The weather in {city} is {description} with a temperature of {temp}°C.")
            else:
                speak("Sorry, I couldn't fetch the weather data. Check the city name.")
        except Exception as e:
            speak("There was an error fetching the weather.")

def get_news(command):
    # Fetches and reads the top news headlines
    for phrase in commands["news"]:
        if command.startswith(phrase):
            try:
                url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
                response = requests.get(url).json()
                articles = response["articles"][:5]  # Get top 5 news articles

                speak("Here are today's top news headlines:")
                for i, article in enumerate(articles, 1):
                    speak(f"Headline {i}: {article['title']}")
            except Exception as e:
                speak("Sorry, I couldn't fetch the news at the moment.")

def add_reminder(command):
    # adding reminders :
    for phrase in commands["reminder"]:
        if command.startswith(phrase):
            reminder_text = command[len(phrase):].strip()  # Extract only the actual search query
            break
    if reminder_text:
        reminders.append(reminder_text)
        speak(f"Reminder added: {reminder_text}")
    else:
        speak("Please specify what you want me to remind you about.")

def get_reminders(command):
    # reading saved reminders.
    for phrase in commands["get_reminder"]:
        if command.startswith(phrase):
            speak("Here are your reminders:")
            for reminder in reminders:
             speak(reminder)
        else:
            speak("You have no reminders set.")

def personalized_greeting():
    # Greeting according to time of day
    hour = datetime.datetime.now().hour

    if hour < 12:
        greeting = "Good morning!"
    elif 12 <= hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"

    speak(f"hello {greeting}  Jarvis here how can i assist you today")

def calculate(command):
    # Performs basic arithmetic calculations
    for phrase in commands["calculate"]:
        if command.startswith(phrase):
            expression = command[len(phrase):].strip()
            break
    try:
        parts = expression.split()
        num1 = float(parts[0])
        operator = parts[1]
        num2 = float(parts[2])

        operations = {
            "+": num1 + num2,
            "-": num1 - num2,
            "*": num1 * num2,
            "/": round(num1 / num2, 2) if num2 != 0 else "Cannot divide by zero"
        }

        result = operations.get(operator, "Invalid operation")
        speak(f"The result is {result}")
    except (IndexError, ValueError):
        speak("Invalid calculation format. Try: 'calculate 5 + 3'.")

def google_search(command):
    # Searches Google for the given command.
    for phrase in commands["search"]:
        if command.startswith(phrase):
            query = command[len(phrase):].strip()  # Extract only the actual search query
            break
    if query:
        speak(f"Searching for {query}")
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
    
def play_youtube(command):
    # Plays the first YouTube search result
    for phrase in commands["play"]:
        if command.startswith(phrase):
            query = command[len(phrase):].strip()
            break
    if query:
        speak(f"Searching YouTube for {query}")
        try:
            url = Search(query).results[0].watch_url
            webbrowser.open(url)
        except IndexError:
            speak("No results found on YouTube.")
    else:
        speak("Please specify a song or video.")

def open_website(command):
    # Opens a website based on command.
    for phrase in commands["open"]:
        if command.startswith(phrase):
            website = command[len(phrase):].strip()
            break
    if website:
        try:
            link = f"https://{website}.com"
            speak(f"Opening {website}")
            webbrowser.open(link)
        except IndexError:
            speak("Please specify a website.")
def execute_command(command):
    # processes and executes user commands.
    command = command.lower()
    if any(command.startswith(phrase) for phrase in commands["search"]):
        google_search(command)

    # Opening websites
    elif any(command.startswith(phrase) for phrase in commands["open"]):
         open_website(command)

    # Calculations
    elif any(command.startswith(phrase) for phrase in commands["calculate"]):
        calculate(command)

    # Play YouTube videos
    elif any(command.startswith(phrase) for phrase in commands["play"]):
        play_youtube(command)
    # Set Reminder
    elif any(command.startswith(phrase) for phrase in commands["reminder"]):
        add_reminder(command)

    # Weather updates
    elif any(command.startswith(phrase) for phrase in commands["weather"]):
        get_weather(command)
    
    elif any(command.startswith(phrase) for phrase in commands["get_reminder"]):
        get_reminders(command)

    # News updates
    elif any(command.startswith(phrase) for phrase in commands["news"]):
        get_news(command)

    # Personal Greeting
    elif any(command.startswith(phrase) for phrase in commands["greet"]):
        for phrase in commands["greet"]:
            if command.startswith(phrase):
              personalized_greeting()
    # Change custom commands
    elif "change command" in command:
        #  say change command _ the command to change
        change_command(command)

    elif command in ["exit", "stop"]:
        speak("Goodbye Have a great day.")
        exit()
    else: 
        response = ai_process(command)
        print(response)
        speak(response)

if __name__ == "__main__":
    personalized_greeting()
    
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source)
                print("Jarvis is listening...")
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()
                print(f"Command: {command}")
                execute_command(command)

        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print(f"Speech recognition request error: {e}")
        except Exception as e:
            print(f"Error: {e}")
