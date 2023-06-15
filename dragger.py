import pygame
from const import *

class Dragger: #Mouse basically...Can change name during implementation

    def __init__(self):
        self.piece = None
        self.dragging = False
        self.mouseX = 0
        self.mouseY = 0
        self.initial_row = 0
        self.initial_col = 0

#Blit method
    def update_blit(self,surface): #Blit places new image aka highlighted piece
        #Texture change, make it bigger when highlighted
        self.piece.set_texture(size=128)
        texture=self.piece.texture

        #New Image
        img = pygame.image.load(texture)

        #Rectangle
        img_center = (self.mouseX,self.mouseY)
        self.piece.texture_rect = img.get_rect(center=img_center)

        #Update blit
        surface.blit(img,self.piece.texture_rect)

#Non-blit methods

    def update_mouse(self,pos):
        self.mouseX, self.mouseY = pos #tuple of coordinate

    def save_initial(self,pos):
        self.initial_row = pos[1] // SQSIZE
        self.initial_col = pos[0] // SQSIZE
    
    def drag_piece(self,piece):
        self.piece = piece
        self.dragging = True

    def undrag_piece(self):
        self.piece = None
        self.dragging = False 
