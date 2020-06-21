import xmltodict
import os

from typing import List, Dict

from ruwordnet.synsets import Sense, Synset


class RuWordNet:
    def __init__(self):
        self._id2synset: Dict[str, Synset] = {}
        self._id2sense: Dict[str, Sense] = {}
        self._word2sense: Dict[str, List[str]] = {}

    @property
    def synsets(self):
        return self._id2synset.values()

    @property
    def senses(self):
        return self._id2sense.values()

    def __getitem__(self, item):
        if item in self._id2synset:
            return self._id2synset[item]
        if item in self._id2sense:
            return self._id2sense[item]
        senses = self.get_senses(item)
        if senses:
            return senses
        raise KeyError()

    def get_senses(self, lemma) -> List[Sense]:
        return [
            self._id2sense[id]
            for id in self._word2sense.get(lemma.upper().strip(), [])
        ]

    def get_synsets(self, lemma) -> List[Synset]:
        return [sense.synset for sense in self.get_senses(lemma) if sense.synset]

    def load_from_xml(self, root='.', parts='NVA'):
        # load senses
        for part in parts:
            fn = os.path.join(root, f'senses.{part}.xml')
            with open(fn, 'r', encoding='utf-8') as f:
                senses = xmltodict.parse(f.read(), process_namespaces=True)
            for sense_raw in senses['senses']['sense']:
                sense = Sense(
                    id=sense_raw['@id'],
                    synset_id=sense_raw['@synset_id'],
                    name=sense_raw['@name'],
                    lemma=sense_raw['@lemma'],
                    # todo: add other keys
                )
                self._id2sense[sense.id] = sense
                if sense.name not in self._word2sense:
                    self._word2sense[sense.name] = []
                if sense.id not in self._word2sense[sense.name]:
                    self._word2sense[sense.name].append(sense.id)
        # load synsets
        for part in parts:
            fn = os.path.join(root, f'synsets.{part}.xml')
            with open(fn, 'r', encoding='utf-8') as f:
                synsets = xmltodict.parse(f.read(), process_namespaces=True)
            for data in synsets['synsets']['synset']:
                if isinstance(data['sense'], list):
                    senses = data['sense']
                else:
                    senses = [data['sense']]
                synset = Synset(
                    id=data['@id'],
                    title=data['@ruthes_name'],
                    definition=data['@definition'],
                    part_of_speech=data['@part_of_speech'],
                )
                for sense in senses:
                    sense = self._id2sense[sense['@id']]
                    sense.synset = synset
                    synset.sense.append(sense)
                self._id2synset[synset.id] = synset
        # load synset relations
        for part in parts:
            fn = os.path.join(root, f'synset_relations.{part}.xml')
            with open(fn, 'r', encoding='utf-8') as f:
                relations = xmltodict.parse(f.read(), process_namespaces=True)
            for relation in relations['relations']['relation']:
                parent = self._id2synset[relation['@parent_id']]
                child = self._id2synset[relation['@child_id']]
                if relation['@name'] == 'hypernym':
                    if child not in parent.hypernyms:
                        parent.hypernyms.append(child)
                if relation['@name'] == 'hyponym':
                    if child not in parent.hyponyms:
                        parent.hyponyms.append(child)
                # todo: add other relations
        # todo: add sense relations (part of, derived_from)
