import streamlit as st
import os
from PIL import Image
import base64
import io
import pdf2image
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Google AI
try:
    GOOGLE_API_KEY = "AIzaSyDj2A9qOVpxV7yRnB1IyL-oJ0ErBR5GUbU"
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    logger.error(f"Error configuring Google AI: {str(e)}")
    raise

class ResumeAnalyzer:
    def __init__(self):
        self.poppler_path = r"C:\Program Files\poppler\Library\bin"
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    def get_gemini_response(self, input_text: str, pdf_content: Dict, prompt: str) -> str:
        """
        Get response from Gemini model
        """
        try:
            # Combine the input text and prompt
            combined_prompt = f"{prompt}\n\nJob Description:\n{input_text}"
            response = self.model.generate_content([combined_prompt, pdf_content])
            return response.text
        except Exception as e:
            logger.error(f"Error getting Gemini response: {str(e)}")
            raise

    def get_custom_query_response(self, query: str, input_text: str, pdf_content: Dict) -> str:
        """
        Get response for custom query from Gemini model
        """
        try:
            prompt = f"""
            As an AI assistant with expertise in resume analysis and recruitment, please answer the following query 
            about the resume in relation to the job description provided.

            Job Description:
            {input_text}

            Query: {query}

            Please provide a detailed and specific answer based on the resume content and job requirements.
            """
            response = self.model.generate_content([prompt, pdf_content])
            return response.text
        except Exception as e:
            logger.error(f"Error getting custom query response: {str(e)}")
            raise

    def convert_pdf_to_image(self, pdf_content: bytes) -> Dict:
        """
        Convert PDF to image and return properly formatted dict for Gemini
        """
        try:
            images = pdf2image.convert_from_bytes(
                pdf_content,
                poppler_path=self.poppler_path,
                dpi=300
            )
            first_image = images[0]
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            first_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            return {
                "mime_type": "image/png",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        except Exception as e:
            logger.error(f"Error converting PDF to image: {str(e)}")
            raise

    def process_uploaded_file(self, uploaded_file) -> Optional[Dict]:
        """
        Process uploaded PDF file
        """
        if uploaded_file is None:
            return None
        
        try:
            pdf_content = uploaded_file.read()
            return self.convert_pdf_to_image(pdf_content)
        except Exception as e:
            logger.error(f"Error processing uploaded file: {str(e)}")
            raise

class ATSApp:
    def __init__(self):
        self.analyzer = ResumeAnalyzer()
        self.prompts = {
            "resume_review": """
            You are an experienced HR professional with technical experience in Data Science, 
            Full Stack Web Development, Big Data Engineering, DevOps, and Data Analysis. 
            Please review the provided resume against the job description for these profiles.
            Share your professional evaluation on whether the candidate's profile aligns with 
            the role. Highlight the strengths and weaknesses of the applicant in relation 
            to the specified job requirements.
            """,
            "percentage_match": """
            You are a skilled ATS scanner with deep understanding of Data Science, Full Stack 
            Web Development, Big Data Engineering, DevOps, and Data Analysis roles. Evaluate 
            the resume against the provided job description. Provide:
            1. Match percentage
            2. Missing keywords
            3. Final thoughts and recommendations
            Format the response clearly with headers and bullet points.
            """
        }

    def setup_page(self):
        """
        Setup Streamlit page configuration
        """
        st.set_page_config(
            page_title="ATS Resume Expert",
            page_icon="📄",
            layout="wide"
        )
        st.title("🎯 ATS Resume Expert")
        st.subheader("By Ashrith Velisoju")
        
    def run(self):
        """
        Run the Streamlit application
        """
        self.setup_page()

        # Input sections
        with st.container():
            input_text = st.text_area(
                "Job Description:",
                placeholder="Paste the job description here...",
                height=200
            )
            
            uploaded_file = st.file_uploader(
                "Upload your resume (PDF)",
                type=["pdf"],
                help="Please upload a PDF file only"
            )

            if uploaded_file:
                st.success("Resume uploaded successfully!")

            # New custom query section
            custom_query = st.text_input(
                "Ask a specific question about the resume:",
                placeholder="E.g., What are the candidate's strongest technical skills? How many years of experience in Python?"
            )

        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            analyze_button = st.button("📋 Analyze Resume", use_container_width=True)
        with col2:
            match_button = st.button("🎯 Calculate Match", use_container_width=True)
        with col3:
            query_button = st.button("❓ Get Answer", use_container_width=True)

        # Process requests
        if uploaded_file is None and (analyze_button or match_button or query_button):
            st.error("Please upload your resume first!")
            return

        try:
            if analyze_button or match_button or query_button:
                pdf_content = self.analyzer.process_uploaded_file(uploaded_file)
                
                if not input_text.strip():
                    st.warning("Please provide a job description!")
                    return

                if analyze_button:
                    self.process_analysis(input_text, pdf_content)
                elif match_button:
                    self.process_matching(input_text, pdf_content)
                elif query_button:
                    if not custom_query.strip():
                        st.warning("Please enter your question!")
                        return
                    self.process_custom_query(custom_query, input_text, pdf_content)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.error(f"Application error: {str(e)}")

    def process_analysis(self, input_text: str, pdf_content: Dict):
        """
        Process resume analysis request
        """
        with st.spinner("Analyzing resume..."):
            response = self.analyzer.get_gemini_response(
                input_text,
                pdf_content,
                self.prompts["resume_review"]
            )
            st.subheader("📊 Analysis Results:")
            st.write(response)

    def process_matching(self, input_text: str, pdf_content: Dict):
        """
        Process resume matching request
        """
        with st.spinner("Calculating match..."):
            response = self.analyzer.get_gemini_response(
                input_text,
                pdf_content,
                self.prompts["percentage_match"]
            )
            st.subheader("🎯 Match Analysis:")
            st.write(response)

    def process_custom_query(self, query: str, input_text: str, pdf_content: Dict):
        """
        Process custom query request
        """
        with st.spinner("Getting answer..."):
            response = self.analyzer.get_custom_query_response(
                query,
                input_text,
                pdf_content
            )
            st.subheader("❓ Query Response:")
            st.write(response)

if __name__ == "__main__":
    try:
        app = ATSApp()
        app.run()
    except Exception as e:
        st.error(f"Application failed to start: {str(e)}")
        logger.critical(f"Application failed to start: {str(e)}")