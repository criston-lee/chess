import os

class Piece:
    
    def __init__(self,name,color,value,texture=None,texture_rect=None):
        self.name = name
        self.color = color
        value_sign = 1 if color == "white" else -1
        self.value = value * value_sign #Basically white will have positive values, black will have negative value
        self.moves = [] #Valid Moves
        self.moved = False
        self.texture = texture
        self.set_texture()
        self.texture_rect = texture_rect
    
    def set_texture(self,size=80): 
        self.texture = os.path.join(
            f"assets/images/imgs-{size}px/{self.color}_{self.name}.png"
        )
    
    def add_move(self,move):
        self.moves.append(move)
    
    def clear_moves(self):
        self.moves = []

class Pawn(Piece):

    def __init__(self,color):
        self.dir = -1 if color =="white" else 1 #black goes down, matrix index increases going down and vice versa
        self.en_passant = False
        super().__init__("pawn",color,1.0) #Hard coded 1 here, adjust for nn if necessary



class Knight(Piece):

    def __init__(self,color):
        super().__init__("knight",color,3.0) #Knight

class Bishop(Piece):

    def __init__(self,color):
        super().__init__("bishop",color,3.0) #Bishop same as knight, maybe can adjust if necessary??


class Rook(Piece):

    def __init__(self,color):
        super().__init__("rook",color,5.0)

class Queen(Piece):

    def __init__(self,color):
        super().__init__("queen",color,9.0)

class King(Piece):

    def __init__(self, color):
        self.left_rook = None
        self.right_rook = None
        super().__init__("king",color,9999.0)