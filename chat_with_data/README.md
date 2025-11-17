# Chat with data

## Features
- Upload any CSV
- LLM **infers schema** from first 10 rows of the uploaded CSV
- Creates **SQLite table** and inserts **all data** from uploaded CSV
- Chat with **LangChain agent**
- 2 tools: `run_sql`, `make_chart`, and has a non-direct functionality of creating database based on user upload (generating database create SQL)
- Prevents **destructive** SQL queries
- Creates support ticket as GitHub issue

## Local Development

Clone [generative-ai-capstone-project](https://github.com/bakhridinova/generative-ai-capstone-project) GitHub repository into your local machine.

Make sure [Package installer for Python](https://pypi.org/project/pip) is downloaded.

Open terminal with path to chat_with_data folder.

Install required libraries using command below:

```bash
    pip install -r requirements.txt
```

Run [Streamlit](https://streamlit.io) application using command below:

```bash
    streamlit run app.py
```

Open http://localhost:8501 to access the chat.

![](screenshots/initial_commands.png)
![](screenshots/initial_page.png)

## What can chat do?

### Create schema based on uploaded CSV file structure

![](screenshots/csv_uploading.png)

Notice the number of rows and total (numeric) in the left panel

![](screenshots/csv_uploaded.png)

#### Logs

![](screenshots/csv_upload_logs.png)

### Answer questions based on uploaded data

![](screenshots/question1_thinking.png)
![](screenshots/question1_result.png)
![](screenshots/question2_result.png)

#### Logs

![](screenshots/question1_logs.png)
![](screenshots/question2_logs.png)

### Create support tickets

Inside chat

![](screenshots/create_ticket1.png)
![](screenshots/create_ticket1_list.png)
![](screenshots/create_ticket1_details.png)

Outside chat

![](screenshots/create_ticket2.png)
![](screenshots/create_ticket2_list.png)
![](screenshots/create_ticket2_details.png)

#### Logs

![](screenshots/create_ticket1_logs.png)
![](screenshots/create_ticket2_logs.png)

### Draw bar charts

![](screenshots/chart1.png)
![](screenshots/chart2.png)

#### Logs

![](screenshots/chart_logs.png)

### Prevent destructive operations

![](screenshots/destructive.png)

#### Logs

![](screenshots/destructive_logs.png)


