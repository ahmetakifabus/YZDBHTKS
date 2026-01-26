FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

RUN mkdir -p /code/uploads && chmod 777 /code/uploads
RUN mkdir -p /code/static/avatars && chmod 777 /code/static/avatars
RUN chmod 777 /code

CMD ["python", "main_app.py"]
