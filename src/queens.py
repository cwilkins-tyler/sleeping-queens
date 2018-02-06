import os
import re
import time
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
        self.is_queen = False
        self.queen_awake = False
        self.moving = False

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

    def hide_card(self, screen, image, bg_colour):
        self.draw_card(screen, self.center, image, bg_colour)
        self.selected = False

    def show_card(self, screen, image_file, bg_colour):
        loaded_image = pygame.image.load(image_file)
        loaded_image = pygame.transform.scale(loaded_image, (50, 70))
        self.draw_card(screen, self.center, loaded_image, bg_colour)
        self.image = loaded_image
        self.selected = True

    def card_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def card_file(self, resource_dir):
        if self.is_queen:
            queen_file = os.path.join(resource_dir, 'queen-{}.jpg'.format(self.card_type))
            return queen_file
        else:
            return os.path.join(resource_dir, 'card-{}.jpg'.format(self.card_type))

    def is_clicked(self):
        card_rect = self.card_rect()
        return card_rect.collidepoint(pygame.mouse.get_pos())

    def is_number_card(self):
        if re.search('^\d+$', self.card_type):
            return True
        else:
            return False

    def select(self, screen):
        self.draw_card(screen, self.center, self.image, self.highlight_colour)
        self.selected = True

    def deselect(self, screen, bg_colour):
        self.draw_card(screen, self.center, self.image, bg_colour)
        self.selected = False


class Player:
    def __init__(self, name):
        self.cards = []
        self.queens = []
        self.card_positions = []
        self.name = name


class Board:
    def __init__(self, screen, players):
        self.screen = screen
        self.animations = False
        self.bg_colour = (100, 100, 100)
        self.player_colour = (200, 200, 200)
        self.resource_dir = os.path.join('..', 'resources')
        self.player_names = players
        self.queens = ['heart', 'rose', 'peacock', 'ice-cream', 'dog', 'cat', 'strawberry', 'sunflower',
                       'rainbow', 'pancake', 'cake', 'ladybird', 'starfish', 'book', 'butterfly', 'moon']
        self.full_deck = ['1', '1', '1', '1', '2', '2', '2', '2', '3', '3', '3', '3', '4', '4', '4', '4',
                          '5', '5', '5', '5', '6', '6', '6', '6', '7', '7', '7', '7', '8', '8', '8', '8',
                          '9', '9', '9', '9', '10', '10', '10', '10', 'king-cookie', 'king-fire', 'king-hat',
                          'king-tie-dye', 'king-turtle', 'king-puzzle', 'king-pasta', 'king-tool', 'king-bubble-gum',
                          'king-chess', 'potion', 'potion', 'potion', 'potion', 'wand', 'wand', 'wand',
                          'knight', 'knight', 'knight', 'knight', 'dragon', 'dragon', 'dragon',
                          'jester', 'jester', 'jester', 'jester']
        self.discard_pile = []
        self.players = []
        self.player_turn = 0
        self.turn_over = False
        self.game_over = False
        self.cards_per_player = 5
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
        # player queen positions is a list of x,y coords where the woken queens will be placed
        self.playable_card_positions = []
        self.player_queen_positions = []
        self.sleeping_queen_positions = []

    def initialise_players(self):
        for player_index, player_name in enumerate(self.player_names):
            player = Player(player_name)
            self.players.append(player)

    def draw_player_name(self, player_name, player_index, colour=None):
        if not colour:
            colour = self.player_colour

        font = pygame.font.Font(None, 50)
        label = font.render(player_name, True, colour)
        if player_index % 2 == 0:
            rotation = (player_index + 1) * 90
            label = pygame.transform.rotate(label, rotation)
        rect = label.get_rect()
        rect.center = self.player_positions[player_index]
        self.screen.blit(label, rect)

    def draw_player_names(self):
        for player_index, player_name in enumerate(self.player_names):
            self.draw_player_name(player_name, player_index)

    def initialise_board(self):
        self.screen.fill(self.bg_colour)
        self.draw_player_names()

        for card_pos in self.playable_cards:
            player_card = Card()
            player_card.draw_card(self.screen, card_pos, self.card_back_image, self.bg_colour)

        for player in self.players:
            for queen in player.queens:
                if not queen.moving:
                    queen.draw_card(self.screen, queen.center, queen.image, self.bg_colour)

    def initialise_card_positions(self):
        queen_offset = 75
        for i in range(len(self.playable_card_offsets)):
            for player_index, player_name in enumerate(self.player_names):
                starting_position = self.player_positions[player_index]
                if player_index == 0:
                    # left
                    target_position = (starting_position[0] + self.playable_card_offsets[i][0],
                                       starting_position[1] + self.playable_card_offsets[i][1])
                    queen_position = (target_position[0] + queen_offset, target_position[1])
                elif player_index == 1:
                    # top
                    target_position = (starting_position[0] + self.playable_card_offsets[i][1],
                                       starting_position[1] + self.playable_card_offsets[i][0])
                    queen_position = (target_position[0], target_position[1] + queen_offset)
                elif player_index == 2:
                    # right
                    target_position = (starting_position[0] - self.playable_card_offsets[i][0],
                                       starting_position[1] - self.playable_card_offsets[i][1])
                    queen_position = (target_position[0] - queen_offset, target_position[1])
                else:
                    # bottom
                    target_position = (starting_position[0] - self.playable_card_offsets[i][1],
                                       starting_position[1] - self.playable_card_offsets[i][0])
                    queen_position = (target_position[0], target_position[1] - queen_offset)

                self.playable_card_positions.append(target_position)
                if len(self.player_queen_positions) <= player_index:
                    self.player_queen_positions.append([])

                self.player_queen_positions[player_index].append(queen_position)

    def deal_initial_cards(self):
        shuffle(self.full_deck)
        num_cards = len(self.full_deck)
        for card_index, target_position in enumerate(self.playable_card_positions):
            if self.animations:
                self.move_card_to_destination(self.card_back, self.screen_center, target_position)
            self.playable_cards.append(target_position)
            target_player = self.players[card_index % len(self.players)]
            target_card = Card()
            target_card.card_type = self.full_deck[card_index]
            self.full_deck.pop()
            target_card.pos_center(target_position[0], target_position[1])
            target_player.cards.append(target_card)
            self.initialise_board()

        assert len(self.full_deck) == num_cards - len(self.players) * self.cards_per_player

    def initialise_queens(self):
        queen_vert_gap = int(float(self.screen.get_height()) / 9)
        queen_horiz_gap = 70
        self.queen_cards = []
        shuffle(self.queens)
        queen_index = 0
        for queen_row in range(4):
            for queen_col in range(2):
                for queen_side in [-1, 1]:
                    queen_centre_y = self.screen_center[1] + (queen_row - 1.5) * queen_vert_gap
                    queen_centre_x = self.screen_center[0] + ((queen_col + 1) * queen_horiz_gap) * queen_side

                    queen_card = Card()
                    queen_card.draw_card(self.screen, (queen_centre_x, queen_centre_y), self.queen_back_image,
                                         self.bg_colour)
                    queen_card.card_type = self.queens[queen_index]
                    queen_card.is_queen = True
                    self.queen_cards.append(queen_card)
                    queen_index += 1

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
            queen_image = pygame.transform.scale(queen_image, (target_queen.width, target_queen.height))
            target_queen.draw_card(self.screen, target_queen.center, queen_image, self.bg_colour)
            target_queen.select(self.screen)
        else:
            self.deselect_queens()

    def deselect_queens(self):
        for queen in self.queen_cards:
            if not queen.queen_awake:
                queen.selected = False
                queen.draw_card(self.screen, queen.center, self.queen_back_image, self.bg_colour)

    def select_queens(self, asleep=True, exclude_player=None):
        if asleep:
            for queen in self.queen_cards:
                if not queen.queen_awake:
                    queen.select(self.screen)
        else:
            for player in self.players:
                if player != exclude_player:
                    for queen in player.queens:
                        if queen.card_type != 'strawberry':
                            queen.select(self.screen)

    def reorder_queens(self, source_player):
        player_index = self.players.index(source_player)
        for queen_index, queen in enumerate(source_player.queens):
            if queen.center != self.player_queen_positions[player_index][queen_index]:
                queen_destination = self.player_queen_positions[player_index][queen_index]
                queen.center = queen_destination
                queen.moving = True
                self.move_card_to_destination(queen.card_file(self.resource_dir), queen.center,
                                              queen_destination)
                queen.moving = False

    def move_card_to_destination(self, source_picture, source_coords, target_coords):
        # create a new image at the source coords
        picture = pygame.image.load(source_picture)
        picture = pygame.transform.scale(picture, (50, 70))

        temp_card = Card()
        temp_card.draw_card(self.screen, source_coords, picture, self.bg_colour)

        # move it to the target
        num_moves = 100
        x_distance = source_coords[0] - target_coords[0]
        y_distance = source_coords[1] - target_coords[1]
        x_increment = float(x_distance) / float(num_moves)
        y_increment = float(y_distance) / float(num_moves)

        for i in range(num_moves + 1):
            self.screen.fill(self.bg_colour)
            new_position = (round(source_coords[0] - (i * x_increment)), round(source_coords[1] - (i * y_increment)))
            self.initialise_board()
            temp_card.draw_card(self.screen, new_position, picture, self.bg_colour)
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
            card.hide_card(self.screen, self.card_back_image, self.bg_colour)

    def select_player_card(self):
        current_player = self.players[self.player_turn]
        for card in current_player.cards:
            if card.is_clicked():
                if card.selected:
                    card.deselect(self.screen, self.bg_colour)
                    self.current_selection.remove(card)
                    return True
                else:
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
            # multiple cards must all be numbers, and either all the same or a sum
            all_numbers = True
            valid_numbers = set()
            for card in self.current_selection:
                if not card.is_number_card():
                    all_numbers = False
                    break

                valid_numbers.add(card.card_type)

            return all_numbers and len(valid_numbers) == 1

    def action_card_selected(self):
        for card in self.current_selection:
            if not card.is_number_card():
                return True

        return False

    def check_for_dragon(self, player):
        for card in player.cards:
            if card.card_type == 'dragon':
                print('Dragon found when stealing')
                card.show_card(self.screen, card.card_file(self.resource_dir), self.bg_colour)

    def wake_queen(self, current_player):
        self.select_queens()
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    for queen in self.queen_cards:
                        if queen.is_clicked():
                            # mark the queen location as available
                            self.sleeping_queen_positions.append(queen.center)

                            # show the queen then move it to the next open queen slot
                            queen_file = queen.card_file(self.resource_dir)
                            queen.show_card(self.screen, queen_file, self.bg_colour)
                            queen.queen_awake = True
                            time.sleep(0.5)
                            player_index = self.players.index(current_player)
                            queen_destination = self.player_queen_positions[player_index][len(current_player.queens)]
                            self.move_card_to_destination(queen_file, queen.center, queen_destination)
                            queen.center = queen_destination
                            current_player.queens.append(queen)
                            pygame.display.flip()

                            return queen

    def perform_action(self):
        action_card = self.current_selection[0]
        current_player = self.players[self.player_turn]

        if action_card.card_type.startswith('king'):
            chosen_queen = self.wake_queen(current_player)

            if chosen_queen.card_type == 'rose':
                self.initialise_board()
                self.draw_center_card()
                self.show_player_cards()
                # rose queen lets you take another queen
                self.wake_queen(current_player)

        elif action_card.card_type == 'jester':
            # draw the next card and see if it is a number card
            self.replace_card(current_player, action_card, jester_card=True)

        elif action_card.card_type == 'knight':
            self.select_queens(asleep=False, exclude_player=current_player)
            pygame.display.flip()
            while True:
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONUP:
                        for player in self.players:
                            for queen in player.queens:
                                if queen.is_clicked():
                                    self.check_for_dragon(player)
                                    queen_file = queen.card_file(self.resource_dir)
                                    queen_destination = self.player_queen_positions[self.player_turn][len(current_player.queens)]
                                    current_player.queens.append(queen)
                                    player.queens.remove(queen)
                                    old_pos = queen.center
                                    queen.center = queen_destination
                                    queen.moving = True

                                    self.move_card_to_destination(queen_file, old_pos, queen_destination)
                                    queen.moving = False
                                    self.reorder_queens(player)
                                    self.initialise_board()
                                    pygame.display.flip()
                                    return

        elif action_card.card_type == 'dragon':
            # dragons don't do anything on their own
            pass
        elif action_card.card_type == 'potion':
            self.select_queens(asleep=False, exclude_player=current_player)
            pygame.display.flip()
            while True:
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONUP:
                        for player in self.players:
                            for queen in player.queens:
                                if queen.is_clicked():
                                    # show the queen then move it to the next open queen slot
                                    queen_file = queen.card_file(self.resource_dir)
                                    queen.queen_awake = False
                                    queen_destination = self.sleeping_queen_positions[0]
                                    player.queens.remove(queen)

                                    self.move_card_to_destination(queen_file, queen.center, queen_destination)
                                    queen.center = queen_destination

                                    self.sleeping_queen_positions.remove(queen.center)

                                    self.reorder_queens(player)
                                    self.initialise_board()
                                    pygame.display.flip()
                                    return
        elif action_card.card_type == 'wand':
            # wands don't do anything on their own
            pass

    def replace_card(self, current_player, old_card, jester_card=False):
        target_card = Card()
        target_card.card_type = self.full_deck[-1]
        target_card.center = self.screen_center

        if jester_card:
            red = (222, 0, 0)
            # check whether the next card is a number card
            if target_card.is_number_card():
                target_card.show_card(self.screen, target_card.card_file(self.resource_dir), self.bg_colour)
                pygame.display.flip()
                current_player_index = self.players.index(current_player)
                for i in range(current_player_index, current_player_index + int(target_card.card_type)):
                    previous_player = self.players[(i - 1) % len(self.players)]
                    chosen_player = self.players[i % len(self.players)]
                    self.draw_player_name(previous_player.name, self.players.index(previous_player))
                    self.draw_player_name(chosen_player.name, self.players.index(chosen_player), colour=red)
                    time.sleep(1)
                    pygame.display.flip()

                # the chosen player gets to choose a queen
                self.wake_queen(chosen_player)
        else:
            print('Replacing {} with {}'.format(old_card.card_type, target_card.card_type))
            self.full_deck.pop()
            self.discard_pile.append(old_card.card_type)
            target_card.center = old_card.center
            current_player.cards.remove(old_card)
            current_player.cards.append(target_card)

    def replace_cards(self):
        current_player = self.players[self.player_turn]
        num_cards = len(self.full_deck)
        if len(self.current_selection) > num_cards:
            print('Not enough cards left, reusing discard pile')
            shuffle(self.discard_pile)
            self.full_deck.extend(self.discard_pile)
            num_cards = len(self.full_deck)

        for i in range(len(self.current_selection)):
            old_card = self.current_selection[i]
            self.replace_card(current_player, old_card)

        assert len(current_player.cards) == self.cards_per_player, len(current_player.cards)
        assert len(self.full_deck) == num_cards - len(self.current_selection)
        self.current_selection = []

    def finalise_turn(self):
        self.hide_player_cards()
        self.deselect_queens()
        self.current_selection = []
        self.player_turn += 1
        self.player_turn %= len(self.player_names)
        self.turn_over = False

        current_player = self.players[self.player_turn]
        if len(current_player.queens) == 5:
            self.game_over = True

    def do_player_turn(self):
        self.center_stack = self.draw_center_card()
        self.show_player_cards()
        for event in pygame.event.get():
            if event.type == QUIT:
                self.hide_player_cards()
                return 1
            elif event.type == MOUSEBUTTONUP:
                if self.select_player_card():
                    pass
                elif self.is_center_card_selected():
                    if self.valid_move():
                        if self.action_card_selected():
                            self.perform_action()
                        self.replace_cards()

                        self.turn_over = True
                    else:
                        print('Not a valid move')
                        for card in self.current_selection:
                            print(card.card_type)

                else:
                    # self.select_queen()
                    pass

            if self.turn_over:
                self.finalise_turn()

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

        if board.do_player_turn() or board.game_over:
            return

        pygame.display.flip()


if __name__ == "__main__":
    enter_players()
    pygame.quit()
