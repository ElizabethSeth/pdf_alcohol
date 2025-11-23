FROM python:3.12-slim

WORKDIR /ui
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ui.py .
ENV PORT=8080

EXPOSE 8080


#ENTRYPOINT ["sh", "-c", "sleep 10 && python ui.py"]
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080', timeout=5)"

CMD ["python", "ui.py"]