import pytest

from ruwordnet import RuWordNet
from ruwordnet.models import Synset, WNSynset, Sense, WNSense


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


def test_indexing():
    wn = RuWordNet()
    # test lookup synsets by id
    potential_ru = wn.get_synset_by_id("134045-N")
    assert isinstance(potential_ru, Synset)
    potential_en = wn.get_en_synset_by_id("11493827-n")
    assert isinstance(potential_en, WNSynset)
    assert potential_en in potential_ru.ili
    assert potential_ru in potential_en.ili

    # test sense lookup (ru)
    ru_potential_senses = wn.get_senses('потенциал')
    assert len(ru_potential_senses) >= 1
    assert any(potential_ru == sense.synset for sense in ru_potential_senses)
    assert potential_ru in wn.get_synsets('потенциал')

    # test sense lookup (en)
    en_potential_senses = wn.get_en_senses('potential')
    assert len(en_potential_senses) >= 1
    assert any(potential_en == sense.synset for sense in en_potential_senses)
    assert potential_en in wn.get_en_synsets('potential')

    # test arbitrary lookup
    with pytest.raises(KeyError):
        _ = wn['нет такого']
    assert isinstance(wn['134045-N'], Synset)
    assert isinstance(wn['11493827-n'], WNSynset)
    assert isinstance(wn['134045-N-189287'], Sense)
    assert isinstance(wn['electric_potential%1:19:00::'], WNSense)
    assert isinstance(wn['потенциал'][0], Sense)
    assert isinstance(wn['potential'][0], WNSense)
