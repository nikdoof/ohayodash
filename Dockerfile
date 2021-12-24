FROM python:3.9-alpine
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./ohayodash /app/ohayodash
CMD ["gunicorn", "--bind", "0.0.0.0:80", "ohayodash.app:app"]