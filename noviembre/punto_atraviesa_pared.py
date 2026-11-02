import matplotlib.pyplot as plt
from math import cos,sin,pi,sqrt
from random import uniform

puntosa=[]
for i in range(11):
    puntosa.append((i, 0))
    puntosa.append((i, -1))
    puntosa.append((i, +1))
#print(puntosa)

#giro

puntosb=[]
for i in range(11):
    coorda = (10,0)
    coordb = (cos(2*pi/3),sin(2*pi/3))
    coordb = tuple(x * i for x in coordb)
    coordc = (cos(2*pi/3+pi/2),sin(2*pi/3+pi/2))
    #
    scoorda = tuple(sum(x) for x in zip(coorda, coordb))
    scoordb = tuple(a + b for a, b in zip(scoorda, coordc))
    scoordc = tuple(a - b for a, b in zip(scoorda, coordc))
    #
    puntosb.append(scoorda)
    puntosb.append(scoordb)
    puntosb.append(scoordc)

#giro

puntosc=[]
for i in range(11):
    coorda = (5,8.66)
    coordb = (cos(4*pi/3),sin(4*pi/3))
    coordb = tuple(x * i for x in coordb)
    coordc = (cos(4*pi/3 + pi / 2), sin(4*pi/3 + pi / 2))
    #
    scoorda = tuple(sum(x) for x in zip(coorda, coordb))
    scoordb = tuple(a + b for a, b in zip(scoorda, coordc))
    scoordc = tuple(a - b for a, b in zip(scoorda, coordc))
    #
    puntosc.append(scoorda)
    puntosc.append(scoordb)
    puntosc.append(scoordc)

puntos = puntosa + puntosb + puntosc

# Separar coordenadas X e Y
x = [p[0] for p in puntos]
y = [p[1] for p in puntos]

a = uniform(0,12)
b = uniform(0,10)

puntoss=[(a,b)]
xa=[p[0] for p in puntoss]
ya=[p[1] for p in puntoss]

plt.scatter(x, y, color='red', s=50)  # s es el tamaño del punto
plt.scatter(xa,ya,color='blue', s=50)
plt.title('Gráfico de puntos sueltos')
plt.xlabel('Eje X')
plt.ylabel('Eje Y')
plt.grid(True)
plt.axis('equal')  # Iguala las escalas de los ejes X e Y


for i in range(len(puntos)):
    dx=puntos[i][0]-puntoss[0][0]
    dy=puntos[i][1]-puntoss[0][1]
    d = sqrt(dx**2+dy**2)
    #print(puntos[i],d)
    if d<1:
        print("punto choca con pared dura")
        break
    elif i==int(len(puntos))-1:
        print("punto atraviesa pared")

plt.show()