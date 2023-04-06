FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app .
EXPOSE 8000
WORKDIR /

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

CMD uvicorn app.main:app --host "0.0.0.0" --port 8000 --forwarded-allow-ips="*" --proxy-headers