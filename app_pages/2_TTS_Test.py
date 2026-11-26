# app_pages/2_TTS_Test.py

import streamlit as st
import pyttsx3
from gtts import gTTS # type: ignore
import tempfile
import threading
import os


# ----------------------------------
# Session State
# ----------------------------------

if "tts_test_audio" not in st.session_state:
    st.session_state["tts_test_audio"] = None

if "tts_playing" not in st.session_state:
    st.session_state["tts_playing"] = False


# ----------------------------------
# English Voice Test
# ----------------------------------

def get_available_voices():

    engine = pyttsx3.init()

    voices = engine.getProperty(
        "voices"
    )

    return voices


def play_voice(
    text,
    voice_id
):

    engine = pyttsx3.init()

    engine.setProperty(
        "voice",
        voice_id
    )

    st.session_state[
        "tts_playing"
    ] = True

    engine.say(text)

    engine.runAndWait()

    st.session_state[
        "tts_playing"
    ] = False


# ----------------------------------
# Hindi Voice Test
# ----------------------------------

def create_hindi_audio(text):

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    temp_file.close()

    tts = gTTS(
        text=text,
        lang="hi"
    )

    tts.save(
        temp_file.name
    )

    return temp_file.name


# ----------------------------------
# TTS TEST PAGE
# ----------------------------------

def tts_test_page():

    st.title("🎤 Voice Testing Lab")

    st.write(
        "Test available voices before using them inside Reading Aid."
    )

    st.divider()

    language = st.selectbox(
        "Language",
        [
            "English",
            "Hindi"
        ]
    )

    sample_text = st.text_area(
        "Sample Text",
        value="Hello, welcome to Assistive Reading Aid.",
        height=200
    )

    # --------------------------
    # ENGLISH TEST
    # --------------------------

    if language == "English":

        voices = get_available_voices()

        voice_names = [
            voice.name
            for voice in voices
        ]

        selected_name = st.selectbox(
            "Available Voices",
            voice_names
        )

        selected_voice = next(
            (
                voice
                for voice in voices
                if voice.name == selected_name
            ),
            None
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "▶ Test Voice",
                use_container_width=True
            ):

                if selected_voice:

                    worker = threading.Thread(
                        target=play_voice,
                        args=(
                            sample_text,
                            selected_voice.id
                        )
                    )

                    worker.daemon = True

                    worker.start()

        with c2:

            if st.button(
                "⏹ Stop Voice",
                use_container_width=True
            ):

                try:

                    pyttsx3.init().stop()

                    st.session_state[
                        "tts_playing"
                    ] = False

                    st.success(
                        "Stopped."
                    )

                except Exception:
                    pass

    # --------------------------
    # HINDI TEST
    # --------------------------

    else:

        c1, c2, c3 = st.columns(3)

        with c1:

            if st.button(
                "▶ Play Hindi",
                use_container_width=True
            ):

                audio_file = create_hindi_audio(
                    sample_text
                )

                st.session_state[
                    "tts_test_audio"
                ] = audio_file

                with open(
                    audio_file,
                    "rb"
                ) as file:

                    audio_bytes = file.read()

                st.audio(
                    audio_bytes,
                    format="audio/mp3"
                )

        with c2:

            if st.button(
                "🔄 Replay Hindi",
                use_container_width=True
            ):

                audio_file = st.session_state.get(
                    "tts_test_audio"
                )

                if (
                    audio_file
                    and
                    os.path.exists(
                        audio_file
                    )
                ):

                    with open(
                        audio_file,
                        "rb"
                    ) as file:

                        audio_bytes = file.read()

                    st.audio(
                        audio_bytes,
                        format="audio/mp3"
                    )

                else:

                    st.warning(
                        "Play Hindi first."
                    )

        with c3:

            if st.button(
                "⏹ Stop Hindi",
                use_container_width=True
            ):

                audio_file = st.session_state.get(
                    "tts_test_audio"
                )

                if (
                    audio_file
                    and
                    os.path.exists(
                        audio_file
                    )
                ):

                    try:

                        os.remove(
                            audio_file
                        )

                    except Exception:
                        pass

                st.session_state[
                    "tts_test_audio"
                ] = None

                st.success(
                    "Hindi audio reset."
                )

    st.divider()

    st.subheader(
        "ℹ️ Notes"
    )

    st.info(
        "English voices use pyttsx3 installed on your computer."
    )

    st.info(
        "Hindi voice uses Google Text-to-Speech (gTTS)."
    )

    if st.session_state.get(
        "tts_playing",
        False
    ):

        st.success(
            "🔊 Voice currently playing"
        )

    else:

        st.info(
            "⏸ Ready for testing"
        )