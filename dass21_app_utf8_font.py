import streamlit as st
from fpdf import FPDF
import io
import os

# -------------------------
# DASS-21 Questions (7 per scale)
# -------------------------
questions = [
    # Depression
    "I couldn't seem to experience any positive feeling at all.",
    "I found it difficult to work up the initiative to do things.",
    "I felt that I had nothing to look forward to.",
    "I felt down-hearted and blue.",
    "I was unable to become enthusiastic about anything.",
    "I felt I wasn't worth much as a person.",
    "I felt that life was meaningless.",
    # Anxiety
    "I was aware of dryness of my mouth.",
    "I experienced breathing difficulty (e.g., excessively rapid breathing, breathlessness in the absence of physical exertion).",
    "I experienced trembling (e.g., in the hands).",
    "I was worried about situations in which I might panic and make a fool of myself.",
    "I felt I was close to panic.",
    "I was aware of the beating of my heart in the absence of physical exertion.",
    "I felt scared without any good reason.",
    # Stress
    "I found it hard to wind down.",
    "I tended to over-react to situations.",
    "I felt that I was using a lot of nervous energy.",
    "I found myself getting agitated.",
    "I found it difficult to relax.",
    "I was intolerant of anything that kept me from getting on with what I was doing.",
    "I felt that I was rather touchy."
]

options = {
    "Did not apply to me at all": 0,
    "Applied to me to some degree, or some of the time": 1,
    "Applied to me to a considerable degree, or a good part of the time": 2,
    "Applied to me very much, or most of the time": 3
}

# Interpretation ranges
depression_ranges = [
    (0, 9, "Normal", "Your score is within the normal range, suggesting you are not experiencing significant depressive symptoms at this time."),
    (10, 13, "Mild", "You may be experiencing some mild depressive symptoms. Monitor your wellbeing and consider self-care strategies."),
    (14, 20, "Moderate", "Your score suggests a moderate level of depressive symptoms. Consider talking with a mental health professional for support."),
    (21, 27, "Severe", "Your score indicates severe depressive symptoms. Professional support is strongly recommended."),
    (28, 42, "Extremely Severe", "Your score indicates extremely severe depressive symptoms. Immediate professional support is advised.")
]

anxiety_ranges = [
    (0, 7, "Normal", "Your score is within the normal range, suggesting minimal anxiety symptoms."),
    (8, 9, "Mild", "You may be experiencing mild anxiety. Mindfulness and stress-reduction techniques may help."),
    (10, 14, "Moderate", "Your score suggests moderate anxiety. Consider professional guidance to manage symptoms."),
    (15, 19, "Severe", "Your score indicates severe anxiety. Seeking professional support is recommended."),
    (20, 42, "Extremely Severe", "Your score indicates extremely severe anxiety symptoms. Urgent professional support is advised.")
]

stress_ranges = [
    (0, 14, "Normal", "Your score is within the normal range, suggesting your stress levels are manageable."),
    (15, 18, "Mild", "You may be experiencing mild stress. Self-care and time-management techniques may help."),
    (19, 25, "Moderate", "Your score suggests moderate stress. Consider professional or peer support to manage workload and lifestyle pressures."),
    (26, 33, "Severe", "Your score indicates severe stress. Professional support is recommended."),
    (34, 42, "Extremely Severe", "Your score indicates extremely severe stress levels. Immediate intervention is advised.")
]

# -------------------------
# PDF Class
# -------------------------
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        base_path = os.path.dirname(__file__)
        self.add_font("DejaVu", "", os.path.join(base_path, "DejaVuSans.ttf"), uni=True)
        self.add_font("DejaVu", "B", os.path.join(base_path, "DejaVuSans-Bold.ttf"), uni=True)

    def header(self):
        self.set_font("DejaVu", "B", 16)
        self.cell(0, 10, "Life Minus Work - DASS-21 Results", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

# -------------------------
# Generate PDF
# -------------------------
def generate_pdf(name, dep_score, dep_cat, dep_msg, anx_score, anx_cat, anx_msg, str_score, str_cat, str_msg):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("DejaVu", "", 12)
    if name:
        pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.ln(5)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Depression", ln=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, f"Score: {dep_score} - {dep_cat}", ln=True)
    pdf.multi_cell(0, 8, dep_msg)
    pdf.ln(3)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Anxiety", ln=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, f"Score: {anx_score} - {anx_cat}", ln=True)
    pdf.multi_cell(0, 8, anx_msg)
    pdf.ln(3)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Stress", ln=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(0, 10, f"Score: {str_score} - {str_cat}", ln=True)
    pdf.multi_cell(0, 8, str_msg)

    pdf_output = io.BytesIO()
    pdf_bytes = pdf.output(dest="S")
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output

# -------------------------
# Interpret Scores
# -------------------------
def interpret_score(score, ranges):
    for low, high, category, message in ranges:
        if low <= score <= high:
            return category, message
    return "Unknown", ""

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="DASS-21 Test", layout="centered")
st.title("🧠 DASS-21 Psychological Assessment")
st.write("This test measures your levels of Depression, Anxiety, and Stress over the past week.")

if "responses" not in st.session_state:
    st.session_state.responses = []
if "page" not in st.session_state:
    st.session_state.page = 0
if "name" not in st.session_state:
    st.session_state.name = ""

def reset_test():
    st.session_state.responses = []
    st.session_state.page = 0
    st.session_state.name = ""

if st.session_state.page < len(questions):
    q = questions[st.session_state.page]
    st.markdown(f"**Q{st.session_state.page + 1}: {q}**")
    for opt_text, opt_value in options.items():
        if st.button(opt_text, key=f"{st.session_state.page}-{opt_text}"):
            st.session_state.responses.append(opt_value)
            st.session_state.page += 1
else:
    st.session_state.name = st.text_input("Your Name (optional)", st.session_state.name)

    if st.button("Get Results"):
        depression_items = [0, 1, 2, 3, 4, 5, 6]
        anxiety_items = [7, 8, 9, 10, 11, 12, 13]
        stress_items = [14, 15, 16, 17, 18, 19, 20]

        dep_score = sum(st.session_state.responses[i] for i in depression_items) * 2
        anx_score = sum(st.session_state.responses[i] for i in anxiety_items) * 2
        str_score = sum(st.session_state.responses[i] for i in stress_items) * 2

        dep_cat, dep_msg = interpret_score(dep_score, depression_ranges)
        anx_cat, anx_msg = interpret_score(anx_score, anxiety_ranges)
        str_cat, str_msg = interpret_score(str_score, stress_ranges)

        st.success(f"Depression: {dep_score} ({dep_cat})")
        st.success(f"Anxiety: {anx_score} ({anx_cat})")
        st.success(f"Stress: {str_score} ({str_cat})")

        pdf_buffer = generate_pdf(st.session_state.name, dep_score, dep_cat, dep_msg, anx_score, anx_cat, anx_msg, str_score, str_cat, str_msg)

        st.download_button(
            label="📥 Download Your Results (PDF)",
            data=pdf_buffer,
            file_name="DASS21_Results.pdf",
            mime="application/pdf"
        )

    st.button("🔄 Restart Test", on_click=reset_test)
