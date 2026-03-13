FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -e . && \
    pip install pytest pytest-cov pytest-mock && \


CMD ["pytest"]