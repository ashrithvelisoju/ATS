from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from PIL import Image
import base64
import io
import pdf2image
import google.generativeai as genai


genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def get_gemini_response(input,pdf_content,prompt):
    model=genai.GenerativeModel("gemini-1.5 Flash")
    response=model.generate_content([input,pdf_content,prompt])
    return response.text


poppler_path = r"C:\Program Files\poppler\Library\bin"
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Convert PDF to image
        pdf_content = uploaded_file.read()  # Assuming 'uploaded_file' is a file-like object
        try:
            images = pdf2image.convert_from_bytes(pdf_content, poppler_path=poppler_path, dpi=300)
        except Exception as e:
            raise FileNotFoundError("File not found")

        first_image = images[0]

        # convert into bytes
        img_byte_arr = io.BytesIO()
        first_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_dict = {
            "mimeType": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()
        }

        return pdf_dict
    else:
        raise FileNotFoundError("File not found")

#Streamlit app
st.set_page_config(page_title="ATS Resume Expert")
st.title("ATS Resume Expert")
input_text=st.text_area("Job Description: ",key="input")
uploaded_file=st.file_uploader("Upload your resume(PDF)",type=["pdf"])

if uploaded_file is not None:
    st.write("Resume uploaded successfully")

submit1=st.button("Tell Me About the Resume")

#submit2=st.button("How Can I Improve My Skills")

submit3=st.button("Perecentage Match")

input_prompt1="""
    You are an experienced HR with Tech Experience in the field of Data Science,Full stack web development,
    Big Data Engineering, DEVOPS,Data Analyst, your task is to review the provided resume against the job description for
    these profiles.
        Please share your professional evaluation on whether the candidate's profile aligns with role.Highlight the
        strengths and weaknesses of the applicant in relation to the specified job requirements. 
"""

#input_prompt2="""for example""""

input_prompt3="""
    You are an skilled ATS scanner with a deep understanding of the Data Science,Full stack web development,
    Big Data Engineering, DEVOPS,Data Analyst and deep ATS functionality. Your task is to evaluate the resume against the
    provided job description. give me the perencetage of match between the resume and the job description.First the
    ouput should come  as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content=input_pdf_setup(uploaded_file)
        response=get_gemini_response(input_text,pdf_content,input_prompt1)
        st.subheader("Response is:")
        st.write(response)
    else:
        st.write("Please upload your resume")

if submit3:
    if uploaded_file is not None:
        pdf_content=input_pdf_setup(uploaded_file)
        response=get_gemini_response(input_text,pdf_content,input_prompt3)
        st.subheader("Response is:")
        st.write(response)
    else:
        st.write("Please upload your resume")