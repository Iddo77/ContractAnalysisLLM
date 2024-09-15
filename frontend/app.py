import streamlit as st
import requests
import json
import os
import pandas as pd
import time

# Read the API URL from the environment variable or use local host as default
API_URL = os.getenv('CONTRACT_ANALYSIS_LLM_API', 'http://localhost:8008')

st.title("Contract Analysis LLM")

# Initialize session state for cookies and contract JSON
if 'cookies' not in st.session_state:
    st.session_state.cookies = None
if 'contract_json' not in st.session_state:
    st.session_state.contract_json = None

# Step 1: Upload Contract
st.header("Upload Contract Document")
contract_file = st.file_uploader("Choose a contract file (DOCX)", type=['docx'], accept_multiple_files=False)

if contract_file is not None and st.session_state.contract_json is None:
    # Show progress indicator
    with st.spinner("Uploading and processing contract..."):
        # Send the file to the backend
        files = {'file': (contract_file.name, contract_file.getvalue(), contract_file.type)}
        response = requests.post(f"{API_URL}/upload_contract", files=files)
        if response.status_code == 200:
            data = response.json()
            st.success(f"{data['message']} Filename: {data['contract_filename']}")

            # Store the contract JSON
            st.session_state.contract_json = data['contract_json']
        else:
            st.error("Failed to upload and process contract.")

# Display the contract JSON if available
if st.session_state.contract_json is not None:
    contract_json = st.session_state.contract_json

    # Visualize the contract in an expandable panel
    st.subheader("Extracted Contract")
    with st.expander("Show/Hide Contract Details", expanded=False):
        # Display the contract JSON in a structured format
        st.json(contract_json)

    # Button to download the contract JSON
    st.download_button(
        label="Download Contract JSON",
        data=st.session_state.contract_json.encode('utf-8'),  # Encode the string directly to bytes
        file_name="contract.json",
        mime="application/json"
    )

# Step 2: Upload Task CSV
st.header("Upload Task Descriptions")
task_file = st.file_uploader("Choose a task file (CSV or XLSX)", type=['csv', 'xlsx'], accept_multiple_files=False)

if task_file is not None:
    # Send the file to the backend
    files = {'file': (task_file.name, task_file.getvalue(), task_file.type)}
    response = requests.post(f"{API_URL}/upload_tasks", files=files)
    if response.status_code == 200:
        data = response.json()
        st.success(f"{data['message']} Tasks uploaded: {data['tasks_uploaded']}")

        # Capture and store the cookies
        st.session_state.cookies = response.cookies

        # Display the tasks in a collapsible section
        st.subheader("Uploaded Tasks")
        with st.expander("Show/Hide Tasks", expanded=False):
            # Fetch the tasks from the backend to display them
            tasks_response = requests.get(f"{API_URL}/get_tasks", cookies=st.session_state.cookies)
            if tasks_response.status_code == 200:
                tasks_data = tasks_response.json()
                tasks_list = tasks_data.get('tasks', [])

                if tasks_list:
                    tasks_df = pd.DataFrame(tasks_list)
                    tasks_df.rename(columns={
                        'task_description': 'Task Description',
                        'task_cost': 'Cost'
                    }, inplace=True)
                    st.dataframe(tasks_df, height=300)
                else:
                    st.write("No tasks to display.")
            else:
                st.error("Failed to retrieve tasks for display.")
    else:
        st.error(f"Failed to upload tasks. Error: {response.json().get('message')}")

# Step 3: Analyze Tasks
if st.button("Analyze Tasks"):
    if st.session_state.cookies:
        with st.spinner("Analyzing tasks..."):
            response = requests.get(f"{API_URL}/analyze_tasks")
            if response.status_code == 200:
                data = response.json()
                st.header("Analysis Results")
                for result in data['results']:
                    st.subheader(f"Task: {result['task_description']}")
                    st.write(f"Cost: ${result['task_cost']}")
                    compliance = "Compliant" if result['compliance'] else "Non-Compliant"
                    st.write(f"Compliance: **{compliance}**")
                    st.write("Reasons:")
                    for reason in result['reasons']:
                        st.write(f"- {reason}")
                    st.write("Applicable Terms:")
                    for term in result['applicable_terms']:
                        st.write(f"- {term}")
                    if result['ambiguity']:
                        st.warning("This task has ambiguities that may require further review.")
            else:
                st.error("Failed to analyze tasks. Ensure both contract and tasks are uploaded.")
    else:
        st.error("Please upload tasks before analysis.")
