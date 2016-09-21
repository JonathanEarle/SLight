import pickle

one=1
two=2

while True:
	data={"one":one,"two":two}
	pickle.dump(data,open("storedData.p","wb"))	
	loaded=pickle.load(open("storedData.p","rb"))
	print(loaded)
	one=input("Enter one: ")
	two=input("Enter two: ")
