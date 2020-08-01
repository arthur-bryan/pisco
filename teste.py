asa = ["asdasd", "asdsfx", "x"]

def find(x):
    if "x" in x:
        return True

res = filter(find, asa)
for i in res:
	print(i)
