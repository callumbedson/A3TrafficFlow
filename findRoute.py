import pandas as pd

# Python3 program to print all paths of source to destination in given graph
# from https://www.geeksforgeeks.org/print-paths-given-source-destination-using-bfs/
# credit to sanjeev2552
from typing import List
from collections import deque
 
#Modified function to convert path to list, which is added to possible routes
def convertPath(path: List[int]) -> None:
    
    pathList = []
    size = len(path)
    for i in range(size):
        pathList.append(path[i])
         
    return(pathList)
 

def isNotVisited(x: int, path: List[int]) -> int:
 
    size = len(path)
    
    for i in range(size):
        if (path[i] == x):
            return 0
             
    return 1
 
# Utility function for finding paths in graph
# from source to destination
def findpaths(g: List[List[int]], src: int,
              dst: int, v: int) -> None:
                   
    # Create a queue which stores the paths
    queue = deque()

	#Create a list that stores the routes
    allRoutes = []
 
    # Path vector to store the current path
    path = []
    path.append(src)
    queue.append(path.copy())
     
    x = 0
    while queue:
        path = queue.popleft()
        last = path[len(path) - 1]
 
        # Add path if last node is the destination 
        if (last == dst):
            allRoutes.append(convertPath(path))
            x += 1
        if x == 15:
            break
        # Check all current nodes, and add new to the queue
        for i in range(len(g[last])):
            if (isNotVisited(g[last][i], path)):
                newpath = path.copy()
                newpath.append(g[last][i])
                queue.append(newpath)
    return allRoutes

#deprecated DFS
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

#search w heuristic
def urch(source, dest):
	print("urchin lad")
	#Read csv with pandas
	df = pd.read_csv("SCATSGraph.csv")
	
	#Initialize node variables
	routes = [[0, source]]
	validRoutes = []
	nodeCosts = []

	while routes:
		currentRoute = routes.pop(0)
		print(currentRoute)
		for index,row in df.iterrows():
			#Assign columns a and b for ease
			A = row["SCATSA"]
			B = row["SCATSB"]
			DIST = row["DIST"]
			if currentRoute[-1] == A and B not in currentRoute:
				print(A, B)
				newRoute = currentRoute.copy()
				newRoute.append(B)
				newRoute[0] = newRoute[0] + DIST			
				if B == dest:
					validRoutes.append(newRoute)
					print("WE GOT ONE!!")
				else:
					newNode = True
					for node in nodeCosts:
						if node[0] == B:
							if newRoute[0] < node[1]:
								node[1] == newRoute[0]
								routes.append(newRoute)
								newNode = False
					if newNode == True:
						nodeCosts.append((B, newRoute[0]))
						routes.append(newRoute)
			elif currentRoute[-1] == B and A not in currentRoute:
				print(B, A)
				newRoute = currentRoute.copy()
				newRoute.append(A)
				newRoute[0] = newRoute[0] + DIST
				if B == dest:
					validRoutes.append(newRoute)
					print("WE GOT ONE!!")
				else:
					newNode = True
					for node in nodeCosts:
						if node[0] == B:
							if newRoute[0] < node[1]:
								node[1] == newRoute[0]
								routes.append(newRoute)
								newNode = False
					if newNode == True:
						nodeCosts.append((B, newRoute[0]))
						routes.append(newRoute)
		#Sort all routes using a lambda to access their cost 
		routes = sorted(routes,key=lambda x:x[0]) 
		#print(routes)
	print(validRoutes)
	return(validRoutes)


#Attaches distance to each path (between 2 SCATS) along a route
def attachDist(allRoutes):
	df = pd.read_csv("SCATSGraph.csv")
	#routeCosts is allRoutes with distances attached (tuple for each path)
	routeCosts = []
	for routes in allRoutes:
		#i is to get next value in the path
		i = 0
		#routecost is an individual route with tuple inc distance
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
						routeCost.append((A,B,DIST))
						foundDist = True
					elif A == routes[i] and B == scat:
						routeCost.append((B,A,DIST))
						foundDist = True
		routeCosts.append(routeCost)
	return routeCosts

#Creates graph array from scats csv
def createGraph(v):
	g = [[] for _ in range(v)]
	df = pd.read_csv("SCATSGraph.csv")
	for index,row in df.iterrows():
		A = int(row["SCATSA"])
		B = int(row["SCATSB"])
		g[A].append(B)
		g[B].append(A)
	return g

def main(src, dst):
	v = 4350
	g = createGraph(v)

    # Function for finding the paths
	return attachDist(findpaths(g, int(src), int(dst), v))

#	allRoutes = (findRoute(970, 4264))
#	for x in range(len(allRoutes)):
#		print("Route ", x+1,  ": ")
#		for y in range(len(allRoutes[x])):
#			print("path : ", allRoutes[x][y][0], " to ", allRoutes[x][y][1], " will cost ", allRoutes[x][y][2])
			