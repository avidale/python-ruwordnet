from typing import List, Optional, Union
from .models import Sense, Synset, WNSynset, WNSense
from .utils import get_default_session


class RuWordNet:
    def __init__(self, filename_or_session=None):
        if filename_or_session is None:
            session = get_default_session()
        elif isinstance(filename_or_session, str):
            session = get_default_session(filename_or_session)
        else:
            session = filename_or_session
        self.session = session

    @property
    def synsets(self) -> List[Sense]:
        """ List of all available synsets """
        return self.session.query(Synset).all()

    @property
    def senses(self) -> List[Sense]:
        """ List of all available senses """
        return self.session.query(Sense).all()

    def __getitem__(self, item: str) -> Union[Synset, Sense, List[Sense], WNSynset, WNSense, List[WNSense]]:
        """ Retrieve sense or synset by its id or name (first try Russian, then English).
        Raise KeyError if nothing is found. """
        synset = self.get_synset_by_id(item)
        if synset:
            return synset
        sense = self.session.query(Sense).filter_by(id=item).first()
        if sense:
            return sense

        senses = self.get_senses(item)
        if senses:
            return senses

        en_synset = self.get_en_synset_by_id(item)
        if en_synset:
            return en_synset

        en_sense = self.session.query(WNSense).filter_by(key=item).first()
        if en_sense:
            return en_sense

        en_senses = self.get_en_senses(item)
        if en_senses:
            return en_senses

        raise KeyError()

    def get_senses(self, lemma: str) -> List[Sense]:
        """ Retrieve a list of senses by a given lemma """
        q = lemma.upper().strip()
        return self.session.query(Sense).filter_by(lemma=q).all()

    def get_synsets(self, lemma: str) -> List[Synset]:
        """ Retrieve a list of synsets by a given lemma """
        return [sense.synset for sense in self.get_senses(lemma) if sense.synset]

    def get_synset_by_id(self, id: str) -> Optional[Synset]:
        """ Retrieve a synset by id or return None """
        return self.session.query(Synset).filter_by(id=id).first()

    def get_en_synset_by_id(self, id: str) -> Optional[WNSynset]:
        """ Retrieve a synset by id or return None (English WordNet) """
        return self.session.query(WNSynset).filter_by(id=id).first()

    def get_en_senses(self, lemma: str) -> List[WNSense]:
        """ Retrieve a list of senses by a given lemma (English WordNet) """
        q = lemma.lower().strip().replace(' ', '_')
        return self.session.query(WNSense).filter_by(name=q).all()

    def get_en_synsets(self, lemma: str) -> List[WNSynset]:
        """ Retrieve a list of synsets by a given lemma (English WordNet) """
        return [sense.synset for sense in self.get_en_senses(lemma) if sense.synset]
