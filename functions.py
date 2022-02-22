import csv
import random
import os


def unload_csv(csv_name, header):
    with open(csv_name, newline='') as f:
        array = []
        fi = csv.DictReader(f)
        for row in fi:
            array.append(row[header])
    return array


def psudoRanChoice(array, counter):
    img = random.choice(array)
    if len(counter) == len(array):
        counter = set()
    while img in counter:
        img = random.choice(array)
    counter.add(img)
    return img, counter


def stratChoice(name, strat, counter):
    i = random.randrange(len(name))
    if len(counter) == len(name):
        counter = set()
    while i in counter:
        i = random.randrange(len(name))
    counter.add(i)
    roll = name[i] + '\n' + strat[i]
    return roll, counter


def embedStratChoice(name, strat, counter):
    i = random.randrange(len(name))
    if len(counter) == len(name):
        counter = set()
    while i in counter:
        i = random.randrange(len(name))
    counter.add(i)
    nameRoll = name[i]
    stratRoll = strat[i]
    return nameRoll, stratRoll, counter


def incrTxt(file_name):
    with open(file_name, 'r') as f:
        count = str(int(f.read()) + 1)
    with open(file_name, 'w') as f:
        f.write(count)
