# 1. תביא לי מחשב לינוקס קטן שכבר מותקן עליו פייתון 3.9
FROM python:3.9-slim

# 2. תיצור בתוך המחשב הזה תיקייה בשם app ותעבוד בתוכה
WORKDIR /app

# 3. תעתיק פנימה את רשימת הספריות ותתקין אותן
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. תעתיק פנימה את שאר הקבצים מהתיקייה שלנו (את קוד הפייתון)
COPY . .

# 5. כשהקונטיינר נדלק, תריץ את פייתון עם הקובץ שלנו
ENTRYPOINT ["python", "stocks_etl.py"]