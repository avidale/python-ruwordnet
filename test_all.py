from ruwordnet import RuWordNet


def test_thesaurus():
    wn = RuWordNet(filename_or_session='ruwordnet/static/ruwordnet.db')
    assert len(wn.get_senses('замок')) == 2
    asparagus = wn.get_senses('спаржа')[0].synset
    assert len(asparagus.hypernyms) == 3
    vegetables = wn.get_senses('спаржа')[0].synset.hypernyms[0]
    assert len(vegetables.hyponyms) == 14


def test_new_thesaurus():
    wn = RuWordNet(filename_or_session='ruwordnet/static/ruwordnet-2021.db')
    assert len(wn.get_senses('замок')) == 2
    asparagus = wn.get_senses('спаржа')[0].synset
    assert len(asparagus.hypernyms) == 3
    vegetables = wn.get_senses('спаржа')[0].synset.hypernyms[0]
    assert len(vegetables.hyponyms) == 15

    assert wn['овощехранилище'][0].synset in vegetables.related

    ru_dwelling, ru_city = wn['132821-N'], wn['134530-N']
    assert ru_city in ru_dwelling.instances
    assert ru_dwelling in ru_city.classes

    geo_science = wn["1702-N"]
    assert geo_science in ru_city.domains
    assert ru_city in geo_science.domain_items
