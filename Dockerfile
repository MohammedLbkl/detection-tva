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


RUN pip install --no-cache-dir gradio psycopg2-binary google-cloud-storage && \
    pip install --no-cache-dir paddlepaddle==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/ && \
    pip install --no-cache-dir -U "paddleocr[doc-parser]"

COPY . .

EXPOSE 8080

CMD ["python", "app.py"]