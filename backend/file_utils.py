from io import BytesIO
from docx import Document
import pandas as pd


def extract_text_from_docx(file_content: bytes) -> str:
    document = Document(BytesIO(file_content))
    text = '\n'.join([para.text for para in document.paragraphs])
    return text


def read_tasks_from_csv(file_content: bytes) -> list:
    df = pd.read_csv(BytesIO(file_content))
    tasks = process_tasks_dataframe(df)
    return tasks


def read_tasks_from_excel(file_content: bytes) -> list:
    df = pd.read_excel(BytesIO(file_content))
    tasks = process_tasks_dataframe(df)
    return tasks


def process_tasks_dataframe(df: pd.DataFrame) -> list:
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
    return tasks
