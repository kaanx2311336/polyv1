FROM mirror.gcr.io/library/python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure boot script is executable
RUN chmod +x boot.sh

EXPOSE 5000

ENTRYPOINT ["./boot.sh"]
