import os
import pygame
from pygame.locals import QUIT, KEYDOWN, K_BACKSPACE, K_RETURN, MOUSEBUTTONUP


class Player:
    def __init__(self, name):
        self.cards = []
        self.name = name


class Board:
    def __init__(self, screen, players):
        self.screen = screen
        self.players = players
        self.queens = ['heart', 'rose', 'peacock', 'ice-cream', 'dog', 'cat', 'strawberry', 'sunflower', 'moon',
                       'rainbow', 'pancake', 'cake', 'ladybird', 'starfish', 'book', 'butterfly']
        self.queen_cards = []
        self.playable_cards = []
        self.bg_colour = (100, 100, 100)
        self.highlight_colour = (22, 106, 22)
        self.resource_dir = os.path.join('..', 'resources')
        self.card_back = os.path.join(self.resource_dir, 'card-back.jpg')
        self.queen_back = os.path.join(self.resource_dir, 'queen-back.jpg')
        self.queen_back_image = pygame.image.load(self.queen_back)
        self.queen_back_image = pygame.transform.scale(self.queen_back_image, (50, 70))
        self.card_back_image = pygame.image.load(self.card_back)
        self.card_back_image = pygame.transform.scale(self.card_back_image, (50, 70))

        screen_border = 30
        screen_center = screen.get_rect().center
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        self.player_positions = [(screen_border, screen_center[1]), (screen_center[0], screen_border),
                                 (screen_center[0], screen_height - screen_border),
                                 (screen_width - screen_border, screen_center[1])]
        self.playable_card_offsets = [(50, -100), (50, -50), (50, 0), (50, 50), (50, 100)]
        self.playable_card_positions = []

    def initialise_players(self):
        self.screen.fill(self.bg_colour)
        font = pygame.font.Font(None, 50)

        for player_index, player_name in enumerate(self.players):
            label = font.render(player_name, True, (200, 200, 200))
            rect = label.get_rect()
            rect.center = self.player_positions[player_index]
            self.screen.blit(label, rect)

        for card_pos in self.playable_cards:
            card_rect = self.card_back_image.get_rect()
            card_rect.center = card_pos
            card_border = pygame.Rect(card_rect.x - 5, card_rect.y - 5, card_rect.width + 10, card_rect.height + 10)
            pygame.draw.rect(self.screen, self.bg_colour, card_border)
            self.screen.blit(self.card_back_image, card_rect)

    def initialise_card_positions(self):
        for player_index, player_name in enumerate(self.players):
            for i in range(len(self.playable_card_offsets)):
                starting_position = self.player_positions[player_index]
                if player_index == 0:
                    target_position = (starting_position[0] + self.playable_card_offsets[i][0],
                                       starting_position[1] + self.playable_card_offsets[i][1])
                elif player_index == 1:
                    target_position = (starting_position[0] + self.playable_card_offsets[i][1],
                                       starting_position[1] + self.playable_card_offsets[i][0])
                elif player_index == 2:
                    target_position = (starting_position[0] - self.playable_card_offsets[i][1],
                                       starting_position[1] + self.playable_card_offsets[i][0])
                else:
                    target_position = (starting_position[0] - self.playable_card_offsets[i][0],
                                       starting_position[1] - self.playable_card_offsets[i][1])

                self.playable_card_positions.append(target_position)

    def initialise_queens(self):
        screen_center = self.screen.get_rect().center

        queen_vert_gap = int(float(self.screen.get_height()) / 7)
        self.queen_cards = []
        for queen_row in range(4):
            for queen_col in range(2):
                for queen_side in [-1, 1]:
                    queen_centre_y = screen_center[1] + (queen_row - 1.5) * (queen_vert_gap)
                    queen_centre_x = screen_center[0] + ((queen_col + 1) * 70) * queen_side

                    queen_rect = self.queen_back_image.get_rect()
                    queen_rect.center = (queen_centre_x, queen_centre_y)
                    self.queen_cards.append(queen_rect)
                    queen_border = pygame.Rect(queen_rect.x - 5, queen_rect.y - 5, queen_rect.width + 10, queen_rect.height + 10)
                    pygame.draw.rect(self.screen, self.bg_colour, queen_border)
                    self.screen.blit(self.queen_back_image, queen_rect)

    def deselect_queens(self):
        for queen in self.queen_cards:
            target_border = pygame.Rect(queen.x - 5, queen.y - 5,
                                        queen.width + 10, queen.height + 10)
            pygame.draw.rect(self.screen, self.highlight_colour, target_border)
            self.screen.blit(self.queen_back, queen)


def enter_players():
    pygame.init()
    pygame.display.set_caption("Sleeping Queens")
    screen = pygame.display.set_mode((580, 660))
    player_name = ""
    max_players = 4
    current_player = 1
    players = []
    font = pygame.font.Font(None, 50)
    select_players = True
    while select_players:
        for evt in pygame.event.get():
            if evt.type == KEYDOWN:
                if evt.unicode.isalpha():
                    player_name += evt.unicode
                elif evt.key == K_BACKSPACE:
                    player_name = player_name[:-1]
                elif evt.key == K_RETURN:
                    if not player_name:
                        print('Finished player assignment:')
                        print('\n'.join(players))
                        select_players = False
                    else:
                        players.append(player_name)
                    player_name = ""
                    current_player += 1
                    if current_player > max_players:
                        print('All players assigned')
                        select_players = False
            elif evt.type == QUIT:
                return
        screen.fill((0, 0, 0))
        screen_center = screen.get_rect().center
        for i in range(max_players):
            if len(players) > i:
                block = font.render(players[i], True, (255, 255, 255))
                rect = block.get_rect()
                rect.center = (screen_center[0] + (rect.width / 2) - 20, ((i - 1) * 50) + screen_center[1])
                screen.blit(block, rect)
            else:
                block = font.render(player_name, True, (255, 255, 255))
            label = font.render('Player{}:'.format(i), True, (200, 200, 200))
            label_rect = label.get_rect()
            label_rect.center = (100, screen_center[1] + ((i - 1) * 50))
            screen.blit(label, label_rect)

        rect = block.get_rect()
        rect.center = (screen_center[0] + (rect.width / 2) - 20, ((current_player - 2) * 50) + screen_center[1])
        screen.blit(block, rect)
        pygame.display.flip()

    print('Players selected: {}'.format(len(players)))
    if len(players) > 0:
        start_game(screen, players)




def move_card_to_destination(screen, board, source_picture, source_coords, target_coords):
    # create a new image at the source coords
    picture = pygame.image.load(source_picture)
    picture = pygame.transform.scale(picture, (50, 70))
    pic_rect = picture.get_rect()
    pic_rect.center = source_coords

    # move it to the target
    num_moves = 100
    x_distance = source_coords[0] - target_coords[0]
    y_distance = source_coords[1] - target_coords[1]

    for i in range(num_moves):
        bg_colour = (100, 100, 100)
        screen.fill(bg_colour)
        board.initialise_players()
        position = pic_rect.center
        x_increment = int(float(x_distance) / float(num_moves))
        y_increment = int(float(y_distance) / float(num_moves))
        new_position = (position[0] - (x_increment * i), position[1] - (y_increment * i))
        screen.blit(picture, new_position)
        pygame.display.update()
        pygame.time.delay(1)


def start_game(screen, player_list):
    board = Board(screen, player_list)
    board.initialise_players()
    board.initialise_card_positions()
    screen_center = screen.get_rect().center

    for target_position in board.playable_card_positions:
        print(target_position)
        board.playable_cards.append(target_position)
        move_card_to_destination(screen, board, board.card_back, screen_center, target_position)

    board.initialise_queens()

    picture = pygame.image.load(board.card_back)
    picture = pygame.transform.scale(picture, (50, 70))
    pic_rect = picture.get_rect()
    pic_rect.center = screen_center
    border = pygame.Rect(pic_rect.x - 5, pic_rect.y - 5, pic_rect.width + 10, pic_rect.height + 10)
    pygame.draw.rect(screen, board.bg_colour, border)
    screen.blit(picture, pic_rect)

    while True:
        for evt in pygame.event.get():
            if evt.type == QUIT:
                return
            elif evt.type == MOUSEBUTTONUP:
                if pic_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, board.highlight_colour, border)
                    screen.blit(picture, pic_rect)
                else:
                    hit_queen = False
                    for queen in board.queen_cards:
                        if queen.collidepoint(pygame.mouse.get_pos()):
                            hit_queen = True
                            target_queen = queen
                            break

                    if hit_queen:
                        board.deselect_queens()
                        target_border = pygame.Rect(target_queen.x - 5, target_queen.y - 5,
                                                    target_queen.width + 10, target_queen.height + 10)
                        pygame.draw.rect(screen, board.highlight_colour, target_border)
                        screen.blit(board.queen_back_image, target_queen)
                    else:
                        board.deselect_queens()

                        pygame.draw.rect(screen, board.bg_colour, border)
                        screen.blit(picture, pic_rect)

        pygame.display.flip()


if __name__ == "__main__":
    enter_players()
    pygame.quit()