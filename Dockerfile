FROM python:3.10-alpine
WORKDIR /app
COPY . .
EXPOSE 8080
RUN apk add --no-cache ca-certificates curl unzip && \
    chmod +x app.py && \
    pip install --no-cache-dir flask requests
CMD ["python3", "app.py"]
