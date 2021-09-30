from PIL import Image
import pygame
import random
import numpy as np
import copy


TARGET_IMAGE_FILENAME = 'samp1.png'
POPULATION = 100
MUTATION_RATE = 1 / 100
CROSSOVER = True
NUMBER_OF_ELITES = 1


pygame.init()
display_width = 800
display_height = 500
gamedisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Picture Evolution')

class Picture:
    def __init__(self, image):
        self.imagedataarray = np.array(image)
        self.fitness = 0

    def picFitness(self, samppixs):
        self.fitness = 0
        evpixs = self.imagedataarray
        for evrow, samprow in zip(evpixs, samppixs):
            for evpix, samppix in zip(evrow, samprow):
                self.fitness += abs(int(evpix[0]) - samppix[0])
                self.fitness += abs(int(evpix[1]) - samppix[1])
                self.fitness += abs(int(evpix[2]) - samppix[2])

    def mutate(self, mutrate):
        k = 0
        for row in self.imagedataarray:
            j = 0
            for pix in row:
                if random.random() < mutrate:
                    self.imagedataarray[k][j] = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
                j += 1
            k += 1

sampimg = Image.open(TARGET_IMAGE_FILENAME)
sampdata = np.array(sampimg)

def evaluateFitness(pictures):
    for pic in pictures:
        pic.picFitness(sampdata)

def crossover(arr0, arr1, genomelength):
    crosspoint = random.randrange(genomelength - 2) + 1
    crossrow = int(crosspoint / len(arr0[0]))
    crosscol = crosspoint % len(arr0[0])
    crossedpic = Picture(np.empty((len(arr0), len(arr0[0]))))
    activearr = None
    inactivearr = None
    if random.randrange(2) == 0:
        activearr = arr0
        inactivearr = arr1
    else:
        activearr = arr1
        inactivearr = arr0
    crossedpic.imagedataarray = copy.deepcopy(activearr)

    
    switch = activearr
    activearr = inactivearr
    inactivearr = switch  
    for k in range(crosscol, len(activearr[0])):
        crossedpic.imagedataarray[crossrow][k] = activearr[crossrow][k]
    for k in range(crossrow + 1, len(activearr)):
        crossedpic.imagedataarray[k] = activearr[k]
    return crossedpic

def createRandPic():
    imgwidth, imgheight = sampimg.size
    randarray = np.random.randint(0, 255, (imgheight, imgwidth, 3))
    randarray = np.array(randarray, dtype=np.uint8)
    randimage = Image.fromarray(randarray)
    randimage.save("evimg.png")
    return randimage

def picSort(pic):
    return pic.fitness

clock = pygame.time.Clock()
crashed = False
gamesampim = pygame.image.load(TARGET_IMAGE_FILENAME)
gamesampim = pygame.transform.scale(gamesampim, (200, 200))

label = pygame.font.SysFont('calibri', 23)

genomelength = len(sampdata) * len(sampdata[0])

#generate initial population
evimgs = []
for k in range(POPULATION):
    evimgs.append(Picture(createRandPic()))

gens = 0
#pygame loop
while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
    
    gameevim = pygame.image.load('evimg.png')
    gameevim = pygame.transform.scale(gameevim, (200, 200))

    gamedisplay.fill((255, 255, 255))

    gamedisplay.blit(gameevim, (display_width * .15, display_height * .25))
    gamedisplay.blit(gamesampim, (display_width * .6, display_height * .25))

    #truncation algorithm
    evaluateFitness(evimgs)
    evimgs.sort(key=picSort)

    gentext = label.render('Generation: ' + str(gens), True, 'black')
    gamedisplay.blit(gentext, (display_width * .15, display_height * .7))
    fittext = label.render('Variation from target: ' + str(evimgs[0].fitness), True, 'black')
    gamedisplay.blit(fittext, (display_width * .15, display_height * .78))
    infotext = label.render('Population: ' + str(len(evimgs)) + '      Mutation rate: ' + str(round(MUTATION_RATE, 5)) + '     Crossover: ' + str(CROSSOVER) + '      Elites: ' + str(NUMBER_OF_ELITES), True, 'black')
    gamedisplay.blit(infotext, (display_width * .10, display_height * .1))

    array = np.array(evimgs[0].imagedataarray, dtype=np.uint8)
    new_image = Image.fromarray(array)
    new_image.save('evimg.png')
    newevimgs = []
    evimgs = evimgs[:len(evimgs) - int(POPULATION / 2)]
    for k in range(NUMBER_OF_ELITES):
        newevimgs.append(evimgs[k])

    for k in range(POPULATION - NUMBER_OF_ELITES):
        if CROSSOVER:
            pics = random.sample(evimgs, 2)
            img = crossover(pics[0].imagedataarray, pics[1].imagedataarray, genomelength)
        else:
            img = copy.deepcopy(evimgs[int(k / 2)])
        img.mutate(MUTATION_RATE)
        newevimgs.append(img)
    evimgs = newevimgs
    gens += 1

    
    pygame.display.update()

pygame.quit()
quit()

