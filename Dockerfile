FROM python:3.12

WORKDIR /code

COPY requirements.txt .

RUN pip install --upgrade pip
RUN apt-get update
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "version2/front.py"]
