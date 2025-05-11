FROM python:3.10.0-alpine3.15

WORKDIR /app

COPY server/requirements.txt .
RUN pip install -r requirements.txt

COPY shared/ ./shared/
COPY server/ ./server/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "server/run.py"] 