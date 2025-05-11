FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY .streamlit .streamlit
COPY data data
COPY reportus reportus
COPY main.py .
ENTRYPOINT ["streamlit", "run"]
CMD ["main.py", "--browser.gatherUsageStats", "false", "--server.fileWatcherType", "none", "--server.port", "8080"]
