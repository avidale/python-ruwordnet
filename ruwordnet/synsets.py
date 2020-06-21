class Sense:
    def __init__(
        self,
        id,
        synset_id,
        name,
        lemma,
        main_word=None,
        synt_type=None,
        poses=None,
        meaning=None,
        part_of_speech=None,
        concept_id=None,
        entry_id=None,
        synset=None,
    ):
        self.id: str = id
        self.synset_id: str = synset_id
        self.name: str = name
        self.lemma: str = lemma
        self.main_word = main_word
        self.synt_type = synt_type
        self.poses = poses
        self.meaning = meaning
        self.part_of_speech = part_of_speech
        self.concept_id = concept_id,
        self.entry_id = entry_id
        self.synset = synset

    def __repr__(self):
        return 'Sense(id="{}", name="{}")'.format(self.id, self.name)


class Synset:
    def __init__(
            self, id, title, part_of_speech, definition='', sense=None,
            hypernyms=None, hyponyms=None,
    ):
        self.id = id
        self.title = title
        self.part_of_speech = part_of_speech
        self.definition = definition
        self.sense = sense or []
        self.hypernyms = hypernyms or []
        self.hyponyms = hyponyms or []

    def __repr__(self):
        return 'Synset(id="{}", title="{}")'.format(self.id, self.title)
