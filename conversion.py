"""
This script converts the raw XML thesaurus data to the sqlite format.
Requires xmltodict and tqdm packages.
"""
import argparse
import os

from tqdm.auto import tqdm
import xmltodict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ruwordnet.models import Sense, Synset, Base, hypernymy_table, domains_table, meronymy_table, pos_synonymy_table, \
    antonymy_table, composition_table, entailment_table, cause_table, derivation_table, instances_table


def load_from_xml(root='.', parts='NVA', file_name='ruwordnet/static/ruwordnet.db'):
    dirname = os.path.dirname(file_name)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

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

    conn = engine.connect()

    # load synset relations
    for part in parts:
        print('loading relations:', part)
        fn = os.path.join(root, f'synset_relations.{part}.xml')
        with open(fn, 'r', encoding='utf-8') as f:
            relations = xmltodict.parse(f.read(), process_namespaces=True)
        for relation in tqdm(relations['relations']['relation']):
            parent_id = relation['@parent_id']
            child_id = relation['@child_id']
            # parent = session.query(Synset).filter_by(id=parent_id).first()
            # child = session.query(Synset).filter_by(id=child_id).first()
            if relation['@name'] == 'hypernym':
                insert = hypernymy_table.insert().values(hyponym_id=parent_id, hypernym_id=child_id)
                conn.execute(insert)
            elif relation['@name'] == 'instance hypernym':
                insert = instances_table.insert().values(instance_id=parent_id, class_id=child_id)
                conn.execute(insert)
            elif relation['@name'] == 'domain':
                insert = domains_table.insert().values(domain_item_id=parent_id, domain_id=child_id)
                conn.execute(insert)
            elif relation['@name'] == 'part holonym':
                insert = meronymy_table.insert().values(meronym_id=parent_id, holonym_id=child_id)
                conn.execute(insert)
            elif relation['@name'] == 'POS-synonymy':
                insert = pos_synonymy_table.insert().values(left_id=parent_id, right_id=child_id)
                conn.execute(insert)
                # synonyms are already duplicated in the data
                # insert = pos_synonymy_table.insert().values(right_id=parent_id, left_id=child_id)
                # conn.execute(insert)
            elif relation['@name'] == 'antonym':
                insert = antonymy_table.insert().values(left_id=parent_id, right_id=child_id)
                conn.execute(insert)
                # antonyms are already duplicated in the data
                # insert = antonymy_table.insert().values(right_id=parent_id, left_id=child_id)
                # conn.execute(insert)
            elif relation['@name'] == 'entailment':
                insert = entailment_table.insert().values(premise_id=parent_id, conclusion_id=child_id)
                conn.execute(insert)
            elif relation['@name'] == 'cause':
                insert = cause_table.insert().values(cause_id=parent_id, effect_id=child_id)
                conn.execute(insert)

    print('loading phrases')
    fn = os.path.join(root, 'composed_of.xml')
    with open(fn, 'r', encoding='utf-8') as f:
        relations = xmltodict.parse(f.read(), process_namespaces=True)
    for relation in tqdm(relations['senses']['sense']):
        phrase_id = relation['@id']
        words = relation['composed_of']['sense']
        if not isinstance(words, list):
            words = [words]
        for word in words:
            word_id = word['@id']
            insert = composition_table.insert().values(word_id=word_id, phrase_id=phrase_id)
            conn.execute(insert)

    print('loading derivations')
    fn = os.path.join(root, 'derived_from.xml')
    with open(fn, 'r', encoding='utf-8') as f:
        relations = xmltodict.parse(f.read(), process_namespaces=True)
    for relation in tqdm(relations['senses']['sense']):
        source_id = relation['@id']
        derivatives = relation['derived_from']['sense']
        if not isinstance(derivatives, list):
            derivatives = [derivatives]
        for derivative in derivatives:
            derivative_id = derivative['@id']
            insert = derivation_table.insert().values(source_id=source_id, derivative_id=derivative_id)
            conn.execute(insert)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert RuWordNet from xml to sqlite')
    parser.add_argument('-s', '--source', default='data', help='name of the directory with the source xml files')
    parser.add_argument('-d', '--destination', default='ruwordnet/static/ruwordnet.db',
                        help='destination database filename')
    args = parser.parse_args()
    load_from_xml(root=args.source, file_name=args.destination)
