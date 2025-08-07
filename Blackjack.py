import random
import pygame
import math

# ---INITIALIZING PYGAME---
pygame.init()
WIDTH, HEIGHT = 800, 600
CARD_WIDTH, CARD_HEIGHT = 60, 87
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Blackjack")
big_font = pygame.font.Font("C:\\Windows\\Fonts\\seguisym.ttf", 36)
small_font = pygame.font.Font("C:\\Windows\\Fonts\\seguisym.ttf", 24)



# ---GLOBAL VARIABLES---
suits = ['hearts', 'diamonds', 'clubs', 'spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
          '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
suit_symbols = {
    'hearts': '♥',
    'diamonds': '♦',
    'clubs': '♣',
    'spades': '♠'
}


# ---ANIMATION---
ANIMATION_SPEED = 0.8
FLIP_SPEED = 0.2

# ---CLASSES FOR BLACKJACK---
class Card:
    def __init__(self, suit, rank, visible=True):
        self.suit = suit
        self.rank = rank
        self.value = values[rank]
        self.visible = visible
        self.image = self.load_image()
        self.back_image = pygame.transform.scale(pygame.image.load("Playing-Cards/back.png"), (CARD_WIDTH, CARD_HEIGHT))

        # Animation properties
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.animating = False
        self.flip_progress = 0.0
        self.flipping = False

    def __str__(self):
        return f"{self.rank}{suit_symbols[self.suit]}"
    
    def load_image(self):
        name_map = {'J': 'jack', 'Q': 'queen', 'K': 'king', 'A': 'ace'}
        rank_str = name_map.get(self.rank, self.rank)
        filename = f"{rank_str}_of_{self.suit}.png"
        path = f"Playing-Cards/{filename}"
        try:
            image = pygame.image.load(path)
            return pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
        except pygame.error:
            print(f"Error loading image: {path}")
            return None
        
    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y

    def animate_to(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y
        self.animating = True
    
    def flip(self):
        if not self.visible:
            self.flipping = True
            self.visible = True

    def update(self):
        # Update position animation state
        if self.animating:
            dx = self.target_x - self.x
            dy = self.target_y - self.y

            if abs(dx) < 1 and abs(dy) < 1:
                self.x = self.target_x
                self.y = self.target_y
                self.animating = False
            else:
                self.x += dx * 0.15
                self.y += dy * 0.15
        
        # Update flip animation state
        if self.flipping:
            self.flip_progress += FLIP_SPEED
            if self.flip_progress >= 1.0:
                self.flip_progress = 1.0
                self.flipping = False
        
    def draw(self, surface, x, y):
        # If flipping
        if self.flipping:
            # Scale the card image based on flip progress
            scale_x = abs(math.cos(self.flip_progress * math.pi)) 
            if self.flip_progress < 0.5:
                # Back side
                scaled_image = pygame.transform.scale(self.back_image, (int(CARD_WIDTH * scale_x), CARD_HEIGHT))
            else:
                # Front side
                scaled_image = pygame.transform.scale(self.image, (int(CARD_WIDTH * scale_x), CARD_HEIGHT))
            
            # Centre the card image
            offset_x = (CARD_WIDTH - scaled_image.get_width()) // 2
            surface.blit(scaled_image, (x + offset_x, y))
        # If not flipping
        else:
            image = self.image if self.visible else self.back_image
            surface.blit(image, (x, y))



class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.cards)
        self.x = 50
        self.y = 50
    

    def deal(self, visible=True):
        card = self.cards.pop()
        card.visible = visible
        card.set_position(self.x, self.y) # Starts at deck position
        return card
    
    def reset(self):
        self.__init__()

    def draw(self, surface):
        # Draw the deck at its position
        if len(self.cards) > 0:
            # Draw the stacked deck
            for i in range(min(3, len(self.cards))):
                offset = i*2
                surface.blit(self.cards[0].back_image, (self.x + offset, self.y + offset))
            
            # Draw the deck count
            draw_text(f"{len(self.cards)}", self.x + CARD_WIDTH + 25, self.y + 50, font=small_font, color=(255, 255, 255))

class Hand:
    def __init__(self):
        self.cards = []
        self.x = 0
        self.y = 0
    
    def add_card(self, card):
        self.cards.append(card)
        self.update_positions()

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.update_positions()
    
    def update_positions(self):
        card_spacing = 80
        start_x = self.x - (len(self.cards) - 1) * card_spacing // 2

        # Update the position of each card in the hand
        for i, card in enumerate(self.cards):
            target_x = start_x + i * card_spacing
            if card.x == 0 and card.y == 0: # New card
                card.set_position(card.x, card.y) # Animate from deck
            card.animate_to(target_x, self.y)

    def score(self):
        total = sum(card.value for card in self.cards)
        # Adjust for Aces
        aces = sum(1 for card in self.cards if card.rank == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total
    
    def update(self):
        # Update each card's position animation
        for card in self.cards:
            card.update()
    
    def draw(self, surface):
        for card in self.cards:
            card.draw(surface, card.x, card.y)




class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.player_turn = True
        self.game_over = False
        self.waiting_to_continue = False
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.dealer_started = False
        self.setup_positions()
        self.reset_round()

    def setup_positions(self):
        self.WIDTH, self.HEIGHT = screen.get_size()
    
        # Dealer hand position
        dealer_x = self.WIDTH // 2
        dealer_y = 100
        self.dealer_hand.set_position(dealer_x, dealer_y)

        # Player hand position
        player_x = self.WIDTH // 2
        player_y = self.HEIGHT - 150
        self.player_hand.set_position(player_x, player_y)

        # Deck position
        self.deck.x = 50
        self.deck.y = 50
    
    # Reset the table for a new round
    def reset_round(self):
        # Reset the game state for a new round
        # If the deck has less than 26 cards, reshuffle
        if len(self.deck.cards) < 26:
            self.deck.reset()
            self.show_reshuffle_screen()
        
        self.player_hand.cards.clear()
        self.dealer_hand.cards.clear()
        
        self.player_turn = True
        self.game_over = False
        self.waiting_to_continue = False
        self.dealer_started = False
        self.setup_positions()

        # Start the round by dealing cards
        self.deal_initial_cards()

    def deal_initial_cards(self):
        # Deal new cards with animation delay
        pygame.time.set_timer(pygame.USEREVENT+1, 500)  # Player Card 1
        pygame.time.set_timer(pygame.USEREVENT+2, 1000)  # Dealer Card 1
        pygame.time.set_timer(pygame.USEREVENT+3, 1500)  # Player Card 2
        pygame.time.set_timer(pygame.USEREVENT+4, 2000)  # Dealer Card 2

    def handle_deal_event(self, event):
        if event.type == pygame.USEREVENT+1:  # Player Card 1
            card = self.deck.deal(visible=True)
            self.player_hand.add_card(card)
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancel timer

        elif event.type == pygame.USEREVENT+2:  # Dealer Card 1
            card = self.deck.deal(visible=True)
            self.dealer_hand.add_card(card)
            pygame.time.set_timer(pygame.USEREVENT + 2, 0)
    
        elif event.type == pygame.USEREVENT+3:  # Player Card 2
            card = self.deck.deal(visible=True)
            self.player_hand.add_card(card)
            pygame.time.set_timer(pygame.USEREVENT + 3, 0)

        elif event.type == pygame.USEREVENT+4:  # Dealer Card 2 (hidden)
            card = self.deck.deal(visible=False)
            self.dealer_hand.add_card(card)
            pygame.time.set_timer(pygame.USEREVENT + 4, 0)


    # Dealer's play logic
    def dealer_play(self):
        # Flip the dealer's second card
        if len(self.dealer_hand.cards) > 1:
            print("Dealer flipping")
            self.dealer_hand.cards[1].flip()
        
        print("Queuing dealer hit")
        # Deal additional cards as needed
        pygame.time.set_timer(pygame.USEREVENT + 5, 1000)  # Start dealer hitting
    
    def dealer_hit(self):
        print("Dealer hitting")
        if self.dealer_hand.score() < 17:
            card = self.deck.deal(visible=True)
            self.dealer_hand.add_card(card)
            pygame.time.set_timer(pygame.USEREVENT + 5, 1000)  # Continue hitting
        else:
            self.game_over = True
            self.waiting_to_continue = True
            pygame.time.set_timer(pygame.USEREVENT + 5, 0)  # Stop hitting



    # Draw the game state
    def draw(self):
        self.WIDTH, self.HEIGHT = screen.get_size()
        screen.fill((0, 100, 0)) # Green background for Blackjack

        # Update positions if window resized
        self.setup_positions()
        
        # Update animations
        self.player_hand.update()
        self.dealer_hand.update()

        # Draw the deck
        self.deck.draw(screen)

        # Draw hands
        self.player_hand.draw(screen)
        self.dealer_hand.draw(screen)
    
        # Draw labels
        dealer_label_x = self.WIDTH // 2
        dealer_label_y = 50
        draw_text("Dealer", dealer_label_x, dealer_label_y)

        player_label_x = self.WIDTH // 2
        player_label_y = self.HEIGHT - 200
        draw_text("Player", player_label_x, player_label_y)

        # Draw scores
        if not self.player_turn or self.game_over:
            dealer_score = self.dealer_hand.score()
            draw_text(f"Score: {dealer_score}", self.WIDTH // 2 + 150, 50)
        else:
            draw_text("Score: ?", self.WIDTH // 2 + 150, 50)    
        
        player_score = self.player_hand.score()
        draw_text(f"Score: {player_score}", self.WIDTH // 2 + 150, self.HEIGHT - 200)

        # Draw controls
        if self.player_turn and not self.game_over:
            draw_text("H - Hit | S - Stand", 100, self.HEIGHT - 50, font=small_font)

        # Results (Game Over)
        if self.game_over and not any(card.flipping for card in self.player_hand.cards + self.dealer_hand.cards):
            result = ""
            if self.player_hand.score() > 21:
                result = "Player Busts!"
            elif self.dealer_hand.score() > 21 or self.player_hand.score() > self.dealer_hand.score():
                result = "Player Wins!"
            elif self.player_hand.score() < self.dealer_hand.score():
                result = "Dealer Wins!"
            else:
                result = "Push!"
        
            # Draw results
            result_width = max(len(result) * 20, 240)
            
            result_rect = pygame.Rect(self.WIDTH // 2 - result_width // 2 - 20, self.HEIGHT // 2 - 60, 
                                    result_width + 40, 120)
            pygame.draw.rect(screen, (0, 0, 0, 128), result_rect)
            pygame.draw.rect(screen, (255, 255, 255), result_rect, 3)

            draw_text(result, self.WIDTH // 2, self.HEIGHT // 2 - 25, color=(255, 255, 0))
            draw_text("Press Enter to Continue...", self.WIDTH // 2, self.HEIGHT // 2 + 25, font=small_font)
    
        pygame.display.flip()

    def show_reshuffle_screen(self):
        screen.fill((0, 108, 0))
        self.WIDTH, self.HEIGHT = screen.get_size()
        draw_text("Reshuffling...", self.WIDTH // 2, self.HEIGHT // 2)
        pygame.display.flip()
        pygame.time.wait(1500)



# ---UTILITY FUNCTIONS---
# Draw text on the screen
# Draw text on the screen
def draw_text(text, x, y, color=(255, 255, 255), font=big_font):
    img = font.render(text, True, color)
    rect = img.get_rect(center =(x, y))
    screen.blit(img, rect)

"""
# Get the color of the card for display
def get_colour(card):
    if card.suit in ['hearts', 'diamonds']:
        return (255, 0, 0)
    else:
        return (0, 0, 0)
"""

# Show the main menu
def show_menu():
    while True:
        WIDTH, HEIGHT = screen.get_size()
        screen.fill((0, 100, 0))

        menu_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
        pygame.draw.rect(screen, (0, 0, 0, 100), menu_rect)
        pygame.draw.rect(screen, (255, 255, 255), menu_rect, 3)

        draw_text("BLACKJACK", WIDTH // 2, HEIGHT // 2 - 50)
        draw_text("Press Enter to Play", WIDTH // 2, HEIGHT // 2, font=small_font)
        draw_text("Press Q to Quit", WIDTH // 2, HEIGHT // 2 + 25, font=small_font)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True, "playing"
                elif event.key == pygame.K_q:
                    return False, "quit"


# ---MAIN GAME LOOP---
def main():
    clock = pygame.time.Clock()
    state = "menu"
    running = True
    game = None
    
    while running:
        if state == "menu":
            running, state = show_menu()
        
        elif state == "playing":
            if game is None:
                game = BlackjackGame()
        
            for event in pygame.event.get():
                # Quit event
                if event.type == pygame.QUIT:
                    running = False
                
                # Card dealing events
                elif event.type >= pygame.USEREVENT + 1 and event.type <= pygame.USEREVENT + 5:
                    if event.type == pygame.USEREVENT + 5:
                        game.dealer_hit()
                    else:
                        print(f"Handling deal event: {event.type}")
                        game.handle_deal_event(event)

                # Reset round
                elif game.waiting_to_continue:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        game.reset_round()
                        game.waiting_to_continue = False

                # Player's turn
                elif game.player_turn and not game.game_over:
                    if event.type == pygame.KEYDOWN:
                        # Hit
                        if event.key == pygame.K_h:
                            card = game.deck.deal(visible=True)
                            game.player_hand.add_card(card)
                            # Check if player busts
                            if game.player_hand.score() > 21:
                                game.player_turn = False
                                game.game_over = True
                                game.waiting_to_continue = True
                        # Stand
                        elif event.key == pygame.K_s:
                            game.player_turn = False

            # Dealer's turn
            if not game.player_turn and not game.game_over and not game.waiting_to_continue and not game.dealer_started:
                game.dealer_play()
                game.dealer_started = True

            game.draw()
            clock.tick(60) # Limit to 60 FPS
    
    pygame.quit()

if __name__ == "__main__":
    main()