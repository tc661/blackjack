import random
import pygame

# ---INITIALIZING PYGAME---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Blackjack")
font = pygame.font.Font("C:\\Windows\\Fonts\\seguisym.ttf", 36)



# ---GLOBAL VARIABLES---
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
          '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
suit_symbols = {
    'Hearts': '♥',
    'Diamonds': '♦',
    'Clubs': '♣',
    'Spades': '♠'
}


# ---CLASSES FOR BLACKJACK---
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = values[rank]

    def __str__(self):
        return f"{self.rank}{suit_symbols[self.suit]}"

class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()
    
    def reset(self):
        self.__init__()

class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        self.cards.append(card)

    def score(self):
        total = sum(card.value for card in self.cards)
        # Adjust for Aces
        aces = sum(1 for card in self.cards if card.rank == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.player_turn = True
        self.game_over = False
        self.waiting_to_continue = False
        self.reshuffle_message = ""
        self.reshuffle_timer = 0
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.reset_round()
    
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
        self.draw()

        # Deal new cards with delay
        pygame.time.wait(300)
        for _ in range(2):
            self.player_hand.add_card(self.deck.deal())
            self.draw()
            pygame.time.wait(300)

            self.dealer_hand.add_card(self.deck.deal())
            self.draw()
            pygame.time.wait(300)

    # Dealer's play logic
    def dealer_play(self):
        self.draw()
        pygame.time.wait(300)
        while self.dealer_hand.score() < 17:
            self.dealer_hand.add_card(self.deck.deal())
            self.draw()
            pygame.time.wait(300)
        self.game_over = True


    # Draw the game state
    def draw(self):
        self.WIDTH, self.HEIGHT = screen.get_size()
        screen.fill((0, 128, 0)) # Green background for Blackjack

        # Draw player hand
        draw_text("Player:",50, self.HEIGHT * 3 // 4)
        x_offset = 200
        for card in self.player_hand.cards:
            draw_text(str(card), x_offset, self.HEIGHT * 3 // 4, get_colour(card))
            x_offset += 80

        # Draw dealer hand
        draw_text("Dealer:", 50, self.HEIGHT // 4)
        x_offset = 200
        # Show dealer's cards based on player's turn
        if not self.player_turn:
            visible_cards = self.dealer_hand.cards
        elif self.dealer_hand.cards:
            visible_cards = [self.dealer_hand.cards[0]]
        else:
            visible_cards = []

        for card in visible_cards:
            draw_text(str(card), x_offset, self.HEIGHT // 4, get_colour(card))
            x_offset += 80
        if self.player_turn and len(self.dealer_hand.cards) > 1:
            draw_text("[?]", x_offset, self.HEIGHT // 4)

        # Draw scores
        if not self.player_turn:
            draw_text(f"{self.dealer_hand.score()}", self.WIDTH-150, self.HEIGHT // 4)
        else:
            draw_text("?", self.WIDTH-150, self.HEIGHT // 4)
        draw_text(f"{self.player_hand.score()}", self.WIDTH-150, self.HEIGHT * 3 // 4)

        # Draw deck size
        draw_text(f"Deck: {len(self.deck.cards)}", self.WIDTH-200, self.HEIGHT // 8)

        # Results (Game Over)
        if self.game_over:
            result = ""
            if self.player_hand.score() > 21:
                result = "Player Busts!"
            elif self.dealer_hand.score() > 21 or self.player_hand.score() > self.dealer_hand.score():
                result = "Player Wins!"
            elif self.player_hand.score() < self.dealer_hand.score():
                result = "Dealer Wins!"
            else:
                result = "Push!"
            draw_text(result, (self.WIDTH//2 - 100), (self.HEIGHT // 2 - 50))
            draw_text("Press Enter to continue...", (self.WIDTH//2 - 100), (self.HEIGHT // 2 + 50))
        pygame.display.flip()


    def show_reshuffle_screen(self):
        screen.fill((0, 128, 0))
        self.WIDTH, self.HEIGHT = screen.get_size()
        draw_text("Reshuffling...", self.WIDTH // 2 - 100, self.HEIGHT // 2)
        pygame.display.flip()
        pygame.time.wait(1000)



# ---UTILITY FUNCTIONS---
# Draw text on the screen
def draw_text(text, x, y, color=(255, 255, 255)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Get the color of the card for display
def get_colour(card):
    if card.suit in ['Hearts', 'Diamonds']:
        return (255, 0, 0)
    else:
        return (0, 0, 0)

# Show the main menu
def show_menu():
    while True:
        WIDTH, HEIGHT = screen.get_size()
        screen.fill((0, 128, 0))
        draw_text("Blackjack", WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text("Press Enter to Play", WIDTH // 2 - 150, HEIGHT // 2)
        draw_text("Press Q to Quit", WIDTH // 2 - 150, HEIGHT // 2 + 50)
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

                # Reset round
                elif game.waiting_to_continue:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        game.reset_round()

                # Player's turn
                elif game.player_turn and not game.game_over:
                    if event.type == pygame.KEYDOWN:
                        # Hit
                        if event.key == pygame.K_h:
                            game.player_hand.add_card(game.deck.deal())
                            # Check if player busts
                            if game.player_hand.score() > 21:
                                game.player_turn = False
                                game.game_over = True
                        # Stand
                        elif event.key == pygame.K_s:
                            game.player_turn = False

            # Dealer's turn
            if not game.player_turn and not game.game_over:
                game.dealer_play()
                game.waiting_to_continue = True
            
            # Game over
            if game.game_over:
                game.waiting_to_continue = True

            game.draw()
    
    pygame.quit()

if __name__ == "__main__":
    main()