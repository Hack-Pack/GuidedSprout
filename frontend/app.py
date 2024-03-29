import sys
from pathlib import Path
import csv
import pandas as pd
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import streamlit as st
from utils import *
from backend.main import *




# FILE PATHS
PROMPT_PATH = "prompts/csv_promt.txt"
CSV_PATH = "backend/out.csv"
STUDENT_IMAGES = "data/student_images"
INSTRUCTOR_IMAGES = "data/instructor_images"
DEFAULT_IMAGE_PATH = "frontend/testing_data/placeholder.png"
VOICE_TESTING = "backend/speech.mp3"
LOGO = "frontend/testing_data/logo.jpeg"
FAVICON = "frontend/testing_data/logo.png"

# Initialize state variables if not already present
if "student_images_paths" not in st.session_state:
    st.session_state.student_images_paths = []

if "instructor_images_path" not in st.session_state:
    st.session_state.instructor_images_path = []

# Set wide mode
st.set_page_config(page_title="Guided Sprout", page_icon=FAVICON , layout="wide")

st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage], [data-testid=stSidebar] .markdown-text-container {
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        [class*="st-"] p {
            font-size: 16px;
        }
        [class*="st-"] span {
            font-size: 25px;
        }
        .toast-message {
            background-color: #F3E7D0;
            color: black;
            border-radius: 8px;
            padding: 20px 50px;
            position: fixed;
            bottom: 130px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            animation: fadeOut 3s ease-in-out forwards;
        }
        @keyframes fadeOut {
            0% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                opacity: 0;
                display: none;
            }
        }
        .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True
)

with st.sidebar:
    st.image(LOGO, width=300)  # Placeholder for a logo

        # Page navigation
    page = st.selectbox("Choose a page", ["Homepage", "Table"])

    with st.expander("Upload Section", expanded=False):  
        # Now, use regular st commands for widgets inside the expander
        uploaded_assignments = st.file_uploader(
            "Upload Assignments", accept_multiple_files=True, type=None
        )  # You can specify types with the 'type' parameter
        if uploaded_assignments:
            st.write("You have uploaded a file.")

        uploaded_rubric = st.file_uploader(
            "Upload Rubric", type=None
        )  # You can specify types with the 'type' parameter

        # The button should just be st.button(), not st.sidebar.button()
        if st.button("Upload Files"):
            if uploaded_assignments and uploaded_rubric:
                for uploaded_assignment in uploaded_assignments:
                    st.session_state.student_images_paths += save_uploaded_file(
                        uploaded_assignment, "data/student_images"
                    )

                st.session_state.instructor_images_path += save_uploaded_file(
                    uploaded_rubric, "data/instructor_images"
                )

                process_images(STUDENT_IMAGES, INSTRUCTOR_IMAGES, PROMPT_PATH, CSV_PATH)

                st.write("Files have been successfully uploaded.")




if page == "Homepage":
    col1, col2 = st.columns(2)
    with col1:
        tab1, tab2 = st.tabs(["Student Images", "Instructor Images"])

        with tab1:
            display_images(
                st.session_state.student_images_paths, DEFAULT_IMAGE_PATH, "Student"
            )

        with tab2:
            display_images(
                st.session_state.instructor_images_path,
                DEFAULT_IMAGE_PATH,
                "Instructor",
            )
            
    with col2:
        tab1, tab2 = st.tabs(["Evaluation", "Feedback"])
        with tab1:
            # Create an empty placeholder
            text_placeholder = st.empty()
            evaluate_button_placeholder = st.empty()

            # Use the placeholder to display the button
            if evaluate_button_placeholder.button("Evaluate"):
                # Clear the placeholder, making the button disappear
                evaluate_button_placeholder.empty()
                results = ""
                with open(CSV_PATH, mode="r", encoding="utf-8") as csv_file:
                    # Create a CSV reader object from the file object
                    csv_reader = csv.DictReader(csv_file)
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Iterate over each row in the CSV
                    counter = 0
                    for row in csv_reader: 
                        counter += 1
                        if counter > 4: break                      
                        question_id = row["question_id"]
                        question = row["question"]
                        student_answer = row["student_answer"]
                        instructor_answer = row["instructor_answer"]
                                                
                        status_text.text(f'Evaluating Question No: {question_id}')
                        evaluation_text, is_correct = evaluate_question(
                            question_id, question, student_answer, instructor_answer
                        )
                                                
                        # Choose color based on correctness
                        color = "green" if is_correct else "orange"
                        if is_correct:
                            time.sleep(2)
                            
                        question_placeholder = st.empty()
                        results = f"<br><strong>Question No: {question_id}</strong><br><span style='color: {color};'>{evaluation_text}</span><br>"
                        progress_bar.progress(int(question_id)*25)
                        status_text.text(f'Evaluated Question No: {question_id}')
                        # st.toast(f'Evaluated Question No: {question_id}', icon='🪄') 

                        # Display the toast message
                        st.markdown(f'<div class="toast-message"> <b>🪄 &nbsp; Evaluated Question No: {question_id} </b></div>', unsafe_allow_html=True)                                        

                        # Use st.markdown to render the HTML
                        text_placeholder.markdown(results, unsafe_allow_html=True)
                    
                    time.sleep(3)
                    status_text.text('Evaluation Done!')                    
                    st.markdown('<div class="toast-message"> <b> Hooray! &nbsp; 🎉  <b> </div>', unsafe_allow_html=True)
                                        
            with tab2:
                bool_speech_show = 0
                if st.button("Generate Feedback "):
                    res = run_tts()
                    rec_questions = top_k_matched_questions("Simplify the expression 2x^2 - 8 / x - 2", k=5)
                    questions_id_list = [int(question.split('.')[0]) for question in rec_questions]
                    questions_text_list = ['.'.join(question.split('.')[1:]).strip() for question in rec_questions]
                    bool_speech_show = 1


                text_placeholder = st.empty()
                
                # TODO: TTS
                # Adding an audio player
                if bool_speech_show:
                    st.write("Listen to your assignment feedback!")
                    
                    audio_file = open(
                        VOICE_TESTING, "rb"
                    )
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3", start_time=0)

                    with st.expander("Audio Transcript", expanded=False):
                        text_placeholder_audio_transcript = st.empty()
                        text_placeholder_audio_transcript.markdown(res, unsafe_allow_html=True)
                
                    results = "🌟 Here are the recommended questions for improvement! Let's dive in and explore 🚀<ul>"
                    for question_number, question_text in zip(questions_id_list, questions_text_list):
                        results += f"<li><strong>Question 3.{question_number}:</strong> {question_text}</li>"  
                    results += "</ul>✨ Keep up the great work, and remember, every question is a step towards mastery! 📚"
                    text_placeholder.markdown(results, unsafe_allow_html=True)

    


elif page == "Table":
    st.title("Table")
    df = pd.read_csv(CSV_PATH)
    st.dataframe(df)
