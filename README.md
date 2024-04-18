**DocBot**
DocBot, your intelligent document analysis assistant designed to help you effortlessly find answers to your questions within the content of provided documents. DocBot addresses this need by harnessing the power of advanced Natural Language Processing (NLP) and Machine Learning technologies. It analyzes, comprehends, and provides intelligent responses based on the content of the provided documents. Whether you’re looking to understand a complex research paper, extract insights from legal documents, or gain insights from a large dataset, DocBot is here to assist.

To use the application in your system follow these steps:

1. Clone the reposirty in your system.
```bash 
git clone https://github.com/rahulprasad02/BTP_FInal.git
```
2. Install all the package using pip
```bash
pip install -r requirement.txt
```
3. Create a file and name it as ```.env```
In this file you will need to enter your API key of OpenAI.

Content of the File

```bash 
OPENAI_API_KEY=<YOUR API KEY >
```

OR
Use below command in the terminal

```bash 
export OPENAI_API_KEY=<YOUR API KEY>
```

4. To run the application
```bash
streamlit run app.py
```