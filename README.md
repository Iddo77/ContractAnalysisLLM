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

   Obtain an API key from OpenAI and use it to set the environment variable OPENAI_API_KEY.

5 **Set Up a Secret Key**
   
   Execute the following command in the terminal (the conda environment should be activated):

	  python -m secret

   Copy the key and use it to set the environment variable CONTRACT_ANALYSIS_LLM_SECRET.

## Project Structure

   The project consists of two main folders:
   - **frontend**: Contains the user interface built with Streamlit.
   - **backend**: Contains the server-side code, using FastAPI.


## Running the Application

1. **Running the Backend**
   Start the backend server using the following command:

      python -m uvicorn backend.app:app --host 0.0.0.0 --port 8008

2. **Running the Frontend**

   Open a new terminal for the frontend, navigate to the project root and make sure the Conda environment is activated:

      conda activate ContractAnalysisLLM
	
   Start the Streamlit app using the following command:

      python -m streamlit run frontend/app.py
   
   If the frontend and backend are running on different machines, you need to set the backend URL on the frontend machine to the environment variable CONTRACT_ANALYSIS_LLM_API.


## How To Use the application

1. In the section 'Upload Contract Document', select a docx file with a contract
2. Wait for the extraction of the JSON (this might take a while)
3. Verify the contract JSON by expanding the contract details under Extracted Contract
4. Download the contract JSON if needed
5. In the section 'Upload Task Descriptions', select a CSV or Excel file with tasks. The file must contain 2 columns named 'Task Description' and 'Amount'.
6. Verify the uploaded tasks by expanding the tasks under Uploaded Tasks
7. Click on the button 'Analyze Tasks'
8. Wait for the analysis to finish (this might take a while)
9. Click Download Analysis Results to get the JSON with the results

## Limitations
This application is a proof of concept (POC). It is not fully tested, and could therefore lack in robustness. 
Take note of the following:
- When uploading files, make sure the file type and content are exactly as described in 'How To Use the application'.
- Do not change the order of uploading files and do not change try to change uploaded files. 
The UI is not designed to handle this: only the happy path is handled. When the UI does not respond as expected, refresh the page and try again.
- After an analysis is done, you must refresh the page to try again.
- Large contracts are not supported. The documents are not chunked into smaller parts. This is out of scope of the POC, because of the limited time frame.
- The LLM retries several times in case an incorrect JSON is created. Usually this is enough, but sometimes you need to simply refresh the UI and try again.
- The application is slow: it uses multiple interactions with an LLM. The full analysis can take several minutes.