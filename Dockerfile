FROM python:3.11.8
LABEL description="Gas sensors API"
WORKDIR /code

RUN pip install poetry==1.7.1

COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install
EXPOSE 5000

COPY . .

CMD poetry run python app.py
