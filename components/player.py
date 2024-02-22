from pygame import Surface, sprite
from pygame import K_w, K_a, K_s, K_d, K_LEFT, K_RIGHT, K_UP, K_DOWN, Vector2
from math import sqrt

class Movable(sprite.Sprite):
  def move(self, movement:Vector2):
    self.rect.x += movement.x # type:ignore
    self.rect.y += movement.y # type:ignore
  
  def move_x(self, value:int):
    self.rect.x += value # type:ignore
  
  def move_y(self, value:int):
    self.rect.y += value # type:ignore

class Player(Movable):
  def __init__(self, x, y, image:Surface, speed = 5, gravity = 0.5, jump_power = 10):
    sprite.Sprite.__init__(self)
    self.x = x
    self.y = y
    self.max_speed = speed
    self.speed = speed
    self.image = image
    self.rect = image.get_rect()
    self.gravity = gravity
    self.jump_momentum = Vector2(0, 0)
    self.jump_power = 10
  
  def normalise_movement(self, movement):
    """This takes both speeds into account to ensure that the player moves consistently"""
    if movement.x != 0 and movement.y != 0:
      self.speed = self.max_speed / sqrt(2)
    else:
      self.speed = self.max_speed
    return movement

  def add_speed(self, movement):
    """returns the movement at the required speed"""
    movement.x = movement.x * self.speed
    movement.y = movement.y * self.speed
    
    return movement
  
  def check_movement(self, keys_pressed, state) -> Vector2:
    """applies the movement vector to the object, generated from key presses"""
    pressing = keys_pressed
    movement = Vector2(0, 0)
    
    if state.get_state() == "editor mode":
      if pressing[K_UP]:
        movement.y -= 1
      if pressing[K_DOWN]:
        movement.y += 1
      if pressing[K_LEFT]:
        movement.x -= 1
      if pressing[K_RIGHT]:
        movement.x += 1
        
    
    elif state.get_state() == "game":
      if pressing[K_LEFT]:
        movement.x -= 1
      if pressing[K_RIGHT]:
        movement.x += 1
      
    movement = self.normalise_movement(movement)

    return movement
  
  def jump(self):
    self.jump_momentum.y = -1 * self.jump_power
    self.move_y(-1)
    if self.jump_momentum.y > -1 * self.jump_power:
      self.jump_momentum.y = -1 * self.jump_power
  
  def update(self, keys_pressed, state, tile_space):
    """
    
    - check horizontal movement
    - check horizontal collisions
    
    - check vertical movement
    - check vertical collisions
    
    """
    # get all movement
    movement = self.add_speed(self.check_movement(keys_pressed, state))
    
    # check horizontal movement
    self.move_x(movement.x)
    
    if state.get_state() == "editor mode":
      # dont bother with collisions
      self.move_y(movement.y)
    
    if state.get_state() == "game":
      # check collisions
      
      soft_colliding_tiles = tile_space.collide_tile_rect(self.rect, False)
      
      if not soft_colliding_tiles:
        print("died")
        # self.respawn()
      
      else:
        # resolve collisions:
        for tile in soft_colliding_tiles:
          if tile_space.check_collidable([tile]):
            if self.rect.left > tile.rect.right:
              self.rect.left = tile.rect.right
            if self.rect.right < tile.rect.left:
              self.rect.right = tile.rect.left
        
        # calculate whether jump momentum is cancelled
        
        soft_colliding_tiles = tile_space.collide_tile_rect(self.rect, False, always_return_values = False)
        hard_colliding_tiles = tile_space.check_collidable(soft_colliding_tiles)
        
        if self.jump_momentum.y > 0:
          moving = "down"
        elif self.jump_momentum.y < 0:
          moving = "up"
        else:
          moving = "still"
        
        summed = sum(hard_colliding_tiles)
        if summed > 0:
          colliding = True
        elif summed == 0:
          colliding = False
        
        if not colliding:
          self.jump_momentum.y += self.gravity
          movement += self.jump_momentum
        
        else:
          self.jump_momentum.y = 0
        
        self.move_y(movement.y)
        
        # post-movement, re-calculate collisions
        soft_colliding_tiles = tile_space.collide_tile_rect(self.rect, False, always_return_values = False)
        print()
        print(f"Player rect (t, l, b, r): {self.rect.top}, {self.rect.right}, {self.rect.bottom}, {self.rect.left}")
        
        for tile in soft_colliding_tiles:
          if tile_space.check_collidable([tile])[0]:
            print(f"Player rect (t, l, b, r): {self.rect.top}, {self.rect.right}, {self.rect.bottom}, {self.rect.left}")
            
            if moving == "down" and self.rect.top != tile.rect.bottom:
              self.rect.bottom = tile.rect.top
            elif moving == "up" and self.rect.bottom != tile.rect.top:
              self.rect.top = tile.rect.bottom
    

  def draw(self, window:Surface):
    window.blit(self.image, (self.rect.x, self.rect.y))