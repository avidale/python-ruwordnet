from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Sense(Base):
    __tablename__ = 'sense'
    metadata = Base.metadata
    id = Column(String(), primary_key=True, index=True)
    name = Column(String(), index=True)
    lemma = Column(String(), index=True)
    # todo: add more fields
    """
    main_word=None,
    synt_type=None,
    poses=None,
    meaning=None,
    part_of_speech=None,
    concept_id=None,
    entry_id=None,
    synset=None,
    """

    synset_id = Column(String(), ForeignKey('synset.id'))
    synset = relationship("Synset", back_populates="senses")

    def __repr__(self):
        return 'Sense(id="{}", name="{}")'.format(self.id, self.name)


hypernymy_table = Table(
    'hypernym_relation',
    Base.metadata,
    Column('hyponym_id', String(), ForeignKey("synset.id"), primary_key=True),
    Column('hypernym_id', String(), ForeignKey("synset.id"), primary_key=True)
)


class Synset(Base):
    __tablename__ = 'synset'
    metadata = Base.metadata
    id = Column(String(), primary_key=True, index=True)
    title = Column(String())
    definition = Column(String())
    part_of_speech = Column(String())

    senses = relationship("Sense", order_by=Sense.id, back_populates="synset")

    hypernyms = relationship(
        "Synset",
        secondary=hypernymy_table,
        back_populates='hyponyms',
        primaryjoin=id == hypernymy_table.c.hyponym_id,
        secondaryjoin=id == hypernymy_table.c.hypernym_id,
    )
    hyponyms = relationship(
        "Synset",
        secondary=hypernymy_table,
        back_populates='hypernyms',
        primaryjoin=id == hypernymy_table.c.hypernym_id,
        secondaryjoin=id == hypernymy_table.c.hyponym_id,
    )

    def __repr__(self):
        return 'Synset(id="{}", title="{}")'.format(self.id, self.title)
