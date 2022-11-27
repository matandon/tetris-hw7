#################################################
# hw7.py: Tetris!
#
# Your name:
# Your andrew id:
#
# Your partner's name:
# Your partner's andrew id:
#################################################

import cs112_f19_week7_linter
import math, copy, random

from cmu_112_graphics import *
from tkinter import *
#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#################################################
# Functions for you to write
#################################################
def gameDimensions():
    rows, cols, cellSize, margin = 15, 10, 20, 25
    return (rows, cols, cellSize, margin)

def appStarted(app):
    app.rows, app.cols, app.cellSize, app.margin = gameDimensions()
    app.emptyColor = "blue"
    app.board = []
    for row in range(app.rows):
        fullRow = []
        for col in range(app.cols):
            fullRow += [app.emptyColor]
        app.board += [fullRow]
    # Seven "standard" pieces (tetrominoes)
    app.iPiece = [
        [  True,  True,  True,  True ]
    ]

    app.jPiece = [
        [  True, False, False ],
        [  True,  True,  True ]
    ]

    app.lPiece = [
        [ False, False,  True ],
        [  True,  True,  True ]
    ]

    app.oPiece = [
        [  True,  True ],
        [  True,  True ]
    ]

    app.sPiece = [
        [ False,  True,  True ],
        [  True,  True, False ]
    ]

    app.tPiece = [
        [ False,  True, False ],
        [  True,  True,  True ]
    ]

    app.zPiece = [
        [  True,  True, False ],
        [ False,  True,  True ]
    ]
    app.tetrisPieces = [app.iPiece, app.jPiece, app.lPiece, app.oPiece, 
                        app.sPiece, app.tPiece, app.zPiece]
    app.tetrisPieceColors = ["red", "yellow", "magenta", "pink", "cyan", 
                             "green", "orange"]
    newFallingPiece(app)
    app.isGameOver = False
    app.score = 0

def newFallingPiece(app):
    randomIndex = random.randint(0, len(app.tetrisPieces) - 1)
    app.fallingPiece = app.tetrisPieces[randomIndex]
    app.fallingPieceColor = app.tetrisPieceColors[randomIndex]
    app.fallingPieceRow = 0
    app.numFallingPieceCols = len(app.fallingPiece[0])
    app.fallingPieceCol = app.cols//2 - (app.numFallingPieceCols//2)

def drawBoard(app, canvas):
    for i in range(app.rows):
        for j in range(app.cols):
            drawCell(app, canvas, i, j, app.board[i][j])

def drawFallingPiece(app, canvas):
    for i in range(len(app.fallingPiece)):
        for j in range(len(app.fallingPiece[0])):
            if app.fallingPiece[i][j] == True:
                drawCell(app, canvas, i + app.fallingPieceRow, 
                         j + app.fallingPieceCol, app.fallingPieceColor)

def drawCell(app, canvas, row, col, color):
    x0, y0 = app.margin + app.cellSize*col, app.margin + app.cellSize*row
    x1, y1 = x0 + app.cellSize, y0 + app.cellSize
    canvas.create_rectangle(x0, y0, x1, y1, 
                            fill = color, width = 4)

def drawScore(app, canvas):
    canvas.create_text(app.width//2, app.margin//2, fill = "dark blue", 
                       text = f"Score: {app.score}", font = "Arial 12 bold")

def redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "orange")
    drawBoard(app, canvas)
    drawFallingPiece(app, canvas)
    drawScore(app, canvas)
    if app.isGameOver == True:
        canvas.create_rectangle(app.margin, 
                                app.margin + app.cellSize,
                                app.width - app.margin, 
                                app.margin + 3*app.cellSize,
                                fill = "black")
        canvas.create_text(app.width // 2, 
                            app.margin + app.cellSize*2, 
                            text = "Game Over! Press r to restart.",
                            fill = "yellow", font = "Arial 10 bold")
        
def moveFallingPiece(app, drow, dcol):
    app.fallingPieceRow += drow
    app.fallingPieceCol += dcol
    if not fallingPieceIsLegal(app):
        app.fallingPieceRow -= drow
        app.fallingPieceCol -= dcol
        return False
    return True

def rotateFallingPiece(app):
    oldRowDim = len(app.fallingPiece)
    oldColDim = len(app.fallingPiece[0])
    oldPiece = app.fallingPiece
    oldRow = app.fallingPieceRow
    oldCol = app.fallingPieceCol
    newRowDim = oldColDim
    newColDim = oldRowDim
    newPiece = [[None]*newColDim for i in range(newRowDim)]
    newRow = app.fallingPieceRow + oldRowDim // 2 - newRowDim // 2
    newCol = app.fallingPieceCol + oldColDim // 2 - newColDim // 2
    for i in range(oldRowDim):
        for j in range(oldColDim):
            newPiece[(oldColDim - 1) - j][i] = oldPiece[i][j]
    app.fallingPiece = newPiece
    app.fallingPieceRow = newRow
    app.fallingPieceCol = newCol
    if fallingPieceIsLegal(app) == False:
        app.fallingPiece = oldPiece
        app.fallingPieceRow = oldRow
        app.fallingPieceCol = oldCol
        
def removeFullRows(app):
    newBoard = []
    app.fullRows = 0
    for row in range(app.rows):
        if app.emptyColor in app.board[row]:
            newBoard += [app.board[row]]
        else:
            app.fullRows += 1
    for i in range(app.fullRows):
        fullRow = []
        for col in range(app.cols):
            fullRow += [app.emptyColor]
        newBoard = [fullRow] + newBoard
    app.board = copy.deepcopy(newBoard)
    app.score += app.fullRows**2

def placeFallingPiece(app):
    for i in range(len(app.fallingPiece)):
        for j in range(len(app.fallingPiece[0])):
            if app.fallingPiece[i][j] == True:
                row = app.fallingPieceRow + i
                col = app.fallingPieceCol + j
                app.board[row][col] = app.fallingPieceColor
    removeFullRows(app)

def fallingPieceIsLegal(app):
    for i in range(len(app.fallingPiece)):
        for j in range(len(app.fallingPiece[0])):
            if app.fallingPiece[i][j] == True:
                if ((app.fallingPieceRow + i < 0) or 
                   (app.fallingPieceRow + i >= app.rows) or
                   (app.fallingPieceCol + j < 0) or
                   (app.fallingPieceCol + j >= app.cols) or
                   (app.board[app.fallingPieceRow + i][app.fallingPieceCol + j]
                   != app.emptyColor)):
                   return False
    return True

def hardDrop(app):
    while True:
        validMove = moveFallingPiece(app, +1, 0)
        if validMove == False:
            placeFallingPiece(app)
            break

def keyPressed(app, event):
    if app.isGameOver == False:
        if event.key == "Left":
            moveFallingPiece(app, 0, -1)
        elif event.key == "Right":
            moveFallingPiece(app, 0, +1)
        elif event.key == "Down":
            moveFallingPiece(app, +1, 0)
        elif event.key == "Up":
            rotateFallingPiece(app)
        elif event.key == "Space":
            hardDrop(app)
    if event.key == "r":
        appStarted(app)

def timerFired(app):
    if app.isGameOver == False:
        moveValid = moveFallingPiece(app, +1, 0)
        if moveValid == False:
            placeFallingPiece(app)
            newFallingPiece(app)
            if fallingPieceIsLegal(app) == False:
                app.isGameOver = True
    
def playTetris():
    rows, cols, cellSize, margin = gameDimensions()
    width = margin*2 + cols*cellSize
    height = margin*2 + rows*cellSize
    runApp(width = width, height = height)

#################################################
# main
#################################################

def main():
    cs112_f19_week7_linter.lint()
    playTetris()

if __name__ == '__main__':
    main()
