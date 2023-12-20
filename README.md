# Псевдорулетка 

### Как настроить 

1) Нужно вызвать Docker Compose - `docker-compose up --build`
2) Вызвать функцию для ролла - `curl -X POST -H "Content-Type: application/json" -d '{"user_id": 3}' http://127.0.0.1:5000/spin`
3) Получить статистику - `curl -X GET -H "Content-Type: application/json" http://127.0.0.1:5000/stats`
