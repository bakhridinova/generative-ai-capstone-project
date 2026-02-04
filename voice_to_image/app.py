import streamlit as st
import os
from dotenv import load_dotenv
from agent import AudioToImagePipeline
from utils import setup_logging, format_file_size, validate_audio_format
import openai
from openai import OpenAI
from audio_recorder_streamlit import audio_recorder


app_logger = setup_logging()
load_dotenv()
app_logger.info("Voice to Image Tool launched")

st.set_page_config(
    page_title="Voice to Image Tool",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #4A90E2;
        margin-bottom: 2rem;
    }
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
    }
    div[data-testid="stVerticalBlock"] > div {
        display: flex;
        flex-direction: column;
        align-items: left;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ Voice to 🌄 Image Tool")

st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")

    api_key_env = os.getenv("OPENAI_API_KEY", "")

    if api_key_env:
        st.session_state["api_key"] = api_key_env
    else:
        if "api_key" in st.session_state:
            del st.session_state["api_key"]

    st.divider()

    st.markdown("""
    Supported audio formats:
    
        MP3 (.mp3)
        MP4 (.mp4)
        WebM (.webm)
    """)


st.subheader("Choose Your Input Method")

st.space()

if st.button("🎙️ Record Audio", use_container_width=True, type="primary"):
    st.session_state["input_method"] = "record"
    app_logger.info("User selected: Record Audio")

st.space()

if st.button("📂 Upload Audio File", use_container_width=True, type="secondary"):
    st.session_state["input_method"] = "upload"
    app_logger.info("User selected: Upload Audio")

selected_method = st.session_state.get("input_method", None)


def execute_audio_to_image_pipeline(audio_data: bytes, audio_name: str = "audio.wav"):

    if "api_key" not in st.session_state or not st.session_state["api_key"]:
        st.error("API key required. Please configure it in the sidebar.")
        return
    
    try:
        pipeline = AudioToImagePipeline(st.session_state["api_key"])
        app_logger.info("Pipeline initialized - starting audio-to-image conversion")

        with st.status("🎧 Transcribing audio...", expanded=False) as status:
            transcription_result = pipeline.convert_speech_to_text(audio_data, audio_name)

        st.markdown(f"**Your spoken words:** {transcription_result}")

        st.session_state["last_transcript"] = transcription_result

        optimized_description = pipeline.optimize_for_image_generation(transcription_result)

        with st.status("🎨 Creating image...", expanded=False) as status:
            st.caption("This typically takes 30-60 seconds")
            image_data = pipeline.synthesize_image(optimized_description)

        st.image(image_data, width=600)

        st.session_state["last_image"] = image_data

        st.download_button(
            label="⬇️ Download Image (PNG)",
            data=image_data,
            file_name=f"{transcription_result}.png",
            mime="image/png",
            use_container_width=True,
            type="primary"
        )


        app_logger.info("Pipeline execution completed successfully")

    except Exception as pipeline_error:
        app_logger.error(f"Pipeline error: {pipeline_error}", exc_info=True)
        st.error(f"❌ Error: {str(pipeline_error)}")



if selected_method == "record":
    st.markdown("---")
    st.subheader("🎙️ Record Audio")

    recorded_audio = audio_recorder(
        text="Click to start recording",
        recording_color="#e74c3c",
        neutral_color="#3498db",
        icon_name="microphone",
        icon_size="3x",
        pause_threshold=2.0
    )

    if recorded_audio:
        audio_size = len(recorded_audio)
        app_logger.info(f"Audio captured | Size: {audio_size} bytes")

        st.success(f"✅ Recording captured ({format_file_size(audio_size)})")

        st.audio(recorded_audio, format="audio/wav")

        st.session_state["current_audio"] = recorded_audio

        st.markdown("---")

        if st.button(
            "🚀 Generate Image",
            use_container_width=True,
            type="primary"
        ):
            execute_audio_to_image_pipeline(recorded_audio, "live_recording.wav")


elif selected_method == "upload":
    accepted_formats = ['mp3', 'mp4', 'webm']

    audio_file = st.file_uploader(
        "Select an audio file",
        type=accepted_formats,
        accept_multiple_files=False
    )
    
    if audio_file is not None:
        if not validate_audio_format(audio_file.name):
            st.error(f"❌ Unsupported format. Please use: {', '.join(accepted_formats).upper()}")
            st.stop()

        file_ext = audio_file.name.split('.')[-1].lower()
        file_size_bytes = audio_file.size

        app_logger.info(f"File uploaded | Name: {audio_file.name} | Size: {file_size_bytes}")

        st.success(f"✅ File uploaded: {audio_file.name} ({format_file_size(file_size_bytes)})")

        st.audio(audio_file, format=f"audio/{file_ext}")

        st.session_state["uploaded_audio_file"] = audio_file

        st.markdown("---")
        if st.button(
            "🚀 Generate Image",
            use_container_width=True,
            type="primary"
        ):
            audio_file.seek(0)
            file_data = audio_file.read()
            execute_audio_to_image_pipeline(file_data, audio_file.name)
