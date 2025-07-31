FROM python:3.10-slim

WORKDIR /app

COPY autotestlab/ ./autotestlab/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "autotestlab/app.py"]
