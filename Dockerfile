FROM python:3.8-slim-buster
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 80
# ENTRYPOINT ["streamlit","run"]
# CMD ["application.py"]
CMD ["sh", "-c", "streamlit run --browser.serverAddress 0.0.0.0 --server.enableCORS False --server.port 80 /app/application.py" ]