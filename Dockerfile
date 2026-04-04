FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app


RUN pip install --no-cache-dir --default-timeout=1000 gradio psycopg2-binary google-cloud-storage

RUN pip install --no-cache-dir --default-timeout=1000 paddlepaddle==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/

RUN pip install --no-cache-dir --default-timeout=1000 -U "paddleocr[doc-parser]"

COPY . .

EXPOSE 8080

CMD ["python", "app.py"]