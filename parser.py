from openpyxl import load_workbook, Workbook
import math

newWorkbook = Workbook()
workbook = load_workbook(filename="C:/Users/bedsoc/Downloads/Scats Data October 2006.xlsx", data_only=True)

sheet = workbook["Data"]
newSheet = newWorkbook.active
scatsList = []

for x in range(3,sheet.max_row):
        roads = sheet["B"+str(x)].value.lower().split(" of ")
        roads[0] = roads[0][:-2].strip()
        #print(roads)

        new = True 
        for scatsNum in scatsList:
            if sheet["A"+str(x)].value == scatsNum[0]:
                new = False
                #print(scatsNum[0], scatsNum[1], roads)
                for road in roads:
                    if road not in scatsNum[1]:
                        scatsNum[1].append(road)
                        #print("New road added")
        if new:
            scatsList.append((sheet["A"+str(x)].value, roads ,sheet["D"+str(x)].value,sheet["E"+str(x)].value))
            #print("New scats added")
#print (scatsList)

for scatsX in scatsList:
    for scatsY in scatsList:
        if scatsX == scatsY:
            continue
        for roadX in scatsX[1]:
            for roadY in scatsY[1]:
                #print(roadX, roadY)
                if roadX == roadY:
                    dist = math.sqrt((scatsX[2] - scatsY[2])**2 + (scatsX[3] - scatsY[3])**2)
                    row = newSheet.max_row + 1
                    newSheet["A" + str(row)] = scatsX[0]
                    newSheet["B" + str(row)] = scatsY[0]
                    newSheet["C" + str(row)] = dist
    scatsList.remove(scatsX)

    
newWorkbook.save("C:/Users/bedsoc/Desktop/SCATSGraph.xlsx")
 