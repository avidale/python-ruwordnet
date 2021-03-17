from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


composition_table = Table(
    'composition_relation',
    Base.metadata,
    Column('word_id', String(), ForeignKey("sense.id"), primary_key=True),
    Column('phrase_id', String(), ForeignKey("sense.id"), primary_key=True)
)


derivation_table = Table(
    'derivation_relation',
    Base.metadata,
    Column('source_id', String(), ForeignKey("sense.id"), primary_key=True),
    Column('derivative_id', String(), ForeignKey("sense.id"), primary_key=True)
)


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
    """

    synset_id = Column(String(), ForeignKey('synset.id'))
    synset = relationship("Synset", back_populates="senses")

    words = relationship(
        "Sense",
        secondary=composition_table,
        back_populates='phrases',
        primaryjoin=id == composition_table.c.phrase_id,
        secondaryjoin=id == composition_table.c.word_id,
    )
    phrases = relationship(
        "Sense",
        secondary=composition_table,
        back_populates='words',
        primaryjoin=id == composition_table.c.word_id,
        secondaryjoin=id == composition_table.c.phrase_id,
    )

    sources = relationship(
        "Sense",
        secondary=derivation_table,
        back_populates='derivations',
        primaryjoin=id == derivation_table.c.derivative_id,
        secondaryjoin=id == derivation_table.c.source_id,
    )
    derivations = relationship(
        "Sense",
        secondary=derivation_table,
        back_populates='sources',
        primaryjoin=id == derivation_table.c.source_id,
        secondaryjoin=id == derivation_table.c.derivative_id,
    )

    def __repr__(self):
        return 'Sense(id="{}", name="{}")'.format(self.id, self.name)


hypernymy_table = Table(
    'hypernym_relation',
    Base.metadata,
    Column('hyponym_id', String(), ForeignKey("synset.id"), primary_key=True),
    Column('hypernym_id', String(), ForeignKey("synset.id"), primary_key=True)
)


domains_table = Table(
    'domain_relation',
    Base.metadata,
    Column('domain_id', String(), ForeignKey("synset.id"), primary_key=True),
    Column('domain_item_id', String(), ForeignKey("synset.id"), primary_key=True)
)


meronymy_table = Table(
    'meronymy_relation',
    Base.metadata,
    Column('meronym_id', String(), ForeignKey("synset.id"), primary_key=True),
    Column('holonym_id', String(), ForeignKey("synset.id"), primary_key=True)
)


instances_table = Table(
    'instance_relation',
    Base.metadata,
    Column('instance_id', String(), ForeignKey("synset.id"), primary_key=True),
    Column('class_id', String(), ForeignKey("synset.id"), primary_key=True)
)


entailment_table = Table(
    'entailment_relation',
    Base.metadata,
    Column('premise_id', String(), ForeignKey("synset.id"), primary_key=True),
    Column('conclusion_id', String(), ForeignKey("synset.id"), primary_key=True)
)


cause_table = Table(
    'cause_relation',
    Base.metadata,
    Column('cause_id', String(), ForeignKey("synset.id"), primary_key=True),
    Column('effect_id', String(), ForeignKey("synset.id"), primary_key=True)
)


pos_synonymy_table = Table(
    'pos_synonymy_relation',
    Base.metadata,
    Column('left_id', String(), ForeignKey("synset.id"), primary_key=True),
    Column('right_id', String(), ForeignKey("synset.id"), primary_key=True)
)


antonymy_table = Table(
    'antonymy_relation',
    Base.metadata,
    Column('left_id', String(), ForeignKey("synset.id"), primary_key=True),
    Column('right_id', String(), ForeignKey("synset.id"), primary_key=True)
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

    domains = relationship(
        "Synset",
        secondary=domains_table,
        back_populates='domain_items',
        primaryjoin=id == domains_table.c.domain_item_id,
        secondaryjoin=id == domains_table.c.domain_id,
    )
    domain_items = relationship(
        "Synset",
        secondary=domains_table,
        back_populates='domains',
        primaryjoin=id == domains_table.c.domain_id,
        secondaryjoin=id == domains_table.c.domain_item_id,
    )

    meronyms = relationship(
        "Synset",
        secondary=meronymy_table,
        back_populates='holonyms',
        primaryjoin=id == meronymy_table.c.holonym_id,
        secondaryjoin=id == meronymy_table.c.meronym_id,
    )
    holonyms = relationship(
        "Synset",
        secondary=meronymy_table,
        back_populates='meronyms',
        primaryjoin=id == meronymy_table.c.meronym_id,
        secondaryjoin=id == meronymy_table.c.holonym_id,
    )

    instances = relationship(
        "Synset",
        secondary=instances_table,
        back_populates='classes',
        primaryjoin=id == instances_table.c.class_id,
        secondaryjoin=id == instances_table.c.instance_id,
    )
    classes = relationship(
        "Synset",
        secondary=instances_table,
        back_populates='instances',
        primaryjoin=id == instances_table.c.instance_id,
        secondaryjoin=id == instances_table.c.class_id,
    )

    premises = relationship(
        "Synset",
        secondary=entailment_table,
        back_populates='conclusions',
        primaryjoin=id == entailment_table.c.conclusion_id,
        secondaryjoin=id == entailment_table.c.premise_id,
    )
    conclusions = relationship(
        "Synset",
        secondary=entailment_table,
        back_populates='premises',
        primaryjoin=id == entailment_table.c.premise_id,
        secondaryjoin=id == entailment_table.c.conclusion_id,
    )

    causes = relationship(
        "Synset",
        secondary=cause_table,
        back_populates='effects',
        primaryjoin=id == cause_table.c.effect_id,
        secondaryjoin=id == cause_table.c.cause_id,
    )
    effects = relationship(
        "Synset",
        secondary=cause_table,
        back_populates='causes',
        primaryjoin=id == cause_table.c.cause_id,
        secondaryjoin=id == cause_table.c.effect_id,
    )

    # pos_synonyms and antonyms are duplicated - it is easier than dirty SQLAlchemy hacks
    pos_synonyms = relationship(
        "Synset",
        secondary=pos_synonymy_table,
        back_populates='pos_synonyms_reverse',
        primaryjoin=id == pos_synonymy_table.c.right_id,
        secondaryjoin=id == pos_synonymy_table.c.left_id,
    )
    pos_synonyms_reverse = relationship(
        "Synset",
        secondary=pos_synonymy_table,
        back_populates='pos_synonyms',
        primaryjoin=id == pos_synonymy_table.c.left_id,
        secondaryjoin=id == pos_synonymy_table.c.right_id,
    )

    antonyms = relationship(
        "Synset",
        secondary=antonymy_table,
        back_populates='antonyms_reverse',
        primaryjoin=id == antonymy_table.c.right_id,
        secondaryjoin=id == antonymy_table.c.left_id,
    )
    antonyms_reverse = relationship(
        "Synset",
        secondary=antonymy_table,
        back_populates='antonyms',
        primaryjoin=id == antonymy_table.c.left_id,
        secondaryjoin=id == antonymy_table.c.right_id,
    )

    def __repr__(self):
        return 'Synset(id="{}", title="{}")'.format(self.id, self.title)
