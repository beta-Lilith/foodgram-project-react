![main workflow badge](https://github.com/beta-Lilith/foodgram-project-react/actions/workflows/main.yml/badge.svg)
# FOODGRAM PROJECT  

## ОПИСАНИЕ ПРОЕКТА  
Пользователи могут регистрироваться, добавлять, редактировать, удалять свои рецепты.  
Все рецепты отображаются на главной, есть возможность добавить/удалить рецепт в избранное и в список покупок, список покупок можно скачать.  
Также есть возможность подписаться/отписаться на другого автора.    
Стандартная админка Django.  
  
Цель дипломного проекта: применить знания, полученные в ходе обучения на курсе Python-разработчик.  
  
## ТЕХНОЛОГИИ
- Python 3.9
- Django 3.2.3
- Django REST Framework 3.12.4
- Linux Ubuntu
- Yandex Cloud
- Nginx
- Gunicorn
- Docker
- GitHub Actions
  
## ЗАПУСТИТЬ ПРОЕКТ
  
Клонировать репозиторий:
```
git clone https://github.com/beta-Lilith/foodgram-project-react.git 
```
  
Добавить секреты для Actions на GitHub:  
(foodgram-project-react -> Settings -> Secrets and variables -> Actions)  
  
`DOCKER_PASSWORD` - пароль учетной записи DockerHub  
`DOCKER_USERNAME` - имя пользователя учетной записи Docker Hub  
`HOST` - ip-адресс вашего удаленного сервера  
`USER` - имя пользователя на удаленном сервере  
`SSH_KEY` - закрытый SSH ключ от удаленного сервера  
`SSH_PASSPHRASE` - пассфраза от удаленного сервера  
`TELEGRAM_TO` - ваш телеграм id  
`TELEGRAM_TOKEN` - token вашего бота  
  
### НА УДАЛЕННОМ СЕРВЕРЕ: 
  
Установите Docker Compose поочередно выполнив команды:  
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
  
Откройте настрой nginx в редакторе nano:
```
sudo nano /etc/nginx/sites-enabled/default
```
  
Отредактируйте по шаблону:
```
server {
    listen 80;
    server_name <ip-вашего сервера> <ваше доменное имя>;
    server_tokens off;
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```
  
Получить SSL-сертификат от Let’s Encrypt  
Установить certbot:  
```
sudo apt install snapd
```
Далее сервер, скорее всего, попросит вам перезагрузить операционную систему. Сделайте это, а потом последовательно выполните команды:  
```
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```
Чтобы начать процесс получения сертификата, введите команду:  
```
sudo certbot --nginx
```
Перезагрузите конфигурацию Nginx:  
```
sudo systemctl reload nginx
```
Чтобы узнать актуальный статус сертификата и сколько дней осталось до его перевыпуска:  
```
sudo certbot certificates
```
Чтобы убедиться, что сертификат будет обновляться автоматически:  
```
sudo certbot renew --dry-run
```
  
Перейдите в корневую директорию, создайте папку foodgram и перейдите в нее:
```
cd
mkdir foodgram
cd foodgram
```
  
Создать файл .evn на примере .env.example в корне проекта репозитория.
  
Скопируйте docker-compose.production.yml в корневую дирректорию удобным для вас способом
  
Запустить docker-compose.production в режиме демона:
```
sudo docker compose -f docker-compose.production.yml up -d
```
  
Выполнить миграции и собрать статику бэкенда, загрузить ингредиенты и теги:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /back_static/static/
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_tags
```
  
Создать суперпользователя:
  
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
  
Готово!  

Документация доступна по адресу:  
https://yafoodgram.zapto.org/api/docs/  
  
## АВТОР
Оскомова Ксения