# Установка
Клонирование репозитория
```
git clone https://github.com/ValMor561/ExtenderBH.git
```
Установка зависимостей
```
cd ExtenderBH
pip install -r requirements.txt
```
# Использование
```
python extender_bh.py -h
```
![](img/general_help.png)
На текущий момент инструмент состоит из 9 основных модулей, а так же вспомогательного модуля для работы с базой данных neo4j, который используется во всех основных модулях.
## Вспомогательный модуль neo4j
![](img/neo4j_help.png)
Включается флагом `-na`, и содержит два обязательных параметра - имя пользователя базы neo4j (`-nl`) и пароль (`-np`)
Ссылка до базы данных neo4j, а также имя базы данных устанавливается по умолчанию, однако если есть необходимость в изменении этих параметров, можно задать свои значения.
## Модуль session
![](img/session_help.png)
Обрабатывает результат работы скрипта [Get-LoggedOn.py](https://gist.icoder.workers.dev/GeisericII/6849bc86620c7a764d88502df5187bd0), вывод которого, видоизменен для упрощения обработки. Измененный скрипт находится в папке `additional_scripts`. Пример входного файла в папке `examples`.
Помимо этого использует результат работы [TrustMeter](https://zeronetworks.com/platform/trustmeter), для перевода IP адресов в NetBIOS имена. Походят как результаты в формате `json`, так и в `csv`.
Пример команды для запуска модуля:
```
python .\extender_bh.py session -si .\sessions.txt -tm '.\test.local Report.json' -na -nl neo4j -np 1234
```
## Модуль spray
![](img/spray_help.png)
Обрабатывает результат атаки Password Spraying, с помощью [NetExec](https://github.com/Pennyw0rth/NetExec). Помечает положительные результаты как захваченные узлы, а так же устанавливает атрибут `ClearTextPassword`. 
Если найденная учетная запись обладает правами администратора на системе, добавит ребро `AdminTo`. 
Пример команды для запуска `nxc`:
```
nxc smb <dc-ip> -u user.txt -p <pass> --continue-on-succes | tee spray.txt
```
Пример команды для запуска модуля:
```
python extender_bh.py spray -i spray.txt -na -nl neo4j -np 1234
```
