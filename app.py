import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
import faiss
import requests
from pdfminer.high_level import extract_text
import os
# from googletrans import Translator
# for recording audio
from audiorecorder import audiorecorder 
import whisper
from tempfile import NamedTemporaryFile


requests_timeout = 30  # Adjust this value as needed

# HUGGING_FACE_TIMEOUT = 30  # Adjust this value as needed

# Set the timeout for all HTTP requests made by requests library
requests.adapters.DEFAULT_RETRIES = 2
session = requests.Session()
session.timeout = requests_timeout

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        # pdf_reader = PdfReader(pdf)
        text  = extract_text(pdf_docs[0])
    # translater=Translator()
    # out=translater.translate("text",dest="en")
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=0,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=text_chunks[:500], embedding=embeddings)
    # index = FAISS.IndexFlatL2(len(embeddings[0]))
    # index = faiss.IndexFlatL2(embeddings.get_embedding_dim())
    return vectorstore
    # return index


# def get_conversation_chain(vectorstore):
#     llm = ChatOpenAI()
#     # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

#     memory = ConversationBufferMemory(
#         memory_key='chat_history', return_messages=True)
#     conversation_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=vectorstore.as_retriever(),
#         memory=memory
#     )
#     return conversation_chain

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(model="gpt-3.5-turbo")  # specify the model here

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    # load_dotenv()
    print(os.environ.get("OPENAI_API_KEY"))
    st.set_page_config(page_title="Chat with multiple PDFs",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with multiple PDFs :books:")
    # st.text_input("Ask a question about your documents:")
    user_question = st.text_input("Ask a question about your documents:", key="text_input_1")

    # below part for audio record
    audio = audiorecorder("Click to record", "Click to stop recording")

    if len(audio) > 0:
        # To play audio in frontend:
        st.audio(audio.export().read())  
        # To save audio to a file, use pydub export method:
        audio.export("audio.wav", format="wav")
        # To get audio properties, use pydub AudioSegment properties:
        st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")
        # Load Whisper model
        model = whisper.load_model("base")
        st.text("Whisper Model Loaded")

        if st.sidebar.button("Transcribe Audio"):
            with NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                temp.write(audio.export().read())
                temp.seek(0)
                st.sidebar.success("Transcribing Audio")
                transcription = model.transcribe(temp.name)
                st.sidebar.success("Transcription Complete")
                user_question = transcription["text"]
                st.text(user_question)

    if user_question:
        handle_userinput(user_question)
    
    #############
    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)
                # get the text chunks
                text_chunks = get_text_chunks(raw_text)
                # create vector store
                vectorstore = get_vectorstore(text_chunks)
                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)

if __name__ == '__main__':
    main()