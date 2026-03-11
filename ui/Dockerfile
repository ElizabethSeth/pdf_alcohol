FROM python:3.12-slim

WORKDIR /ui
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ui.py .

EXPOSE 8080
ENV PORT=8080
#EXPOSE 8005
ENTRYPOINT ["sh", "-c", "sleep 10 && python ui.py"]
CMD ["python", "ui.py"]