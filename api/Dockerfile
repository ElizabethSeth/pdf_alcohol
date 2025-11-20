FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

ENV OPENAI_API_KEY=${OPENAI_API_KEY}

WORKDIR /api
#COPY qdrant_data qdrant_data
#COPY .env .env
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api.py ./api.py

EXPOSE 8002
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8002"]