from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt


def generateInstance(width: int, height: int, numAgents: int, obstaclePercentage: float, T: int, mode: str = "random", seed: int = 42) -> str:
    random.seed(seed)

    totalCells = width * height
    allCells = [(x, y) for x in range(1, width + 1) for y in range(1, height + 1)]

    if mode == "warehouse":
        freeCells = {(x, y) for (x, y) in allCells if x <= 2 or x >= (width - 1)}

        for h in range(1, height + 1):
            if (h + 1) % 3 == 0:
                freeCells.update((x, h) for x in range(1, width + 1))

        for w in range(1, width + 1)[2:-2]:
            if (w - 2) % 6 == 0:
                freeCells.update((w, y) for y in range(1, height + 1))

        obstacles = set(allCells) - freeCells

        # starts left, goals right
        startFree = [(x, y) for (x, y) in freeCells if x <= 2]
        goalFree = [(x, y) for (x, y) in freeCells if x >= (width - 1)]
        if len(startFree) < numAgents or len(goalFree) < numAgents:
            raise ValueError("Not enough free cells for agents")
        startPositions = random.sample(startFree, numAgents)
        goalPositions = random.sample(goalFree, numAgents)
        # plot_grid(width, height, obstacles)
    else:
        numObstacles = int(round(totalCells * (float(obstaclePercentage) / 100.0)))
        obstacles = set(random.sample(allCells, numObstacles)) if numObstacles > 0 else set()
        freeCells = [cell for cell in allCells if cell not in obstacles]
        if len(freeCells) < 2 * numAgents:
            raise ValueError("Not enough free cells for starts and goals")
        selectedCells = random.sample(freeCells, 2 * numAgents)
        startPositions = selectedCells[:numAgents]
        goalPositions = selectedCells[numAgents:]

    plot_grid(width, height, obstacles, startPositions, goalPositions)

    lines = [
        f"agent(1..{numAgents}).",
        f"rangeX(1..{width}).",
        f"rangeY(1..{height}).",
        f"time(1..{T}).",
        "",
        *([f"obstacle({x}, {y})." for x, y in sorted(obstacles)] if obstacles else []),
        "",
        *[f"at({i}, {x}, {y}, 0)." for i, (x, y) in enumerate(startPositions, start=1)],
        "",
        *[f"goal({i}, {x}, {y})." for i, (x, y) in enumerate(goalPositions, start=1)]
    ]

    return "\n".join(lines)


def writeInstance(instance: str, outputFile: str) -> None:
    with open(outputFile, "w") as f:
        f.write(instance)
    print(outputFile)


def plot_grid(sizeX, sizeY, obstacles, startPositions=None, goalPositions=None):
    fig, ax = plt.subplots(figsize=(5, 5))
    for x in range(1, sizeX + 1):
        for y in range(1, sizeY + 1):
            face = 'black' if (x, y) in obstacles else 'white'
            ax.add_patch(plt.Rectangle((x, y), 1, 1,
                                       edgecolor='gray',
                                       facecolor=face))
    ax.set_xlim(1, sizeX + 1)
    ax.set_ylim(1, sizeY + 1)
    ax.set_aspect('equal')
    ax.axis('off')

    if not startPositions or not goalPositions:
        plt.show()
        return

    numAgents = len(startPositions)
    cmap = plt.colormaps['tab20'].resampled(numAgents)
    colors = [cmap(i) for i in range(numAgents)]

    markerSize = (14, 20) if sizeX < 10 else (7, 10)

    for i, (s, g) in enumerate(zip(startPositions, goalPositions)):
        sx, sy = s
        gx, gy = g
        c = colors[i]

        ax.plot(
            sx + 0.5, sy + 0.5,
            marker='o', markersize=markerSize[0],
            markeredgecolor='k',
            markerfacecolor=c
        )

        ax.plot(
            gx + 0.5, gy + 0.5,
            marker='*', markersize=markerSize[1],
            markeredgecolor='k',
            markerfacecolor=c
        )

    plt.show()


if __name__ == "__main__":
    # Based on:
    # Gómez, R. N., Hernández, C., & Baier, J. A. (2020). Solving Sum-of-Costs Multi-Agent Pathfinding with Answer-Set Programming. Proceedings of the AAAI Conference on Artificial Intelligence, 34(06), 9867-9874.
    # https://doi.org/10.1609/aaai.v34i06.6540

    parentOutputDir = "mapf_instances"
    os.makedirs(parentOutputDir, exist_ok=True)

    obstaclePercentages = [0, 10, 25]
    instCount = 0

    # random 8×8
    width, height = 8, 8
    T = 100
    mode = "random"

    agents = list(range(10, 21, 2))
    for numAgents in agents:
        for obstaclePercentage in obstaclePercentages:
            for i in range(3):
                instanceStr = generateInstance(width, height, numAgents, obstaclePercentage, T, mode, instCount)
                writeInstance(instanceStr, os.path.join(parentOutputDir, f"{instCount:03}_random_{width}x{height}_a{numAgents}_p{obstaclePercentage}_{i}.lp"))
                instCount += 1

    # random 20×20
    width, height = 20, 20
    T = 120
    mode = "random"

    agents = list(range(16, 29, 2))
    for numAgents in agents:
        for obstaclePercentage in obstaclePercentages:
            for i in range(3):
                instanceStr = generateInstance(width, height, numAgents, obstaclePercentage, T, mode, instCount)
                writeInstance(instanceStr, os.path.join(parentOutputDir, f"{instCount:03}_random_{width}x{height}_a{numAgents}_p{obstaclePercentage}_{i}.lp"))
                instCount += 1

    # warehouse
    T = 120
    mode = "warehouse"

    for width, height in [(15, 15), (21, 18)]:
        for numAgents in list(range(16, 29, 2)):
            for i in range(3):
                instanceStr = generateInstance(width, height, numAgents, obstaclePercentage, T, mode, instCount)
                writeInstance(instanceStr, os.path.join(parentOutputDir, f"{instCount:03}_warehouse_{width}x{height}_a{numAgents}_{i}.lp"))
                instCount += 1
