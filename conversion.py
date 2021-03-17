import argparse
import os

from tqdm.auto import tqdm
import xmltodict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ruwordnet.models import Sense, Synset, Base, hypernymy_table


def load_from_xml(root='.', parts='NVA', file_name='static/ruwordnet.db'):
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
            session.add(synset)
            # adding sense to the synset is redundant, because senses already have synset id
            #for sense_raw in senses:
            #    sense = session.query(Sense).filter_by(id=sense_raw['@id']).first()
            #    synset.senses.append(sense)

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
            #parent = session.query(Synset).filter_by(id=parent_id).first()
            #child = session.query(Synset).filter_by(id=child_id).first()
            if relation['@name'] == 'hypernym':
                insert = hypernymy_table.insert().values(hyponym_id=parent_id, hypernym_id=child_id)
                conn.execute(insert)
                #if child not in parent.hypernyms:
                #    parent.hypernyms.append(child)


    # todo: add other relations
    # todo: add sense relations (part of, derived_from)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert RuWordNet from xml to sqlite')
    parser.add_argument('-s', '--source', default='data', help='name of the directory with the source xml files')
    parser.add_argument('-d', '--destination', default='static/ruwordnet.db', help='destination database filename')
    args = parser.parse_args()
    load_from_xml(root=args.source, file_name=args.destination)
