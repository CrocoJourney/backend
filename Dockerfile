FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app .
EXPOSE 8000
CMD uvicorn main:app --host "0.0.0.0" --port 8000 --forwarded-allow-ips="*" --proxy-headers