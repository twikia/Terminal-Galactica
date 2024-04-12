import random
import time
import os
import threading
import keyboard
import datetime
import sys

def update_terminal(x, y, text):
    """
    Updates the terminal output at a specific (x, y) position with the provided text.
    This function uses ANSI escape codes to move the cursor and clear the line before printing.
    
    Parameters:
    - x: The column position (1-based).
    - y: The row position (1-based).
    - text: The text to print at the specified position.
    """
    # Move the cursor to the specified position
    print(f"\033[{y};{x}H", end="")
    # Clear the line from the cursor position to the end of the line
    print("\033[K", end="")
    # Print the new text
    print(text, end="")
    # Flush the output to ensure it appears immediately
    sys.stdout.flush()



board = []
gCol = 1
isRunning = True
score = 0


# Function to clear the screen
def clear_screen():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

# Function to generate the game board
def generate_board():
    global board
    board = []
    
    for i in range(12):
        row = ["|"]
        for j in range(15):
            row.append(' ')
        row.append("|")
        board.append(row)
    

# Function to display the game board
def display_board():
    global board, score

    boardStr = "                       Score: " + str(score) + "\n"

    for row in board:
        boardStr += "             " + ' '.join(row) + "\n"

    return boardStr

    
#handle highscores
def update_and_display_highscores(new_score):
    highscores_file = 'highscores'
    today = datetime.date.today()
    
    # Read the existing high scores
    try:
        with open(highscores_file, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        lines = []
    
    # Append the new score and date
    lines.append(f"{new_score} - {today}\n")
    
    # Sort the scores in descending order (assuming higher scores are better)
    lines.sort(key=lambda line: int(line.split(' - ')[0]), reverse=True)
    
    # Write the updated scores back to the file
    with open(highscores_file, 'w') as file:
        file.writelines(lines)
    
    # Display the top 10 scores
    print("Top 10 Scores:")
    for line in lines[:10]:
        print(line.strip())


def moveChar():
    global board
    global isRunning, gCol
    row = 11
    col = 1

    left = ["a", "left"]
    right = ["d","right"]
    

    while isRunning:
        
        event = keyboard.read_event()

        if event.event_type == keyboard.KEY_DOWN:

            board[row][col] = " "
            
            # Move left, ensuring we don't go out of bounds
            if event.name in left and col > 1:                
                col -= 1  # Move left
                gCol -= 1
            
            # Move right, ensuring we don't go out of bounds
            if event.name in right and col < 15:
                col += 1  # Move right
                gCol += 1
            
            board[row][col] = "H"

            time.sleep(.01)
        
        time.sleep(.04)

            
def shoot():
    global isRunning, gCol, board
    shoot = ["w","up","space"]

    while isRunning:
         
        event = keyboard.read_event()

        if event.event_type == keyboard.KEY_DOWN:
            
            if event.name in shoot:
                board[10][gCol] = "*"
                tBull = threading.Thread(target=bullet, args=())
                tBull.start()
                time.sleep(.1)
                
        time.sleep(.03)

def bullet():
    global gCol
    col = gCol
    row = 10

    time.sleep(.05)
    board[row][col] = "!"
    stored = "!"

    time.sleep(.02)
    board[row][col] = " "
    row -= 1

    
    while row >= 0 and isRunning:

        # stop the bullet if we hit anything
        if stored != "!":
            break

        board[row][col] = stored

        time.sleep(.1)

        stored = board[row][col]
        board[row][col] = ' '
        row -= 1


def spawnEnemies():
    global isRunning

    delayBetweenSpawns = 2
    delayForMovingEnemeies = .01

    while isRunning:
        randomCol = random.randint(1,14)

        enemyT = threading.Thread(target=enemy, args=(randomCol,delayForMovingEnemeies,))
        enemyT.start()

        time.sleep(delayBetweenSpawns)

        if delayBetweenSpawns > .8:
            delayBetweenSpawns -= .05
        if delayForMovingEnemeies > .006:
            delayForMovingEnemeies -= .0002
    

def enemy(col, runDelay):
    global isRunning, board, score, gCol

    row = 0
    enemyAlive = True

    time.sleep(.25)
    while isRunning and enemyAlive:

        board[row][col] = "@"

        #check if collides
        for i in range(100):
            if board[row][col] == "!":
                enemyAlive = False
                score += 1
                break
            time.sleep(runDelay)


        board[row][col] = ' '
        row += 1

        if row < 12:
            if board[row][col] == "!" and enemyAlive:
                    enemyAlive = False
                    score += 1
                    break

        if row >= 12:
            isRunning = False

            time.sleep(.3)

            update_and_display_highscores(score)

            print("\nGAME OVER!!")
            print("\nscore was: ", score, "\n\n")
            print("Presse any key to play again...\nesc to leave...")

            time.sleep(1.5)
            event = keyboard.read_event()
            if event.name != "esc":
                
                time.sleep(.05)
                isRunning = True
                gCol = 1
                score = 0
                play_game()

            else:
                print("Leave")            
            
            return 
        

        if board[row][col] == "!" and enemyAlive:
                enemyAlive = False
                score += 1
                break
    
    if not enemyAlive:
        board[row][col] = "*"
        time.sleep(.3)
        board[row][col] = " "


    

def displayScreen():
    global isRunning

    while isRunning:
        # clear_screen()
        # print(, end="")
        update_terminal(1,1,display_board())
        
        time.sleep(.015)


# Main game loop
def play_game():

    time.sleep(.3)

    clear_screen()
    generate_board()
    clear_screen()

    global board, isRunning, score, gCol

    board[11][1] = 'H'

    time.sleep(.2)

    moveThread = threading.Thread(target=moveChar, args=())
    moveThread.start()

    shootThread = threading.Thread(target=shoot, args=())
    shootThread.start()

    resfreshThread = threading.Thread(target=displayScreen, args=())
    resfreshThread.start()

    spawnEnemiesThread = threading.Thread(target=spawnEnemies, args=())
    spawnEnemiesThread.start()

    #Handle distributing keys and listing for values
    while isRunning:
        
        event = keyboard.read_event()

        #exit the game
        if event.name == "esc":
            
            
            isRunning = False
            time.sleep(.2)
            print("Exiting...")
            # print("Presse any key to play again...\nesc to leave...")
            
            break  # Exit the loop if the ESC key is pressed

        time.sleep(.03)

    moveThread.join()
    shootThread.join()
    resfreshThread.join()
    spawnEnemiesThread.join()
    
    

        
    

if __name__ == "__main__":
    play_game()


