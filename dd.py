import asyncio
import speech_recognition as sr
import pyttsx3
import g4f

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Initialize the recognizer and text-to-speech engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Default names
user_name = "Zamani"
assistant_name = "Jarvis"

# Conversation history to remember past interactions
conversation_history = [
    {"role": "system", "content": f"You are {assistant_name}, a helpful assistant."}
]

def speak(text):
    """Convert text to speech."""
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen():
    """Listen to microphone input and return as text."""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio)
            print(f"{user_name} said: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Sorry, my speech service is down.")
            speak("Sorry, my speech service is down.")
            return None

def ask_g4f(question):
    """Send a question to the assistant and return the response."""
    global conversation_history

    # Add the user's question to the conversation history
    conversation_history.append({"role": "user", "content": question})
    
    # Make the request with the updated conversation history
    response = g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or another model supported by g4f
        messages=conversation_history,
    )

    # Process and return the response
    if isinstance(response, str):
        return response.strip()
    elif isinstance(response, dict) and 'choices' in response:
        return response['choices'][0]['message']['content'].strip()
    else:
        return "Sorry, I didn't get a proper response."

def main():
    """Main function to run the voice assistant."""
    global user_name, assistant_name, conversation_history
    
    speak(f"Hello {user_name}, how can I help you today?")
    
    while True:
        question = listen()
        if question:
            if "change my name to" in question.lower():
                user_name = question.split("to")[-1].strip()
                speak(f"Okay, I'll call you {user_name} from now on.")
                conversation_history.append({"role": "user", "content": f"My name is now {user_name}."})
            
            elif f"change your name to" in question.lower():
                assistant_name = question.split("to")[-1].strip()
                speak(f"Okay, you can call me {assistant_name} from now on.")
                conversation_history[0] = {"role": "system", "content": f"You are {assistant_name}, a helpful assistant."}
            
            else:
                response = ask_g4f(question)
                print(f"{assistant_name} says: {response}")
                speak(response)
                # Add the assistant's response to the conversation history
                conversation_history.append({"role": "assistant", "content": response})
        else:
            speak("Please try asking your question again.")

if __name__ == "__main__":
    main()
