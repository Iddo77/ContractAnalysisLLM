import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.contract_term_extraction import ContractTermExtractionAgent
from backend.file_utils import extract_text_from_docx, read_tasks_from_csv, read_tasks_from_excel
from backend.models import (
    ContractUploadResponse,
    TaskUploadResponse,
    TaskAnalysisResponse
)
from backend.session_manager import create_session, get_session, set_session_data
from backend.task_compliance_analysis import TaskComplianceAnalysisAgent, analyze_tasks_compliance

app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

__version__ = "0.1.0"


contract_term_extraction_agent = ContractTermExtractionAgent()
task_compliance_analysis_agent = TaskComplianceAnalysisAgent()


@app.middleware("http")
async def add_session_id(request: Request, call_next):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = create_session()
    request.state.session_id = session_id

    # Proceed to process the request
    response = await call_next(request)
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    return response


@app.get('/version')
def version():
    return Response(content=__version__, media_type="text/plain")


@app.post("/upload_contract", response_model=ContractUploadResponse)
async def upload_contract(request: Request, file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()

        if file_extension == '.docx':
            contract_text = extract_text_from_docx(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a DOCX or TXT file.")

        contract, contract_json = await contract_term_extraction_agent.extract_contract_terms(contract_text)

        # Store in session
        session_id = request.state.session_id
        set_session_data(session_id, "contract_json", contract_json)

        return ContractUploadResponse(
            message="Contract uploaded and processed successfully.",
            contract_filename=filename,
            contract_json=contract_json
        )
    except Exception as e:
        return JSONResponse(
            content={"message": f"An error occurred while processing the contract: {str(e)}"},
            status_code=500
        )


@app.post("/upload_tasks", response_model=TaskUploadResponse)
async def upload_tasks(request: Request, file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()

        if file_extension == '.csv':
            tasks = read_tasks_from_csv(content)
        elif file_extension == '.xlsx':
            tasks = read_tasks_from_excel(content)
        else:
            return JSONResponse(
                content={"message": "Unsupported file type. Please upload a CSV or XLSX file."},
                status_code=400
            )

        # Store tasks in session
        session_id = request.state.session_id
        set_session_data(session_id, "tasks", tasks)

        return TaskUploadResponse(
            message="Tasks uploaded successfully.",
            tasks_uploaded=len(tasks)
        )
    except Exception as e:
        return JSONResponse(
            content={"message": f"An error occurred while processing the tasks: {str(e)}"},
            status_code=500
        )


@app.get("/get_tasks")
def get_tasks(request: Request):
    # Retrieve tasks from session
    session_id = request.state.session_id
    session_data = get_session(session_id)
    tasks = session_data.get("tasks")

    if not tasks:
        return JSONResponse(
            content={"message": "No tasks found in session."},
            status_code=404
        )

    return {"tasks": tasks}


@app.get("/analyze_tasks", response_model=TaskAnalysisResponse)
async def analyze_tasks(request: Request):
    # Retrieve data from session
    session_id = request.state.session_id
    session_data = get_session(session_id)

    contract_json = session_data.get("contract_json")
    tasks = session_data.get("tasks")

    if contract_json is None or not tasks:
        return JSONResponse(
            content={"message": "Contract and tasks must be uploaded before analysis."},
            status_code=400
        )

    results = await analyze_tasks_compliance(contract_json, tasks, task_compliance_analysis_agent)
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8008)
