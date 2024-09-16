import streamlit as st
import requests
import json
import os
import pandas as pd

# Read the API URL from the environment variable or use localhost as default
API_URL = os.getenv('CONTRACT_ANALYSIS_LLM_API', 'http://localhost:8008')

st.title("Contract Analysis LLM")

# Initialize session state for cookies, contract JSON, and tasks
if 'cookies' not in st.session_state:
    st.session_state.cookies = None
if 'contract_json' not in st.session_state:
    st.session_state.contract_json = None
if 'tasks' not in st.session_state:
    st.session_state.tasks = None

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
            st.session_state.cookies = response.cookies
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

if task_file is not None and st.session_state.tasks is None:
    # Send the file to the backend
    with st.spinner("Uploading and processing tasks..."):
        files = {'file': (task_file.name, task_file.getvalue(), task_file.type)}
        print('COOKIES 1: ' + str(st.session_state.cookies))
        response = requests.post(f"{API_URL}/upload_tasks", files=files, cookies=st.session_state.cookies)
        st.session_state.cookies = response.cookies
        print('COOKIES 2: ' + str(st.session_state.cookies))
        if response.status_code == 200:
            data = response.json()
            st.success(f"{data['message']} Tasks uploaded: {data['tasks_uploaded']}")
            # Store the tasks in the session state
            tasks_response = requests.get(f"{API_URL}/get_tasks", cookies=st.session_state.cookies)
            st.session_state.cookies = tasks_response.cookies
            print('COOKIES 3: ' + str(st.session_state.cookies))
            if tasks_response.status_code == 200:
                tasks_data = tasks_response.json()
                st.session_state.tasks = tasks_data.get('tasks', [])
        else:
            st.error(f"Failed to upload tasks. Error: {response.json().get('message')}")

# Display the tasks if available
if st.session_state.tasks is not None:
    st.subheader("Uploaded Tasks")
    with st.expander("Show/Hide Tasks", expanded=False):
        tasks_list = st.session_state.tasks
        if tasks_list:
            tasks_df = pd.DataFrame(tasks_list)
            tasks_df.rename(columns={
                'task_description': 'Task Description',
                'task_cost': 'Cost'
            }, inplace=True)
            st.dataframe(tasks_df, height=300)
        else:
            st.write("No tasks to display.")

# Step 3: Analyze Tasks
if st.button("Analyze Tasks"):
    if st.session_state.cookies and st.session_state.tasks:
        with st.spinner("Analyzing tasks..."):
            response = requests.get(f"{API_URL}/analyze_tasks", cookies=st.session_state.cookies)
            st.session_state.cookies = response.cookies
            if response.status_code == 200:
                data = response.json()
                st.header("Analysis Results")
                for result in data['results']:
                    st.subheader(f"Task: {result['task_description']}")
                    st.write(f"Cost: ${result['task_cost']}")
                    st.write("Applicable Terms:")
                    for term in result['applicable_terms']:
                        st.write(f"- {term}")
                    st.write("Reasons:")
                    st.write(f"{result['reasoning']}")
                    compliance = "Compliant" if result['compliance'] else "Non-Compliant"
                    st.write(f"Compliance: **{compliance}**")
                    if result['ambiguous']:
                        st.warning("This task has ambiguities that may require further review.")
            else:
                st.error("Failed to analyze tasks. Ensure both contract and tasks are uploaded.")
    else:
        st.error("Please upload tasks before analysis.")
