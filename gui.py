import pygame

class UI():
    def __init__(self, window, fps, board_size, main_menu_image, clock, text):
        self.window = window
        self.fps = fps
        self.board_size = board_size
        self.main_menu_image = main_menu_image
        self.clock = clock
        self.text = text


    def MainMenu(self):
        pygame.font.init()
        my_font = pygame.font.Font(None, 100)
        text = my_font.render(self.text, True, (255,255,255))
        text_rect = text.get_rect(center=(self.board_size/2, self.board_size/6))    
        black_button = pygame.Surface((75, 50))
        black_button.fill((0,0,0))
        white_button = pygame.Surface((75, 50))
        white_button.fill((255, 255, 255))
        line = pygame.Surface((self.board_size, 75))
        line.fill((50, 50, 50))

        self.window.blit(self.main_menu_image, (0, 0))
        self.window.blit(text, text_rect)  
        self.window.blit(line, (0, self.board_size*0.8))  
        while True:
            self.window.blit(white_button, (self.board_size/2-80, self.board_size*0.8+12.5))
            self.window.blit(black_button, (self.board_size/2+10, self.board_size*0.8+12.5))
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    # black button
                    if pos[0] > self.board_size/2+10 and pos[0] < self.board_size/2+85 and pos[1] > self.board_size*0.8+12.5 and pos[1] < self.board_size*0.8+12.5+50:
                        return True
                    # white button
                    if pos[0] > self.board_size/2-80 and pos[0] < self.board_size/2-5 and pos[1] > self.board_size*0.8+12.5 and pos[1] < self.board_size*0.8+12.5+50:
                        return False
            pygame.display.update()

    