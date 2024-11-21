import requests
while True:
    in1=input("Enter the URL: ")
    if not (in1.startswith("https://")):
        in1="https://raabit.org/"+in1
    res=requests.get(in1)
    url="/".join((in1.replace("https://","").split("/")[1:]))
    with open("./public/"+url,"wb") as file:
        file.write(res.content)