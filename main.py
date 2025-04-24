import streamlit as st
import openai
import pdfplumber
import docx
import json

openai.api_key = ""

def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def analyze_resume(resume_text):
    prompt = (
        "Extract the following from this resume: Name, Contact Info, Education, "
        "Work Experience (with dates), Key Skills. Return as JSON.\n\n"
        f"{resume_text}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.2,
    )
    return response['choices'][0]['message']['content']

st.title("Ultralight Resume Analyzer")

uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]:
        resume_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file type.")
        st.stop()

    st.subheader("Extracted Resume Text (Preview)")
    st.write(resume_text[:1000] + ("..." if len(resume_text) > 1000 else ""))

    if st.button("Analyze Resume"):
        with st.spinner("Analyzing..."):
            analysis = analyze_resume(resume_text)
        st.subheader("Analysis Result")
        try:
            result = json.loads(analysis)
            if "Name" in result:
                st.markdown(f"**Name:** {result['Name']}")
            if "Contact Info" in result:
                st.markdown(f"**Contact Info:** {result['Contact Info']}")
            if "Education" in result:
                st.markdown("**Education:**")
                st.write(result["Education"])
            if "Work Experience" in result:
                st.markdown("**Work Experience:**")
                st.write(result["Work Experience"])
            if "Key Skills" in result:
                st.markdown("**Key Skills:**")
                st.write(result["Key Skills"])
        except Exception as e:
            st.error("Could not parse analysis result. Showing raw output:")
            st.code(analysis)