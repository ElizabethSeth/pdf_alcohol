FROM python:3.12-slim

WORKDIR /ui
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gradio_ui.py .

EXPOSE 8003

ENTRYPOINT ["python", "gradio_ui.py"]
