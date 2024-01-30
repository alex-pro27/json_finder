# Поиск по JSON Файлу со структурой данных: список словарей
Пример:
```json
[
   {
    "id": 1,
    "title": "Report agency simple family.",
    "rand_float": 0.0382615286355954,
    "rand_int": 316984
  },
  {
    "id": 2,
    "title": "Next often despite family.",
    "rand_float": 0.5743787352491577,
    "rand_int": 293573
  }
]
```

Версия Python: >= 3.8 

Установка:
```bash
pip install -r requirements.txt
```

Доступные Опции:
```
options:
  -f FILEPATH           Путь к файлу
  -t TERMS, --term      Условие поиска, пример: 'name:Some test' или 'name:Some te:part' Где name - ключ, Some test - значение, :part - Поиск по части значения
  -o OPERATOR, --operator Оператор сравнения OR - найденое совпадение хотябы в одном из ключей (По умолчанию) | AND - полное совпадение во всех ключах
```

Примеры использования:
Поиск частичным совпадением в title и с использованием оператора AND
```bash
python3 main.py --operator AND -f C:\Users\Василий\data.json -t 'title:family:part' -t 'rand_int:293573'
```

Поиск по диапазону значений
```bash
python main.py -f C:\Users\Василий\data.json -t "rand_int:3358:gt" -t "rand_int:3370:lt"
```
Доступные операторы сравнения:
```
gt - больше
lt - меньше
gte - больше или равно
lte - меньше или равно
```
