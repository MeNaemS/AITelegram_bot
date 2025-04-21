FROM python:latest
WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
RUN mkdir -p /app/logs
COPY . .
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
