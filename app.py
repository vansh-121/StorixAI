from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from gtts import gTTS
import tempfile
import re

# Load environment variables
load_dotenv()

# Configure the Google API with the provided key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load the Gemini Pro model
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to generate a strongly genre-specific story
def get_story_response(topic, story_type):
    prompt = (
        f"Write a complete {story_type.lower()} story about {topic}. "
        f"Use clear and straightforward language that a normal person can easily follow and avoid complex terms by using basic vocabulary."
        f"Make the story deeply representative of the {story_type} genre, with the proper tone, elements, and style."
        f"For example, if it's horror, make it suspenseful and frightening; if it's romantic, make it heartfelt and emotional."
        f"Make sure the story is suitable for all audiences, avoiding graphic or sensitive content."
        f"Ensure the response is respectful, gentle, without any physical intimacy or inappropriate content."
        f"Ensure the story is unique, simple languaged, easy to be understood, crisp, and fully aligned with the chosen genre."
        f"Also focus on making the story fun and clear for the reader and have a meaningful end related to the chosen genre."
    )
    
    # Send the message and get the response chunks
      
    try:
        response_chunks = chat.send_message(prompt, stream=True)
        full_response = ""

        # Check each chunk for valid text content
        for chunk in response_chunks:
            if hasattr(chunk, 'text') and chunk.text:
                full_response += chunk.text
            else:
                # If no valid text is returned, provide a simple, non-intrusive message
                return "Sorry, the story could not be generated. Please try again with a different topic or genre."

        # If full_response is still empty, handle it
        if not full_response:
            return "Sorry, no valid text was returned from the response. Please try a different topic or genre."

        return full_response

    except ValueError:
        # Handle the error silently without showing an error block
        return "This topic isn't permitted under our policies. Feel free to explore a different genre or storyline."


# Function to convert text to speech and return the audio file path
def text_to_speech(text):
    """Converts text to speech and returns the path to the audio file."""
    st.info("Generating Audio...")

    clean_text = re.sub(r'[*_~`]', '', text)
    clean_text = re.sub(r'http\S+|www\S+|https\S+', '', clean_text, flags=re.MULTILINE)

    tts = gTTS(text=clean_text, lang='en')
    temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
    tts.save(temp_file_path)

    st.success("Audio generated!")

    return temp_file_path

# Initialize Streamlit app
st.set_page_config(page_title="StoryAI - Dream Story Generator", page_icon="📚", layout="centered")

# Custom CSS for responsiveness across both light and dark modes
st.markdown("""
    <style>
    :root {
        --text-color: var(--color-text);  /* Adapt to text color based on light/dark mode */
        --primary-color: #F18DA5;        /* Accent color */
        --border-color: rgba(255, 255, 255, 0.1);  /* Soft border color that adapts */
    }
    .title-container {
        text-align: center;
        margin-bottom: 5px;
    }
    .story-box {
        padding: 15px;
        background-color: var(--background-color-primary);
        border-left: 4px solid var(--primary-color);
        border-radius: 5px;
        margin-bottom: 20px;
        color: var(--text-color);
    }
    .spaced-container {
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


st.markdown("""
    <style>
    .title-container {
        text-align: center;
        margin-bottom: 5px;
    }
    .gradient-title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class='title-container'>
        <h1 class='gradient-title'>
            <span style="color: #5A82E1;">S</span>
            <span style="color: #6D8BE6;">T</span>
            <span style="color: #7E94EA;">O</span>
            <span style="color: #8F9EEE;">R</span>
            <span style="color: #A0A7F2;">I</span>
            <span style="color: #F18DA5;">X</span>
            &nbsp;
            <span style="color: #5A82E1;">A</span>
            <span style="color: #6D8BE6;">I</span>
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)



# Header with adaptive text color and a consistent look across modes
st.markdown(
    "<div class='title-container'><h1 style='color: var(--primary-color);'>Dream. Create. Generate.</h1></div>",
    unsafe_allow_html=True
)

# Add some spacing and a subtitle, adaptive to theme colors
st.markdown("<p style='text-align: center; color: var(--text-color);'>Note: Kindly avoid using any inappropriate topics, as they will hinder the generation of the story.</p>", unsafe_allow_html=True)

# User input for topic, placed inside a container for better alignment
with st.container():
    st.markdown("<h4 class='spaced-container' style='color: var(--text-color);'>Enter your story's topic :</h4>", unsafe_allow_html=True)
    topic_input = st.text_input("Topic", placeholder="e.g., A magical forest, A detective in the city...")

# Dropdown for story type selection
st.markdown("<h4 class='spaced-container' style='color: var(--text-color);'>Choose your story's genre:</h4>", unsafe_allow_html=True)
story_type = st.selectbox(
    "Story Genre", ["Fantasy", "Realistic", "Horror", "Comedy", "Adventure", "Mystery", "Sci-Fi"]
)

# Submit button to generate the story, styled with padding
submit = st.button("Generate Story", help="Click to create your story!", use_container_width=True)

# Process user input and generate the story
if submit and topic_input:
    st.markdown("<hr>", unsafe_allow_html=True)  # Separator line for clarity
    
    # Display loader while generating the story
    with st.spinner('Generating your story...'):
        response = get_story_response(topic_input, story_type)

    # Display the generated story with a subheader and a markdown block
    st.markdown(
        f"<h2 style='color: var(--text-color);'>Your {story_type} Story</h2>", 
        unsafe_allow_html=True
    )
    st.markdown(f"<div class='story-box'>{response}</div>", unsafe_allow_html=True)

    # Convert the story to speech with a loader
    with st.spinner('Converting story to audio...'):
        audio_file_path = text_to_speech(response)
    
    audio_file = open(audio_file_path, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

    # Optional: Add a "Listen to Story" subheader
    st.markdown("<h4 style='color: var(--text-color);'>Listen to Your Story</h4>", unsafe_allow_html=True)
else:
    st.warning("Please enter a topic to generate your story.", icon="⚠️")