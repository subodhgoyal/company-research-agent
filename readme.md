# AI Sales Agent

This project is an AI-powered sales agent that uses OpenAI and SERP APIs to gather and summarize information about companies. It is built using Streamlit for the user interface.

## Setup Instructions

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo

Create and Configure the .env File
Copy the .env.example file to .env:

bash
Copy code
cp .env.example .env
Open the .env file and replace the placeholder values with your actual API keys:

env
Copy code
# .env
OPENAI_API_KEY=your_actual_openai_api_key
SERP_API_KEY=your_actual_serp_api_key
Install Dependencies
Install the required Python packages using pip:

bash
Copy code
pip install -r requirements.txt
Run the Application
Run the Streamlit application:

bash
Copy code
streamlit run main.py
Project Structure
bash
Copy code
project/
│
├── .env.example        # Example environment variables file
├── .gitignore          # Git ignore file
├── sales-agent_streamlit.py             # Main application code
├── requirements.txt    # Python dependencies
├── README.md           # Project setup and instructions
├── notebooks/          # Directory for Jupyter notebooks
│   └── sales-agent_VF.ipynb  # Initial development notebook
└── LICENSE             # License file

##Notebooks
The notebooks/ directory contains Jupyter notebooks used during the initial development phase of the project. These notebooks provide insight into the exploratory analysis and development process.

##Usage
Enter the company name in the input field.
Click the "Search" button.
View the summarized information about the company.
