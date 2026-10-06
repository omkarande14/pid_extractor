# P&ID & PFD Component Extractor

An AI-powered engineering tool to extract components from Piping and Instrumentation Diagrams (P&ID) and Process Flow Diagrams (PFD) into structured Excel spreadsheets using Google Gemini Multimodal Vision AI.

## Features

- **Multi-Format Support**: Direct processing of technical drawings in PDF, PNG, JPG, and JPEG.
- **Zero-Dependency PDF Rendering**: High-resolution 200 DPI vector rendering via PyMuPDF (no external Poppler binary required).
- **Intelligent Component Extraction**: Automatically identifies and structures:
  - Equipment & Tag Numbers (Pumps, Tanks, Vessels, etc.)
  - Component Types & Descriptions
  - Line Sizes & Pipelines
  - Connectivity Relationships (`Connected_From_To`)
- **Excel Export**: Instant one-click generation and download of formatted `.xlsx` component sheets.
- **Interactive UI**: Clean, dual-pane Streamlit application with live diagram preview and data tables.

## Quick Start

### 1. Prerequisites & Virtual Environment

Ensure you have Python 3.10+ installed.

```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Add your Google Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

*(You can also enter your API key directly in the Streamlit web sidebar).*

### 4. Run the Application

```bash
streamlit run app.py
```