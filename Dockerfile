FROM python:3-stretch

WORKDIR /project

RUN pip install --upgrade pip \
  && pip install bottle opencv-python imutils requests paste

CMD ["python", "server.py"]