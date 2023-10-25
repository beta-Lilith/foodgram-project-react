# praktikum_new_diplom

Пока готов только бэк, временно прописан nginx.conf, чтобы поднять фронт локально.  
В директории foodgram-project-react/infra  
```
docker compose up
```
В дирректории foodgram-project-react/backend с активированным вирт.окружением
При необходимости:  
выполнить миграции  
```
python manage.py migrate
``` 
импортировать csv  
```
python manage.py load_csv
```
Поднять бэк  
```
python manage.py runserver
```