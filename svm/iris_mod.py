import csv

iris = open("../data/iris.csv",'r')
iris_mod = open("../data/iris_mod.csv",'w')
start = csv.reader(iris)
end = csv.writer(iris_mod)

for row in start:
	new_row = row[0:4]

	if row[4] == "Iris-setosa":
		new_row.append(0.0)
	elif row[4] == "Iris-versicolor":
		new_row.append(1.0)
	elif row[4] == "Iris-virginica":
		new_row.append(2.0)

	print(new_row)
	end.writerow(tuple(new_row))

iris.close()
iris_mod.close()