# Репозиторий к семинару "Основы backend-разработки"

## Что нужно сделать перед семинаром?
#### Собрать проект на виртуалке
1. зайти на виртуалку и склонировать на нее этот репозиторий
2. выполнить команду `docker build -t ds-backend .`
3. запустить сервис командой `./run.sh`
4. открыть в браузере страничку *http://<vm_ip>:8080* и проверить, что выводится слово *"Hello"*

#### Настроить VS Code для удаленного редактирования
1. установить VS Code на свою машину
2. установить в VS Code расширение "Remote - SSH" - [инструкция](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) (раздел "Getting started")
3. открыть проект в VS Code через Remote SSH


### Пример тестирования сервиса
```
curl -X GET http://158.160.33.21:8080/readPlateNumberById   -H "Content-Type: application/json"   -d '{"image_id": 10022}'
```