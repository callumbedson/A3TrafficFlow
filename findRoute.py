import pandas as pd


def findRoute(source, dest):
	print("Loading Workbook")
	#Read csv with pandas
	df = pd.read_csv("SCATSGraph.csv")
	
	#Initialize node variables
	currentPath = []
	unexplored = [source]
	explored = []
	allRoutes = []

	print("running search")	
	#Loop to find paths while theres nodes that havent been searched
	while unexplored:
		#Depth first so gets 1 index 
		currentNode = unexplored.pop()
		currentPath.append(currentNode)
		deadEnd = True #hmm
		print("current path: ", currentPath)
		for index,row in df.iterrows():
			#Assign columns a and b for ease
			A = row["SCATSA"]
			B = row["SCATSB"]
			if (A == source and B == dest) or (B == source and A == dest):
				break
			#print(A, B)
			if currentNode == A:
				if B == dest:
					currentPath.append(dest)
					print("Found route")
					allRoutes.append(currentPath)
					explored.append(currentNode)
					currentPath = []
					unexplored = [source]
					break
				elif B not in explored and B not in unexplored and B not in currentPath:
					unexplored.append(B)
					#print("path found between ", A, B)
					deadEnd = False
			elif currentNode == B:
				if A == dest:
					currentPath.append(dest)
					print("Found route")
					allRoutes.append(currentPath)
					explored.append(currentNode)
					currentPath = []
					unexplored = [source]
					break
				elif A not in explored and A not in unexplored and A not in currentPath:
					unexplored.append(A)
					#print("path found between ", B, A)
					deadEnd = False
		if deadEnd == True and currentPath:
			print("deadend, popping: ", currentPath.pop()) #hmm

	print(allRoutes)
	return attachDist(allRoutes)

def attachDist(allRoutes):
	df = pd.read_csv("SCATSGraph.csv")
	routeCosts = []
	for routes in allRoutes:
		#i is to get next value in the path
		i = 0
		routeCost = []
		for scat in routes:
			i += 1
			foundDist = False
			if i < len(routes):
				for index,row in df.iterrows():
					if foundDist == True:
						break
					#Assign columns from CSV to Variables
					A = row["SCATSA"]
					B = row["SCATSB"]
					DIST = row["DIST"]
					if A == scat and B == routes[i]:
						print(A, B, DIST)
						routeCost.append((A,B,DIST))
						foundDist = True
					elif A == routes[i] and B == scat:
						print(B, A, DIST)
						routeCost.append((B,A,DIST))
						foundDist = True
		routeCosts.append(routeCost)
	return routeCosts

if __name__ == "__main__":
	allRoutes = (findRoute(970, 4264))
	for x in range(len(allRoutes)):
		print("Route ", x+1,  ": ")
		for y in range(len(allRoutes[x])):
			print("path : ", allRoutes[x][y][0], " to ", allRoutes[x][y][1], " will cost ", allRoutes[x][y][2])
			