FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD exec streamlit run app.py --server.port ${PORT} --server.address 0.0.0.0
