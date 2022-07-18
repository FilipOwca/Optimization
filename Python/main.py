import math
from Building import Building
from CreateWalls import CreateWalls
from Grid import Grid
from Visualisation import Visualisation
from Wall import Wall
from Vertical_Load import Load
from pymoo.optimize import minimize
from pymoo.core.problem import ElementwiseProblem
import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.factory import get_sampling, get_crossover, get_mutation

# Input data for the program: building's dimensions, thickness of walls and floor, loads, material parameters.
# *Given in SI Units*
width = 15
length = 20
hFloor = 4
heightOfBuilding = 40
floorNr = heightOfBuilding / hFloor
tFloor = 0.3
tWall = 0.3
columnCs = 0.09
columnNr = 10
gLoad = 2500
qLoad = 3000
youngModulus = 33000000000
youngModulusDesign = youngModulus / 1.2
shearModulusDesign = youngModulusDesign / 2.4
num_ver_axes = 5
num_hor_axes = 4
num_wall_hor_axis = num_ver_axes - 1
num_wall_ver_axis = num_hor_axes - 1


# Diagonal of the building's plan
d = math.sqrt(width * width + length * length)

# New instance of class Building
building = Building()

# Creating the list of points (axes' intersections) based on given number of axes
grid = Grid(num_ver_axes, num_hor_axes)
listOfPoints = grid.SetGrid(length, width)

maxNumberOfWalls = (num_hor_axes - 1) * num_ver_axes + (num_ver_axes - 1) * num_hor_axes
# solution = [1] * maxNumberOfWalls
# solution = np.random.rand(maxNumberOfWalls)
# print(solution)

# Set of walls ( 0 = no wall, 1 = wall)
# solution[2] = 1
# # solution[3] = 1
# solution[4] = 1
# # solution[21] = 1
# solution[26] = 1
# solution[27] = 1
# solution[100] = 0
# solution[101] = 0
# solution[102] = 0


# Creation of walls
# wallCreator = CreateWalls()
# walls = wallCreator.ConstructWalls(num_ver_axes, num_hor_axes, listOfPoints, solution)

# for wall in walls:
#     print("Wall coordinates: START({},{}) END({},{})".format(wall.StartEndCord()[0], wall.StartEndCord()[1], wall.StartEndCord()[2], wall.StartEndCord()[3]))
#
# # Finding the coordinates of the shear centre of the bracing system (walls)
# shearCoordinates = building.ShearCentre(walls)
#
# # Distance between geometrical center and shear center of the building
# c = math.sqrt((length / 2 - shearCoordinates[0]) * (length / 2 - shearCoordinates[0]) +
#           (width / 2 - shearCoordinates[1]) * (width / 2 - shearCoordinates[1]))
#
# # Physical parameters related to the bracing system (layout of walls)
# sumTorsionalMoment = building.SumTorsionalMoment(walls)
# warpingAreaMoment = building.WarpingAreaMoment(walls)
#
# # Global buckling loads for pure bending about Y (horizontal) and Z (vertical) axes
# FvBBy = 7.8 * floorNr / (floorNr + 1.6) * 0.4 * \
#          (youngModulusDesign * building.SumInertialMomentY(walls)) / (heightOfBuilding * heightOfBuilding)
# FvBBz = 7.8 * floorNr / (floorNr + 1.6) * 0.4 * \
#          (youngModulusDesign * building.SumInertialMomentZ(walls)) / (heightOfBuilding * heightOfBuilding)
#
# # Global buckling load for pure shear about Y(horizontal) and Z (vertical) axes
# FvBSy = shearModulusDesign * building.SumShearAreaY(walls)
# FvBSz = shearModulusDesign * building.SumShearAreaZ(walls)
#
# # Total characteristic vertical load acting on the building
# Load = Load(width, length, tFloor, gLoad, qLoad, walls, hFloor, tWall, columnCs, columnNr, floorNr)
# verticalLoad = Load.GetVerticalLoad()
#
# # Global buckling load taking into account bending and shear
# FVBy = FvBBy / (1 + FvBBy / FvBSy)
# FVBz = FvBBz / (1 + FvBBz / FvBSz)

# # Left and right-hand side of rotational stability formula
# RotationL = 1 / heightOfBuilding * math.sqrt((youngModulusDesign * warpingAreaMoment / 1e6) /
#                                          (verticalLoad * ((d * d / 12) + c * c))) + 1 / 2.28 * \
#              math.sqrt(shearModulusDesign * sumTorsionalMoment / (verticalLoad * ((d * d / 12) + c * c)))
RotationLimit = 1 / math.sqrt(0.31 * floorNr / (floorNr + 1.6))

def TranslationY(solution):
    from Vertical_Load import Load
    wallCreator = CreateWalls()
    walls = wallCreator.ConstructWalls(num_ver_axes, num_hor_axes, listOfPoints, solution)
    FvBBy = 7.8 * floorNr / (floorNr + 1.6) * 0.4 * \
            (youngModulusDesign * building.SumInertialMomentY(walls)) / (heightOfBuilding * heightOfBuilding)
    FvBSy = shearModulusDesign * building.SumShearAreaY(walls)
    FVBy = FvBBy / (1 + FvBBy / FvBSy)
    value = 0.1 * FVBy / 1e6
    Load = Load(width, length, tFloor, gLoad, qLoad, walls, hFloor, tWall, columnCs, columnNr, floorNr)
    verticalLoad = Load.GetVerticalLoad()
    result = [value, verticalLoad]
    return result

def TranslationZ(solution):
    from Vertical_Load import Load
    wallCreator = CreateWalls()
    walls = wallCreator.ConstructWalls(num_ver_axes, num_hor_axes, listOfPoints, solution)
    FvBBz = 7.8 * floorNr / (floorNr + 1.6) * 0.4 * \
            (youngModulusDesign * building.SumInertialMomentZ(walls)) / (heightOfBuilding * heightOfBuilding)
    FvBSz = shearModulusDesign * building.SumShearAreaZ(walls)
    FVBz = FvBBz / (1 + FvBBz / FvBSz)
    value = 0.1 * FVBz / 1e6
    Load = Load(width, length, tFloor, gLoad, qLoad, walls, hFloor, tWall, columnCs, columnNr, floorNr)
    verticalLoad = Load.GetVerticalLoad()
    result = [value, verticalLoad]
    return result

def Rotation(solution):
    from Vertical_Load import Load
    wallCreator = CreateWalls()
    walls = wallCreator.ConstructWalls(num_ver_axes, num_hor_axes, listOfPoints, solution)
    shearCoordinates = building.ShearCentre(walls)
    Load = Load(width, length, tFloor, gLoad, qLoad, walls, hFloor, tWall, columnCs, columnNr, floorNr)
    verticalLoad = Load.GetVerticalLoad()
    c = math.sqrt((length / 2 - shearCoordinates[0]) * (length / 2 - shearCoordinates[0]) +
                  (width / 2 - shearCoordinates[1]) * (width / 2 - shearCoordinates[1]))
    sumTorsionalMoment = building.SumTorsionalMoment(walls)
    warpingAreaMoment = building.WarpingAreaMoment(walls)
    RotationL = 1 / heightOfBuilding * math.sqrt((youngModulusDesign * warpingAreaMoment / 1e6) /
                                                 (verticalLoad * ((d * d / 12) + c * c))) + 1 / 2.28 * \
                math.sqrt(shearModulusDesign * sumTorsionalMoment / (verticalLoad * ((d * d / 12) + c * c)))
    return RotationL

class MyProblem(ElementwiseProblem):

    def __init__(self):
        super().__init__(n_var=maxNumberOfWalls,
                         n_obj=3,
                         n_constr=3,
                         xl=np.zeros(maxNumberOfWalls),
                         xu=np.ones(maxNumberOfWalls))

    def _evaluate(self, solution, out, *args, **kwargs):

        f1 = TranslationY(solution)[0]
        f2 = TranslationZ(solution)[0]
        f3 = Rotation(solution)

        g1 = TranslationY(solution)[1] /1e6 - TranslationY(solution)[0]
        g2 = TranslationZ(solution)[1] /1e6 - TranslationZ(solution)[0]
        g3 = RotationLimit - Rotation(solution)

        out['F'] = [f1, f2, f3]
        out['G'] = [g1, g2, g3]

problem = MyProblem()

algorithm = NSGA2(pop_size=100)


stop_criteria = ('n_gen',50)

results = minimize(problem=problem, algorithm=algorithm, termination=stop_criteria)

solution = np.rint(results.X[0])
# Validation of the translation and rotation conditions
print("Translation in Z Direction: ", TranslationY(solution)[1] / 1e6, " <= ", TranslationY(solution)[0]) # 14.67 = verticalLoad / 1e6
print("Translation in Y Direction: ", TranslationZ(solution)[1] / 1e6, " <= ", TranslationZ(solution)[0])
print("Rotation: ", Rotation(solution), " >= ", RotationLimit)


print(results.F)
print(results.G)

f = open("data.txt", "w")

visualisation = Visualisation()
for i in range(np.array(results.X).shape[0]):
    vis = visualisation.ToTable(num_hor_axes, num_ver_axes, results.X[i])
    f.write(str(vis))
    f.write("\n")
    f.write("\n")
f.close()
# wallCreator = CreateWalls()
# walls = wallCreator.ConstructWalls(num_ver_axes, num_hor_axes, listOfPoints, testResult)
# for wall in walls:
#     print("Wall coordinates: START({},{}) END({},{})".format(wall.StartEndCord()[0], wall.StartEndCord()[1], wall.StartEndCord()[2], wall.StartEndCord()[3]))

