import csv
import os
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, Response
from backend.models import (
    ContractUploadResponse,
    TaskUploadResponse,
    TaskAnalysisResponse,
    TaskAnalysisResult,
)
from docx import Document
from io import BytesIO


app = FastAPI()

__version__ = "0.1.0"

# Global variables to store uploaded data (for simplicity)
contract_json = None
tasks = []


@app.get('/version')
def version():
    return Response(content=__version__, media_type="text/plain")


@app.post("/upload_contract", response_model=ContractUploadResponse)
async def upload_contract(file: UploadFile = File(...)):
    # Read the uploaded file
    content = await file.read()
    global contract_json

    # Determine the file type based on the filename or content type
    filename = file.filename
    file_extension = os.path.splitext(filename)[1].lower()

    if file_extension == '.docx':
        document = Document(BytesIO(content))
        contract_text = '\n'.join([para.text for para in document.paragraphs])
    else:
        return JSONResponse(
            content={"message": "Unsupported file type. Please upload a DOCX file."},
            status_code=400
        )

    # Use LLM to extract contract terms and store in contract_json
    # Implement your extract_contract_terms function
    # contract_json = extract_contract_terms(contract_text)

    return ContractUploadResponse(
        message="Contract uploaded and processed successfully.",
        contract_filename=filename
    )


@app.post("/upload_tasks", response_model=TaskUploadResponse)
async def upload_tasks(file: UploadFile = File(...)):
    global tasks
    content = await file.read()
    filename = file.filename
    file_extension = os.path.splitext(filename)[1].lower()

    # Read the file into a pandas DataFrame
    if file_extension == '.csv':
        df = pd.read_csv(BytesIO(content))
    elif file_extension == '.xlsx':
        df = pd.read_excel(BytesIO(content))
    else:
        return JSONResponse(
            content={"message": "Unsupported file type. Please upload a CSV or XLSX file."},
            status_code=400
        )

    # Process the DataFrame
    tasks = []
    for index, row in df.iterrows():
        task_description = row['Task Description']
        amount_str = str(row['Amount'])
        # Remove any currency symbols and commas, and convert to float
        task_cost = float(amount_str.replace('$', '').replace(',', '').strip())
        tasks.append({
            "task_description": task_description,
            "task_cost": task_cost
        })

    return TaskUploadResponse(
        message="Tasks uploaded successfully.",
        tasks_uploaded=len(tasks)
    )


@app.get("/analyze_tasks", response_model=TaskAnalysisResponse)
def analyze_tasks():
    # Ensure contract and tasks are uploaded
    if contract_json is None or not tasks:
        return JSONResponse(
            content={"message": "Contract and tasks must be uploaded before analysis."},
            status_code=400
        )
    # TODO: Use LLM to analyze tasks against contract_json
    results = []
    for task in tasks:
        # Placeholder analysis
        result = TaskAnalysisResult(
            task_description=task['task_description'],
            task_cost=task['task_cost'],
            compliance=True,  # Replace with actual compliance result
            reasons=["Compliant with all applicable terms."],  # Replace with actual reasons
            ambiguity=False,
            applicable_terms=["Term 1", "Term 2"]  # Replace with actual terms
        )
        results.append(result)
    return TaskAnalysisResponse(results=results)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8008)
