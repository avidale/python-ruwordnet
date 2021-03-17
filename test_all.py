from ruwordnet import RuWordNet


def test_thesaurus():
    wn = RuWordNet(filename_or_session='ruwordnet/static/ruwordnet.db')
    assert len(wn.get_senses('замок')) == 2
    asparagus = wn.get_senses('спаржа')[0].synset
    assert len(asparagus.hypernyms) == 3
    vegetables = wn.get_senses('спаржа')[0].synset.hypernyms[0]
    assert len(vegetables.hyponyms) == 14
