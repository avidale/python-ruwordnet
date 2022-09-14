"""
This script converts the raw XML thesaurus data to the sqlite format.
Requires xmltodict and tqdm packages.
"""
import argparse
import os
from collections import OrderedDict, defaultdict

from tqdm.auto import tqdm
import xmltodict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ruwordnet.models import Sense, Synset, Base, hypernymy_table, domains_table, meronymy_table, pos_synonymy_table, \
    antonymy_table, composition_table, entailment_table, cause_table, derivation_table, instances_table, related_table
from ruwordnet.models import WNSynset, WNSense, ili_table


def load_from_xml(root='.', parts='NVA', file_name='ruwordnet/static/ruwordnet.db'):
    dirname = os.path.dirname(file_name)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    if os.path.exists(file_name):
        os.remove(file_name)
    engine = create_engine(f'sqlite:///{file_name}', echo=False)
    Base.metadata.create_all(engine)

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    # load senses
    for part in parts:
        print('loading senses:', part)
        fn = os.path.join(root, f'senses.{part}.xml')
        with open(fn, 'r', encoding='utf-8') as f:
            senses = xmltodict.parse(f.read(), process_namespaces=True)
        for sense_raw in tqdm(senses['senses']['sense']):
            sense = Sense(
                id=sense_raw['@id'],
                synset_id=sense_raw['@synset_id'],
                name=sense_raw['@name'],
                lemma=sense_raw['@lemma'],
                # todo: add other keys
            )
            session.add(sense)
    session.commit()

    # load synsets
    for part in parts:
        print('loading synsets:', part)
        fn = os.path.join(root, f'synsets.{part}.xml')
        with open(fn, 'r', encoding='utf-8') as f:
            synsets = xmltodict.parse(f.read(), process_namespaces=True)
        for data in tqdm(synsets['synsets']['synset']):
            synset = Synset(
                id=data['@id'],
                title=data['@ruthes_name'],
                definition=data['@definition'],
                part_of_speech=data['@part_of_speech'],
            )
            session.add(synset)

    session.commit()

    # load interlingual index
    fn = os.path.join(root, f'ili.xml')
    if os.path.exists(fn):
        print('creating foreign Wordnet...')
        with open(fn, 'r', encoding='utf-8') as f:
            ili_raw = xmltodict.parse(f.read(), process_namespaces=True)
        pairs_to_insert = set()
        already = set()
        for match in tqdm(ili_raw['ili']['match']):
            wn_synsets = match['wn-synset']
            if isinstance(wn_synsets, OrderedDict):
                wn_synsets = [wn_synsets]
            for wnss in wn_synsets:
                pairs_to_insert.add((match['rwn-synset']['@id'], wnss['@id']))
                if wnss['@id'] in already:
                    continue
                already.add(wnss['@id'])
                lemmas = wnss['lemma']
                if isinstance(lemmas, OrderedDict):
                    lemmas = [lemmas]
                for s in lemmas:
                    if s['@key'] in already:
                        continue
                    already.add(s['@key'])
                    wn_sense = WNSense(name=s['@name'], key=s['@key'], synset_id=wnss['@id'])
                    session.add(wn_sense)
                wn_synset = WNSynset(
                    id=wnss['@id'],
                    definition=wnss['@definition'],
                )
                session.add(wn_synset)
        session.commit()
        print('connecting synsets with foreign Wordnet...')
        conn = engine.connect()
        conn.execute(ili_table.insert(), [dict(ruwn_id=id1, wn_id=id2) for id1, id2 in pairs_to_insert])
    else:
        print('interlingual index does not exist; skipping it!')

    conn = engine.connect()

    # load synset relations
    for part in parts:
        print('loading relations:', part)
        fn = os.path.join(root, f'synset_relations.{part}.xml')
        with open(fn, 'r', encoding='utf-8') as f:
            relations = xmltodict.parse(f.read(), process_namespaces=True)
        rel2values = defaultdict(set)
        for relation in tqdm(relations['relations']['relation']):
            parent_id = relation['@parent_id']
            child_id = relation['@child_id']
            # parent = session.query(Synset).filter_by(id=parent_id).first()
            # child = session.query(Synset).filter_by(id=child_id).first()
            rel2values[relation['@name']].add((parent_id, child_id))

            # ['hypernym', 'related', 'POS-synonymy', 'hyponym', 'domain', 'part holonym', 'instance hypernym',
            #   'instance hyponym', 'part meronym', 'antonym'])
            # ['hypernym', 'entailment', 'domain', 'POS-synonymy', 'hyponym', 'cause', 'antonym']
            # ['POS-synonymy', 'domain', 'hypernym', 'hyponym', 'antonym']
            # uncovered: related, hyponym, instance hyponym, part meronym
        for relation_name, pairs in rel2values.items():
            if relation_name == 'hypernym':
                conn.execute(
                    hypernymy_table.insert(),
                    [dict(hyponym_id=parent_id, hypernym_id=child_id) for parent_id, child_id in pairs]
                )
            elif relation_name == 'instance hypernym':
                conn.execute(
                    instances_table.insert(),
                    [dict(instance_id=parent_id, class_id=child_id) for parent_id, child_id in pairs]
                )
            elif relation_name == 'domain':
                conn.execute(
                    domains_table.insert(),
                    [dict(domain_item_id=parent_id, domain_id=child_id) for parent_id, child_id in pairs]
                )
            elif relation_name == 'part holonym':
                conn.execute(
                    meronymy_table.insert(),
                    [dict(meronym_id=parent_id, holonym_id=child_id) for parent_id, child_id in pairs]
                )
            elif relation_name == 'POS-synonymy':
                conn.execute(
                    pos_synonymy_table.insert(),
                    [dict(left_id=parent_id, right_id=child_id) for parent_id, child_id in pairs]
                )
                # synonyms are already duplicated in the data
                # insert = pos_synonymy_table.insert().values(right_id=parent_id, left_id=child_id)
                # conn.execute(insert)
            elif relation_name == 'antonym':
                conn.execute(
                    antonymy_table.insert(),
                    [dict(left_id=parent_id, right_id=child_id) for parent_id, child_id in pairs]
                )
                # antonyms are already duplicated in the data
                # insert = antonymy_table.insert().values(right_id=parent_id, left_id=child_id)
                # conn.execute(insert)
            elif relation_name == 'entailment':
                conn.execute(
                    entailment_table.insert(),
                    [dict(premise_id=parent_id, conclusion_id=child_id) for parent_id, child_id in pairs]
                )
            elif relation_name == 'cause':
                conn.execute(
                    cause_table.insert(),
                    [dict(cause_id=parent_id, effect_id=child_id) for parent_id, child_id in pairs]
                )
            elif relation_name == 'related':
                conn.execute(
                    related_table.insert(),
                    [dict(left_id=parent_id, right_id=child_id) for parent_id, child_id in pairs]
                )
            else:
                print('unknown relation name', relation_name)
        print('relation types', rel2values.keys())

    print('loading phrases')
    fn = os.path.join(root, 'composed_of.xml')
    with open(fn, 'r', encoding='utf-8') as f:
        relations = xmltodict.parse(f.read(), process_namespaces=True)
    pairs_to_insert = set()
    for relation in tqdm(relations['senses']['sense']):
        phrase_id = relation['@id']
        words = relation['composed_of']['sense']
        if not isinstance(words, list):
            words = [words]
        for word in words:
            word_id = word['@id']
            pairs_to_insert.add((word_id, phrase_id))
    conn.execute(
        composition_table.insert(),
        [dict(word_id=word_id, phrase_id=phrase_id) for word_id, phrase_id in pairs_to_insert]
    )

    print('loading derivations')
    fn = os.path.join(root, 'derived_from.xml')
    with open(fn, 'r', encoding='utf-8') as f:
        relations = xmltodict.parse(f.read(), process_namespaces=True)
    pairs_to_insert = set()
    for relation in tqdm(relations['senses']['sense']):
        source_id = relation['@id']
        derivatives = relation['derived_from']['sense']
        if not isinstance(derivatives, list):
            derivatives = [derivatives]
        for derivative in derivatives:
            derivative_id = derivative['@id']
            pairs_to_insert.add((source_id, derivative_id))
    conn.execute(
        derivation_table.insert(),
        [dict(source_id=source_id, derivative_id=derivative_id) for source_id, derivative_id in pairs_to_insert]
    )
    print('All loaded successfully!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert RuWordNet from xml to sqlite')
    parser.add_argument(
        '-s', '--source', default='data/rwn-2021', help='name of the directory with the source xml files'
    )
    parser.add_argument('-d', '--destination', default='ruwordnet/static/ruwordnet-2021.db',
                        help='destination database filename')
    args = parser.parse_args()
    load_from_xml(root=args.source, file_name=args.destination)
