FROM python:3.12-slim

WORKDIR /ui
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ui.py .

EXPOSE 8051
ENV PORT=8051
#EXPOSE 8005
#ENTRYPOINT ["sh", "-c", "sleep 50 && python ui.py"]
CMD ["python", "ui.py"]