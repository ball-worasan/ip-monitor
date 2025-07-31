FROM python:3.11-slim

WORKDIR /app

# ติดตั้ง dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมด
COPY . .

# สร้างผู้ใช้ non-root (optional)
RUN addgroup --system app && adduser --system --ingroup app app && chown -R app:app /app
USER app

ENV FLASK_ENV=production

EXPOSE 8000

# ให้ start script รันทั้งสอง process
RUN chmod +x start.sh

# Healthcheck: ใช้ไฟล์ healthcheck.py
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD ["python", "healthcheck.py"]

CMD ["./start.sh"]
