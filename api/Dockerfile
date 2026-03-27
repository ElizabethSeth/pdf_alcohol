FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /main
COPY .env .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py ./main.py
COPY lib lib
COPY combined_alcohol_companies_schema.csv .
EXPOSE 8003
CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8003"]