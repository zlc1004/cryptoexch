import json

out={}

with open("priv/amount.txt","r") as f:
    dat=f.read().split("\n")

for i in dat:
    if i:
        i=i.split(",")
        out[i[0]]=i[1]

with open("priv/amount.json","w") as f:
    f.write(json.dumps(out))