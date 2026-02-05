FROM python:3.10-alpine

WORKDIR /app

RUN apk add --no-cache curl

COPY requirements.txt app.py ./

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 9002

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:9002/health || exit 1

CMD ["python", "app.py"]