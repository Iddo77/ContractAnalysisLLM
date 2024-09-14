# ContractAnalysisLLM
An LLM-powered tool using LangChain for extracting contract terms and analyzing task compliance.

## Overview

ContractAnalysisLLM uses GPT and LangChain to:

- **Extract** terms and conditions from contract documents into a structured JSON format.
- **Analyze** task descriptions and costs against the extracted contract terms to determine compliance.
- **Assess Ambiguity** in task descriptions, providing reasons for any uncertainties.
- **Provide Results** that include applicable terms, compliance status, and explanations.

## Installation

Follow these steps to set up the project:

## Installation

Follow these steps to set up the project:

1. **Clone the Repository**

   Run the following commands:

       git clone https://github.com/yourusername/ContractAnalysisLLM.git
       cd ContractAnalysisLLM

2. **Create a Conda Environment**

   Ensure you have Anaconda or Miniconda installed. Create and activate a new Python 3.11 environment:

       conda create -n ContractAnalysisLLM python=3.11
       conda activate ContractAnalysisLLM

3. **Install Dependencies**

   Install the required Python packages:

       pip install -r requirements.txt

4. **Set Up OpenAI API Key**

   Obtain an API key from OpenAI and set it as an environment variable:
   Linux/macOS:

          export OPENAI_API_KEY='your-openai-api-key'

   Windows (PowerShell):
   
         [System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-openai-api-key", "User")

5. **Project Structure**

   The project consists of two main folders:
   - **frontend**: Contains the user interface built with Streamlit.
   - **backend**: Contains the server-side code, using FastAPI.

6. **Running the Application**
   Navigate to the project root and make sure the Conda environment is activated:

	conda activate ContractAnalysisLLM

   Start the backend server using the following command:

      python -m uvicorn backend.app:app --host 0.0.0.0 --port 8008


   Open a new terminal for the frontend, navigate to the project root and make sure the Conda environment is activated.
   Start the Streamlit app using the following command:

      python -m streamlit run frontend/app.py
   
   If the frontend and backend are running on different machines, you need to set the backend URL to the environment variable CONTRACT_ANALYSIS_LLM_API.




   