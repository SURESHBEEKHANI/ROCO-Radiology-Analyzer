## **Radiology Analyzer **

This repository contains a Python-based web application for AI-powered radiology image analysis, built using Streamlit and Groq AI. The core application logic is implemented in app.py.

🚀 Key Features & Files

app.py – Main application file containing Streamlit UI and analysis logic.
requirements.txt – List of project dependencies.
LICENSE – MIT License file governing the use of the repository.
.gitignore – Configuration file to exclude unnecessary files from version control.

🛠️ Technical Capabilities

🖼️ Image Processing – Uses PIL.Image to handle multiple formats (PNG, JPG, JPEG).
🧠 AI Analysis – Integrates groq.Groq client for LLaMA model inference.
📄 PDF Generation – Implements reportlab for creating structured radiology reports.
🔐 Environment Management – Utilizes dotenv for secure API key configuration.

🔑 Key Functions in app.py

configure_application() – Initializes and configures Streamlit settings.
generate_radiology_report() – Manages AI-based radiology analysis.
generate_pdf_report() – Generates downloadable PDF reports.
