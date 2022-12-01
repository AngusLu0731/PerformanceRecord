FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /performanceRecord
WORKDIR /performanceRecord
COPY requirements.txt /performanceRecord/
RUN pip install -r requirements.txt
COPY . /performanceRecord/