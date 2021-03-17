from ruwordnet import RuWordNet

wn = RuWordNet()
q = wn.get_senses('замок')

if not q:
    print('no results found')

for i, sense in enumerate(q):
    print(i)
    print(sense)
    print(sense.synset)
    print(sense.synset.senses)
    print(sense.synset.hypernyms)

print(wn.get_senses('коса'))
print(wn.get_synsets('коса'))
