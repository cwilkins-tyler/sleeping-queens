import os
import re
import pygame
from random import shuffle
from pygame.locals import QUIT, KEYDOWN, K_BACKSPACE, K_RETURN, MOUSEBUTTONUP


class Card:
    def __init__(self):
        self.center = None
        self.x = None
        self.y = None
        self.card_type = None
        self.image = None
        self.width = 50
        self.height = 70
        self.highlight_colour = (22, 106, 22)
        self.selected = False

    def pos_center(self, x, y):
        self.center = (x, y)
        self.x = x - (self.width / 2)
        self.y = y - (self.height / 2)

    def draw_card(self, screen, coords, image, bg_colour):
        card_rect = image.get_rect()
        card_rect.center = coords
        card_border = pygame.Rect(card_rect.x - 5, card_rect.y - 5, card_rect.width + 10, card_rect.height + 10)
        pygame.draw.rect(screen, bg_colour, card_border)
        screen.blit(image, card_rect)
        self.pos_center(coords[0], coords[1])
        self.image = image

    def card_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def card_file(self, resource_dir):
        return os.path.join(resource_dir, 'card-{}.jpg'.format(self.card_type))

    def is_clicked(self):
        card_rect = self.card_rect()
        return card_rect.collidepoint(pygame.mouse.get_pos())

    def select(self, screen):
        self.draw_card(screen, self.center, self.image, self.highlight_colour)
        self.selected = True


class Player:
    def __init__(self, name):
        self.cards = []
        self.card_positions = []
        self.name = name


class Board:
    def __init__(self, screen, players):
        self.screen = screen
        self.bg_colour = (100, 100, 100)
        self.resource_dir = os.path.join('..', 'resources')
        self.player_names = players
        self.queens = ['heart', 'rose', 'peacock', 'ice-cream', 'dog', 'cat', 'strawberry', 'sunflower',
                       'rainbow', 'pancake', 'cake', 'ladybird', 'starfish', 'book', 'butterfly', 'moon']
        self.full_deck = ['1', '1', '1', '1', '2', '2', '2', '2', '3', '3', '3', '3', '4', '4', '4', '4',
                          '5', '5', '5', '5', '6', '6', '6', '6', '7', '7', '7', '7', '8', '8', '8', '8',
                          '9', '9', '9', '9', '10', '10', '10', '10', 'king-fire', 'potion', 'wand',
                          'knight', 'dragon', 'jester']
        self.players = []
        self.player_turn = 0
        self.queen_cards = []
        self.playable_cards = []
        self.current_selection = []
        self.card_back = os.path.join(self.resource_dir, 'card-back.jpg')
        self.queen_back = os.path.join(self.resource_dir, 'queen-back.jpg')
        self.queen_back_image = pygame.image.load(self.queen_back)
        self.queen_back_image = pygame.transform.scale(self.queen_back_image, (50, 70))
        self.card_back_image = pygame.image.load(self.card_back)
        self.card_back_image = pygame.transform.scale(self.card_back_image, (50, 70))
        self.center_stack = None
        screen_border = 30
        card_border = 75
        self.screen_center = screen.get_rect().center
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        self.player_positions = [(screen_border, self.screen_center[1]), (self.screen_center[0], screen_border),
                                 (screen_width - screen_border, self.screen_center[1]),
                                 (self.screen_center[0], screen_height - screen_border)]
        self.playable_card_offsets = [(card_border, -150), (card_border, -75), (card_border, 0), (card_border, 75),
                                      (card_border, 150)]
        # playable card positions is a list of x,y coords which contain playable cards for the given players
        self.playable_card_positions = []

    def initialise_players(self):
        for player_index, player_name in enumerate(self.player_names):
            player = Player(player_name)
            self.players.append(player)

    def initialise_board(self):
        self.screen.fill(self.bg_colour)
        font = pygame.font.Font(None, 50)

        for player_index, player_name in enumerate(self.player_names):
            label = font.render(player_name, True, (200, 200, 200))
            rect = label.get_rect()
            rect.center = self.player_positions[player_index]
            self.screen.blit(label, rect)

        for card_pos in self.playable_cards:
            player_card = Card()
            player_card.draw_card(self.screen, card_pos, self.card_back_image, self.bg_colour)

    def initialise_card_positions(self):
        for i in range(len(self.playable_card_offsets)):
            for player_index, player_name in enumerate(self.player_names):
                starting_position = self.player_positions[player_index]
                if player_index == 0:
                    target_position = (starting_position[0] + self.playable_card_offsets[i][0],
                                       starting_position[1] + self.playable_card_offsets[i][1])
                elif player_index == 1:
                    target_position = (starting_position[0] + self.playable_card_offsets[i][1],
                                       starting_position[1] + self.playable_card_offsets[i][0])
                elif player_index == 2:
                    target_position = (starting_position[0] - self.playable_card_offsets[i][0],
                                       starting_position[1] - self.playable_card_offsets[i][1])
                else:
                    target_position = (starting_position[0] - self.playable_card_offsets[i][1],
                                       starting_position[1] - self.playable_card_offsets[i][0])

                self.playable_card_positions.append(target_position)

    def deal_initial_cards(self):
        shuffle(self.full_deck)
        for card_index, target_position in enumerate(self.playable_card_positions):
            self.move_card_to_destination(self.card_back, self.screen_center, target_position)
            self.playable_cards.append(target_position)
            target_player = self.players[card_index % len(self.players)]
            target_card = Card()
            target_card.card_type = self.full_deck[card_index]
            target_card.pos_center(target_position[0], target_position[1])
            target_player.cards.append(target_card)
            self.initialise_board()

    def initialise_queens(self):
        queen_vert_gap = int(float(self.screen.get_height()) / 9)
        queen_horiz_gap = 70
        self.queen_cards = []
        shuffle(self.queens)
        for queen_row in range(4):
            for queen_col in range(2):
                for queen_side in [-1, 1]:
                    queen_centre_y = self.screen_center[1] + (queen_row - 1.5) * queen_vert_gap
                    queen_centre_x = self.screen_center[0] + ((queen_col + 1) * queen_horiz_gap) * queen_side

                    queen_card = Card()
                    queen_card.draw_card(self.screen, (queen_centre_x, queen_centre_y), self.queen_back_image,
                                         self.bg_colour)
                    self.queen_cards.append(queen_card)

    def select_queen(self):
        target_queen = None
        for queen in self.queen_cards:
            if queen.is_clicked():
                target_queen = queen
                break

        if target_queen:
            self.deselect_queens()
            queen_name = self.queens[self.queen_cards.index(target_queen)]
            chosen_queen = os.path.join(self.resource_dir, 'queen-{}.jpg'.format(queen_name))
            queen_image = pygame.image.load(chosen_queen)
            queen_image = pygame.transform.scale(queen_image, (60, 80))
            target_queen.draw_card(self.screen, target_queen.center, queen_image, self.bg_colour)
            target_queen.select(self.screen)
        else:
            self.deselect_queens()

    def deselect_queens(self):
        for queen in self.queen_cards:
            queen.draw_card(self.screen, queen.center, self.queen_back_image, self.bg_colour)

    def move_card_to_destination(self, source_picture, source_coords, target_coords):
        # create a new image at the source coords
        picture = pygame.image.load(source_picture)
        picture = pygame.transform.scale(picture, (50, 70))
        pic_rect = picture.get_rect()
        pic_rect.center = source_coords

        # move it to the target
        num_moves = 100
        x_distance = source_coords[0] - target_coords[0]
        y_distance = source_coords[1] - target_coords[1]
        x_increment = float(x_distance) / float(num_moves)
        y_increment = float(y_distance) / float(num_moves)

        for i in range(num_moves + 1):
            bg_colour = (100, 100, 100)
            self.screen.fill(bg_colour)
            position = pic_rect.center
            new_position = (round(position[0] - (x_increment * i)), round(position[1] - (y_increment * i)))
            self.initialise_board()
            self.screen.blit(picture, new_position)
            pygame.display.update()
            pygame.time.delay(1)

    def show_player_cards(self):
        current_player = self.players[self.player_turn]
        for card in current_player.cards:
            target_card_file = card.card_file(self.resource_dir)
            if not os.path.isfile(target_card_file):
                target_card_file = os.path.join(self.resource_dir, 'card-1.jpg')

            target_card = pygame.image.load(target_card_file)
            target_card = pygame.transform.scale(target_card, (card.width, card.height))
            card.draw_card(self.screen, card.center, target_card, self.bg_colour)
            if card.selected:
                card.select(self.screen)

    def hide_player_cards(self):
        current_player = self.players[self.player_turn]
        for card in current_player.cards:
            card.draw_card(self.screen, card.center, self.card_back_image, self.bg_colour)
            card.selected = False

    def select_player_card(self):
        current_player = self.players[self.player_turn]
        for card in current_player.cards:
            if card.is_clicked():
                card.select(self.screen)
                self.current_selection.append(card)
                return True

        return False

    def draw_center_card(self):
        center_card = Card()
        center_card.draw_card(self.screen, self.screen_center, self.card_back_image, self.bg_colour)
        return center_card

    def is_center_card_selected(self):
        if self.center_stack.is_clicked():
            return True
        else:
            return False

    def valid_move(self):
        if len(self.current_selection) == 1:
            # any single card can be played
            return True
        else:
            # multiple cards must all be numbers
            all_numbers = True
            for card in self.current_selection:
                if not re.search('^\d+$', card.card_type):
                    all_numbers = False

            return all_numbers

    def do_player_turn(self):
        self.center_stack = self.draw_center_card()
        self.show_player_cards()
        for event in pygame.event.get():
            if event.type == QUIT:
                print('Exiting')
                self.hide_player_cards()
                return 1
            elif event.type == MOUSEBUTTONUP:
                if self.select_player_card():
                    print('Player Card selected')
                elif self.is_center_card_selected():
                    if self.valid_move():
                        print('Moving cards')
                    else:
                        print('Not a valid move')

                    print('Ending turn: {}'.format(self.player_turn))
                    self.hide_player_cards()
                    self.player_turn += 1
                    self.player_turn %= len(self.player_names)
                else:
                    self.select_queen()

        return 0


def enter_players():
    pygame.init()
    pygame.display.set_caption("Sleeping Queens")
    screen = pygame.display.set_mode((800, 800))
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

        if len(players) < max_players:
            rect = block.get_rect()
            rect.center = (screen_center[0] + (rect.width / 2) - 20, ((current_player - 2) * 50) + screen_center[1])
            screen.blit(block, rect)
            pygame.display.flip()

    print('Players selected: {}'.format(len(players)))
    if len(players) > 0:
        start_game(screen, players)


def start_game(screen, player_list):
    board = Board(screen, player_list)
    board.initialise_players()
    board.initialise_board()
    board.initialise_card_positions()
    board.deal_initial_cards()
    board.initialise_queens()

    while True:
        for evt in pygame.event.get():
            if evt.type == QUIT:
                return

        if board.do_player_turn():
            return

        pygame.display.flip()


if __name__ == "__main__":
    enter_players()
    pygame.quit()
