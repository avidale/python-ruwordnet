# python-ruwordnet
Питоновская обёртка для тезауруса [RuWordNet](https://ruwordnet.ru/ru).

Чтобы воспользоваться тезаурусом, склонируйте данный репозиторий 
и запустите следующий код
```python
from ruwordnet import RuWordNet
wn = RuWordNet()
wn.load_from_xml(root='data')
```

После этого можно, например, искать синсеты, в которые входит слово
```python
for sense in wn.get_senses('замок'):
    print(sense.synset)
# Synset(id="126228-N", title="СРЕДНЕВЕКОВЫЙ ЗАМОК")
# Synset(id="114707-N", title="ЗАМОК ДЛЯ ЗАПИРАНИЯ")
```

Для каждого синсета можно глядеть на гиперонимы...
```python
wn.get_senses('спаржа')[0].synset.hypernyms
# [Synset(id="348-N", title="ОВОЩИ"),
#  Synset(id="4789-N", title="ТРАВЯНИСТОЕ РАСТЕНИЕ"),
#  Synset(id="6878-N", title="ОВОЩНАЯ КУЛЬТУРА")]
```
... или, наоборот, на гипонимы
```python
wn.get_senses('спаржа')[0].synset.hypernyms[0].hyponyms
# [Synset(id="107993-N", title="АРТИШОК"),
# Synset(id="108482-N", title="СПАРЖА"),
# Synset(id="118660-N", title="ЗЕЛЕНЫЙ ГОРОШЕК"),
# ...
```

