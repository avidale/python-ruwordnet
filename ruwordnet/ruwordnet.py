from typing import List, Union
from .models import Sense, Synset
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

    def __getitem__(self, item: str) -> Union[Synset, Sense, List[Sense]]:
        """ Retrieve sense or synset by its id """
        synset = self.session.query(Synset).filter_by(id=item).first()
        if synset:
            return synset
        sense = self.session.query(Sense).filter_by(id=item).first()
        if sense:
            return sense

        senses = self.get_senses(item)
        if senses:
            return senses
        raise KeyError()

    def get_senses(self, lemma: str) -> List[Sense]:
        """ Retrieve a list of senses by a given lemma """
        q = lemma.upper().strip()
        return self.session.query(Sense).filter_by(lemma=q).all()

    def get_synsets(self, lemma: str) -> List[Synset]:
        """ Retrieve a list of synsets by a given lemma """
        return [sense.synset for sense in self.get_senses(lemma) if sense.synset]
