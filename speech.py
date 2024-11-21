import streamlit as st
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import threading

# Set up the Gemini Flash model
GEMINI_API_KEY = "AIzaSyCU6AUNuasUZiiwT6PAjLbnflrnfYfNjWM"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Set up speech recognition
recognizer = sr.Recognizer()

# Set up text-to-speech
engine = pyttsx3.init()

def listen_to_speech():
    """Capture speech and return recognized text."""
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            st.write(f"Recognized speech: {text}")
            return text
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            st.write("Sorry, there was a request error with the API.")
            return None

def generate_llm_response(prompt):
    """Send the prompt to the Gemini model and get the response."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.write(f"Error in generating response: {e}")
        return None

def speak_text(text):
    """Convert text to speech and speak it out in a separate thread."""
    def run_tts():
        engine.say(text)
        engine.runAndWait()

    # Create a new thread for the TTS operation
    tts_thread = threading.Thread(target=run_tts)
    tts_thread.start()

# Initialize the conversation state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Streamlit UI
st.title("Speech-to-Speech LLM Bot")

if st.button("Start Conversation"):
    # Listen to speech input
    input_text = listen_to_speech()
    
    if input_text:
        st.session_state.conversation_history.append(f"You: {input_text}")

        # Generate response from the LLM
        response = generate_llm_response(input_text)
        
        if response:
            st.session_state.conversation_history.append(f"Bot: {response}")
            speak_text(response)
    
    # Display conversation history
    for msg in st.session_state.conversation_history:
        st.write(msg)

# Option to reset the conversation
if st.button("Reset Conversation"):
    st.session_state.conversation_history = []
    st.write("Conversation reset.")