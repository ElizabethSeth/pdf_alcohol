FROM python:3.12-slim

WORKDIR /ui
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ui.py .
COPY .env /ui/.env
COPY lib lib
COPY f_card.py /ui/f_card.py
COPY s_card.py /ui/s_card.py
COPY t_card.py /ui/t_card.py


EXPOSE 8051
ENV PORT=8051
#EXPOSE 8005
#ENTRYPOINT ["sh", "-c", "sleep 50 && python ui.py"]
CMD ["python", "ui.py"]