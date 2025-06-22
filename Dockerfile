# pull the official base image
FROM python:3.12.0-alpine


#Укажем мета данные
LABEL authors="zeroneed"

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочий каталог можно выбрать любой, например, '/' или '/home' и т. д.
WORKDIR /usr/src/app

#Копируем удаленный файл в рабочем каталоге в контейнере
#COPY main.py ./
# Теперь структура выглядит следующим образом '/usr/src/app/main.py'
# copy project to work directory
COPY . .

# update pip and install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

#Для запуска программного обеспечения следует использовать инструкцию CMD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
#CMD [ "python", "./main.py"]


# создание образа
# docker build --tag fastapi_hello_word:latest .
# --tag Устанавливает тег для образа (latest)
# Точка . указывает на то, что Dockerfile находится в текущем рабочем каталоге

# создание контейнера
# docker run --name fastapi_hello_word -d -p 80:80 fastapi_hello_word:latest
# --name: Устанавливает имя контейнера Docker
# -d: Заставляет образ работать  в фоновом режиме
# p 80:80: Сопоставляет порт 80 в контейнере Docker с портом 80 на локальном хосте.
# fastapi_hello_word:latest: Указывает, какой образ используется для сборки контейнера Docker.


