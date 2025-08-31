import pygame   
from network import Network 
import pickle   
pygame.font.init()  

width = 700
height = 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")


class Button:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 150
        self.height = 100 
    def draw(self, win):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(win, self.color, rect)
        pygame.draw.rect(win, (255,255,255), rect, 2)

        font = pygame.font.SysFont("comicsans", 40)
        text = font.render(self.text, True, (255,255,255))
        win.blit(text, (self.x + self.width//2 - text.get_width()//2,
                        self.y + self.height//2 - text.get_height()//2))
   
        
    def click(self, pos):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return rect.collidepoint(pos)



def redrawWindow(win, game, p):
    win.fill((128,128,128))
    
    if not(game.connected()):
        font = pygame.font.SysFont("comicsans", 80)
        text = font.render("Waiting for Player...", 1, (255,0,0), True)
        win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
    else: 
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Your Move", 1, (0, 255, 255))
        win.blit(text, (80, 200))

        text = font.render("Opponents", 1, (0, 255, 255))
        win.blit(text, (380, 200))

        move1 = game.get_player_move(0)
        move2 = game.get_player_move(1)
    if game.bothWent():
        text1 = font.render(move1, 1, (0,0,0))
        text2 = font.render(move2, 1, (0,0,0))
    else:
        if game.p1Went and p == 0:
            text1 = font.render(move1, 1, (0,0,0))
        elif game.p1Went:
            text1 = font.render("Locked In", 1, (0,0,0))
        else:
            text1 = font.render("Waiting...", 1, (0,0,0))

        if game.p2Went and p == 1:
            text2 = font.render(move2, 1, (0,0,0))
        elif game.p2Went:
            text2 = font.render("Locked In", 1, (0,0,0))
        else:
            text2 = font.render("Waiting...", 1, (0,0,0))

    if p == 1:
        win.blit(text2, (100, 350))
        win.blit(text1, (400, 350))
    else:
        win.blit(text1, (100, 350))
        win.blit(text2, (400, 350))

    for btn in btns:
        btn.draw(win)
    pygame.display.update()
        



btns = [Button("Rock", 50, 500, (0,0,0)), Button("Scissors", 250, 500, (255,0,0)), Button("Paper", 450, 500, (0,255,0))]
def main(ip, port):
    run = True
    clock = pygame.time.Clock()

    
    win.fill((128,128,128))
    font = pygame.font.SysFont("comicsans", 60)
    txt = font.render("Connecting...", 1, (0, 0, 0))
    win.blit(txt, (width//2 - txt.get_width()//2, height//2 - txt.get_height()//2))
    pygame.display.update()

    n = Network("127.0.0.1", 5555)

    try:
        player = int(n.getP())
    except Exception:
        player = 0
    print("You are player", player)

    game = None
    retry_counter = 0

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                print("Mouse down at:", pos)
                for btn in btns:
                    if btn.click(pos):
                        print("Clicked button:", btn.text)
                        if not (game and game.connected()):
                            print("Not ready (game.connected() == False)")
                            break
                        try:
                            if player == 0 and not game.p1Went:
                                n.send(btn.text)
                            elif player == 1 and not game.p2Went:
                                n.send(btn.text)
                            else:
                                print("Already locked in for this player.")
                        except Exception as e:
                            print("Send failed:", e)
                           
                            return "BACK"

        try:
            game = n.send("get")
            retry_counter = 0
        except Exception:
            retry_counter += 1
            game = None

        win.fill((128, 128, 128))
        font = pygame.font.SysFont("comicsans", 60)

        if game is None:
 
            small = pygame.font.SysFont("comicsans", 40)
            msg = small.render(f"Connecting to server... (retry {retry_counter})", True, (200, 0, 0))
            win.blit(msg, (width//2 - msg.get_width()//2, height//2 - msg.get_height()//2))
            pygame.display.update()
            continue

   
        if hasattr(game, "connected") and not game.connected():
            wait = font.render("Waiting for Player...", True, (255, 0, 0))
            win.blit(wait, (width//2 - wait.get_width()//2, height//2 - wait.get_height()//2))
            pygame.display.update()
            continue

        
        if hasattr(game, "bothWent") and game.bothWent():
            
            result = game.winner()

            
            redrawWindow(win, game, player)
            pygame.time.delay(500)

            
            result_font = pygame.font.SysFont("comicsans", 90)
            if (result == 1 and player == 1) or (result == 0 and player == 0):
                text = result_font.render("You Won!", True, (255, 0, 0))
            elif result == -1:
                text = result_font.render("Tie Game!", True, (255, 0, 0))
            else:
                text = result_font.render("You Lost...", True, (255, 0, 0))

            win.blit(text, (width//2 - text.get_width()//2, height//2 - text.get_height()//2))
            pygame.display.update()
            pygame.time.delay(2000)

           
            try:
                _ = n.send("reset")
            except Exception:
                err = pygame.font.SysFont("comicsans", 40).render("Reset failed. Retrying...", True, (200, 0, 0))
                win.blit(err, (width//2 - err.get_width()//2, height//2 + 40))
                pygame.display.update()
                
        redrawWindow(win, game, player)


def menu_screen():
    run = True 
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        win.fill((128,128,128))
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Click to Play!", 1, (255,0,0))
        win.blit(text, (100,200))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"  
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "PLAY"

running = True
while running:
    action = menu_screen()
    if action == "EXIT":
        break

    result = main("127.0.0.1", 5555)
    if result == "EXIT":
        break

pygame.quit()