import pygame, sys
from pygame.locals import *
import numpy as np

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 480

BOARD_WIDTH = 12
BOARD_HEIGHT = 22

PREVIEW_WIDTH = 8
PREVIEW_HEIGHT = 8

# Top Corner of the preview window
PREVIEW_X = 260
PREVIEW_Y = 10

XMARGIN = 10
YMARGIN = 10

# A threshold for how long you have to hold a key down to register a movement
HOLD_THRESHOLD = 200

# Move down quicker than left/right
DOWN_HOLD_THRESHOLD = 20

# Event ID for clock tick (for making pieces fall)
CLOCK_TICK = USEREVENT + 1

# Starting speed at which pieces fall
STARTING_SPEED = 1000

SQUARE_LENGTH = 20

# The position of the score text on the screen
SCORE_POSITION = (300, 200)

# The number of different piece configurations
NUM_PIECE_TYPES = 7

#          R    G    B
RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
BLUE   = (  0,   0, 255)
YELLOW = (255, 255,   0)
ORANGE = (255, 128,   0)
PURPLE = (255,   0, 255)
CYAN   = (  0, 255, 255)
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)


class Tetris:

  def __init__(self):
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # The state of the game to be drawn to the screen
    self.game_state = np.zeros((BOARD_WIDTH,BOARD_HEIGHT))

    # The blocks that are not being controlled
    self.game_block = np.zeros((BOARD_WIDTH,BOARD_HEIGHT))

    # The state of the piece that is currently being moved
    self.game_piece = np.zeros((BOARD_WIDTH,BOARD_HEIGHT))

    self._rects = []
    self._preview_rects = []

    self.font =pygame.font.Font(None,30)
    self.score = 0
    self.score_text = self.font.render("Score: "+str(self.score), 1,(255,255,255))
    DISPLAYSURF.blit(self.score_text, SCORE_POSITION)

    self.piece_types = []
    self.setup_piece_types()

    # Current rotation index
    self.rot = 0

    for i in range(BOARD_WIDTH):
      self._rects.append([])
      for j in range(BOARD_HEIGHT):
        r = pygame.Rect((XMARGIN + (i*SQUARE_LENGTH), 
                         YMARGIN + (j*SQUARE_LENGTH),
                         SQUARE_LENGTH,
                         SQUARE_LENGTH))
        self._rects[i].append(r)
    for i in range(PREVIEW_WIDTH):
      self._preview_rects.append([])
      for j in range(PREVIEW_HEIGHT):
        r = pygame.Rect((PREVIEW_X + (i*SQUARE_LENGTH), 
                         PREVIEW_Y + (j*SQUARE_LENGTH),
                         SQUARE_LENGTH,
                         SQUARE_LENGTH))
        self._preview_rects[i].append(r)
    
    while True:
      self.run_game()

  def run_game(self):

    # Reset game board
    self.reset()
    pygame.time.set_timer(CLOCK_TICK, STARTING_SPEED)
    self.play_speed = STARTING_SPEED
    self.playing = True
    i = int(np.random.random()*NUM_PIECE_TYPES)
    self.next_piece = i
    self.generate_new_piece()

    while self.playing:
      for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
          pygame.quit()
          sys.exit()
        elif event.type == KEYUP and event.key == K_BACKSPACE:
          return 0 # Start a new game
        elif event.type == CLOCK_TICK:
          # Move the piece down by one space
          self.move_piece_down()
        elif event.type == KEYDOWN and event.key == K_DOWN:
          # Drop the piece rapidly

          #TEMP testing rects
	        self.move_piece_down()
        elif event.type == KEYDOWN and event.key == K_RIGHT:
          self.move_piece_sideways(1)
        elif event.type == KEYDOWN and event.key == K_LEFT:
          self.move_piece_sideways(-1)
        elif event.type == KEYDOWN and event.key == K_UP:
          self.rotate_piece()
        elif event.type == KEYDOWN and event.key == K_RETURN:
          self.generate_new_piece()
        elif event.type == KEYDOWN and event.key == K_SPACE:
          self.connect_piece()
      keys = pygame.key.get_pressed()
      if keys[pygame.K_DOWN]:
        self.down_count += 1
        if self.down_count > DOWN_HOLD_THRESHOLD:
          self.move_piece_down()
          self.down_count = 0
      else:
        self.down_count = 0

      if keys[pygame.K_LEFT]:
        self.left_count += 1
        if self.left_count > HOLD_THRESHOLD:
          self.move_piece_sideways(-1)
          self.left_count = 0
      else:
        self.left_count = 0

      if keys[pygame.K_RIGHT]:
        self.right_count += 1
        if self.right_count > HOLD_THRESHOLD:
          self.move_piece_sideways(1)
          self.right_count = 0
      else:
        self.right_count = 0

      self.draw()

  def reset(self):
    for i in range(BOARD_WIDTH):
      for j in range(BOARD_HEIGHT):
        self.game_state[i,j] = 0
        self.game_block[i,j] = 0
        self.game_piece[i,j] = 0

    # Set up the walls around the border

    # Floor
    self.game_block[:,-1] = 8

    # Left and Right Walls
    self.game_block[-1,:] = 8
    self.game_block[0,:] = 8

    # Reset score
    self.score = 0
    self.score_text = self.font.render("Score: "+str(self.score), 1,(255,255,255))

  def draw(self):
    DISPLAYSURF.fill(BLACK)
    self.game_state = self.game_block + self.game_piece
    for i in range(BOARD_WIDTH):
      for j in range(BOARD_HEIGHT):
        if self.game_state[i,j] != 0:
          #pygame.draw.rect(DISPLAYSURF, get_colour(self.game_state[i,j]), self._rects[i][j], 4)
          pygame.draw.rect(DISPLAYSURF, get_colour(self.game_state[i,j]), self._rects[i][j], 0)
    for i in range(PREVIEW_WIDTH):
      for j in range(PREVIEW_HEIGHT):
        if self.preview_display[i,j] != 0:
          pygame.draw.rect(DISPLAYSURF, get_colour(self.preview_display[i,j]), self._preview_rects[i][j], 0)
    DISPLAYSURF.blit(self.score_text, SCORE_POSITION)
    pygame.display.update()

  def connect_piece(self):
    # Connect the piece as part of the 'background' can't be moved anymore
    self.game_block += self.game_piece
    # Check to see if something breaks
    check = reduce(lambda x,y: x*y, np.split(self.game_block[1:BOARD_WIDTH-1,1:BOARD_HEIGHT-1],BOARD_WIDTH-2))
    if np.sum(check) != 0:
      loc = np.where(check != 0)[1]
      score = len(loc)
      i = loc[-1]+1
      while i > 1:
        self.game_block[1:BOARD_WIDTH-1,i] = self.game_block[1:BOARD_WIDTH-1,max(i-score,0)]
	i -= 1
      self.score += score ** 2
      self.score_text = self.font.render("Score: "+str(self.score), 1,(255,255,255))
      # Increase the speed of pieces falling
      self.play_speed = max(self.play_speed * (.95 ** (score ** 2)), 100)
      pygame.time.set_timer(CLOCK_TICK, int(self.play_speed))

    # Check to see if the user lost the game
    if np.sum(self.game_block[1:BOARD_WIDTH-1,0]) != 0:
      self.playing = False

    self.generate_new_piece()

  def generate_new_piece(self):
    i = int(np.random.random()*NUM_PIECE_TYPES)
    self.game_piece = self.piece_types[self.next_piece].copy()
    self.next_piece = i
    self.preview_display = self.preview[i]

  def move_piece_down(self):
    # Attempts to move the piece down by one space
    # If it collides then it becomes part of the background and a new piece spawns
    attempt = np.roll(self.game_piece,1)
    if self.collision(attempt):
      self.connect_piece()
    else:
      self.game_piece = attempt

  def move_piece_sideways(self, d):
    # Attempts to move the piece sideways
    attempt = np.roll(self.game_piece,d,axis=0)
    if not self.collision(attempt):
      self.game_piece = attempt

  def rotate_piece(self):
    # Find the co-ordinates of the 'bounding box' of the piece
    x1 = 0
    y1 = 0
    while np.sum(self.game_piece[x1,:]) == 0:
      x1 += 1
    while np.sum(self.game_piece[:,y1]) == 0:
      y1 += 1
    x2 = BOARD_WIDTH - 1 
    y2 = BOARD_HEIGHT - 1
    while np.sum(self.game_piece[x2,:]) == 0:
      x2 -= 1
    while np.sum(self.game_piece[:,y2]) == 0:
      y2 -= 1
    # Find length and approximate midpoint
    xlen = x2 - x1
    ylen = y2 - y1
    xm = int((x2+x1)/2.0)
    ym = int((y2+y1)/2.0)
    # Find the distances around the center point
    xpre = x1 - xm
    xpost = x2 - xm
    ypre = y1 - ym
    ypost = y2 - ym
    attempt = np.zeros((BOARD_WIDTH,BOARD_HEIGHT))
    # Check bounds and do the rotation
    if xm+ypre >= 0 and xm+ypost+1 < BOARD_WIDTH and ym+xpre >= 0 and ym+xpost+1 < BOARD_HEIGHT:
      attempt[xm+ypre:xm+ypost+1,ym+xpre:ym+xpost+1] = np.rot90(self.game_piece[x1:x2+1,y1:y2+1])
      if not self.collision(attempt):
        self.game_piece = attempt

  def collision(self, piece):
    # Check to see if it hits other pieces, as well as hitting the floor or walls
    # The floor/wall check sees if the piece is looping around in the space
    return not((np.sum(self.game_block * piece) == 0) and 
               (np.sum(piece[:,0]*piece[:,-1]) == 0) and 
               (np.sum(piece[0,:]*piece[-1,:]) == 0))

  def setup_piece_types(self):

    line = np.zeros((BOARD_WIDTH,BOARD_HEIGHT))
    line[BOARD_WIDTH/2-2:BOARD_WIDTH/2+2,0] = 1

    square = np.zeros((BOARD_WIDTH,BOARD_HEIGHT))
    square[BOARD_WIDTH/2-1:BOARD_WIDTH/2+1,0:2] = 2

    L1 = np.zeros((BOARD_WIDTH,BOARD_HEIGHT))
    L1[BOARD_WIDTH/2-1:BOARD_WIDTH/2+2,0] = 3
    L1[BOARD_WIDTH/2+1,1] = 3

    L2 = np.zeros((BOARD_WIDTH,BOARD_HEIGHT))
    L2[BOARD_WIDTH/2-1:BOARD_WIDTH/2+2,0] = 4
    L2[BOARD_WIDTH/2-1,1] = 4

    S1 = np.zeros((BOARD_WIDTH,BOARD_HEIGHT))
    S1[BOARD_WIDTH/2-1:BOARD_WIDTH/2+1,0] = 5
    S1[BOARD_WIDTH/2:BOARD_WIDTH/2+2,1] = 5

    S2 = np.zeros((BOARD_WIDTH,BOARD_HEIGHT))
    S2[BOARD_WIDTH/2:BOARD_WIDTH/2+2,0] = 6
    S2[BOARD_WIDTH/2-1:BOARD_WIDTH/2+1,1] = 6

    T = np.zeros((BOARD_WIDTH,BOARD_HEIGHT))
    T[BOARD_WIDTH/2-2:BOARD_WIDTH/2+1,0] = 7
    T[BOARD_WIDTH/2-1,1] = 7

    self.piece_types.append(line)
    self.piece_types.append(square)
    self.piece_types.append(L1)
    self.piece_types.append(L2)
    self.piece_types.append(S1)
    self.piece_types.append(S2)
    self.piece_types.append(T)

    # Set up previews of pieces

    self.preview = []
    for i in range(NUM_PIECE_TYPES):
      self.preview.append( np.zeros((8,8)) )
      # Set up borders
      self.preview[i][:,0] = 8
      self.preview[i][:,-1] = 8
      self.preview[i][0,:] = 8
      self.preview[i][-1,:] = 8

    # Line
    self.preview[0][2:6,4] = 1
    
    # Square
    self.preview[1][3:5,3:5] = 2
    
    # L1
    self.preview[2][3:6,4] = 3
    self.preview[2][5,3] = 3
    
    # L2
    self.preview[3][3:6,4] = 4
    self.preview[3][3,3] = 4
    
    # S1
    self.preview[4][3:5,3] = 5
    self.preview[4][4:6,4] = 5
    
    # S2
    self.preview[5][3:5,4] = 6
    self.preview[5][4:6,3] = 6
    
    # T
    self.preview[6][3,3] = 7
    self.preview[6][2:5,4] = 7

def get_colour(i):
  if i == 1:
    return GREEN
  elif i == 2:
    return RED
  elif i == 3:
    return BLUE
  elif i == 4:
    return PURPLE
  elif i == 5:
    return ORANGE
  elif i == 6:
    return YELLOW
  elif i == 7:
    return CYAN
  elif i == 8:
    return WHITE
  else:
    return BLACK

if __name__ == '__main__':
  t = Tetris()
  while True:
    t.run_game()
