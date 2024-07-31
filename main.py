import streamlit as st
import os
import requests
from PIL import Image
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load the logo image
logo = Image.open('images.jpg')

# Get API keys from environment variables
groq_api_key = os.getenv('GROQ_API_KEY')
weather_api_key = os.getenv('WEATHER_API_KEY')

def read_txt(file_path):
    """Reads text from a given file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text.strip()

def get_weather(city):
    """Fetches weather information for a given city."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The weather in {city} is {weather} with a temperature of {temperature}°C."
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"Other error occurred: {err}"

def main():
    col1, col2 = st.columns([2, 8])  # Adjust the column widths as needed
    
    with col1:
        st.image(logo, width=100)  # Adjust the width as needed and add a caption if necessary
    
    with col2:
        st.markdown('<p style="text-align: center;">'
                    '<h1 style="font-size: 70px; margin-top: -30px;">PineyBot</h1>'
                    '</p>', unsafe_allow_html=True)
    
    st.markdown("---")  # Adds a horizontal line as a gap
    
    model = 'llama3-8b-8192'  # Set default model
    
    # Fixed conversational memory length
    conversation_length = 10
    
    memory = ConversationBufferWindowMemory(k=conversation_length)
    user_question = st.text_area("Ask a question:")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    else:
        for message in st.session_state.chat_history:
            memory.save_context({'input': message['human']}, {'output': message['AI']})
    
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)
    conversation = ConversationChain(llm=groq_chat, memory=memory)
    
    if st.button("Ask"):
        if user_question:
            if "weather" in user_question.lower():
                if "in" in user_question.lower():
                    city = user_question.split("in")[-1].strip()
                    weather_info = get_weather(city)
                    st.write("Chatbot:", weather_info)
                else:
                    st.write("Chatbot: Please specify a city to check the weather.")
            else:
                data = read_txt('./docs/data.txt')  # Change file extension to .txt
                prompt = f"{data} {user_question}"
                response = conversation(prompt)
                message = {'human': user_question, 'AI': response['response']}
                st.session_state.chat_history.append(message)
                st.write("Chatbot:", response['response'])

if __name__ == '__main__':
    main()
