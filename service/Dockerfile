FROM python:3

WORKDIR /usr/app

ADD ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD ./ ./

CMD ["python", "app.py"]