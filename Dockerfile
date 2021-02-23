FROM python:3.6
EXPOSE 80 8000
RUN mkdir /Users/yanhuaqiang/python/demo -p
COPY . /Users/yanhuaqiang/python/demo
WORKDIR /Users/yanhuaqiang/python/demo
RUN pip install -r requirements.txt -i  https://mirrors.aliyun.com/pypi/simple/
WORKDIR /Users/yanhuaqiang/python/demo
CMD python manage.py runserver 0.0.0.0:8000
