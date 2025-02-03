FROM python:3.11
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERD=1
WORKDIR /code
COPY backend/requirements.txt /code/
RUN pip install -r  requirements.txt
RUN apt-get update && apt-get install -y gettext
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY . /code/