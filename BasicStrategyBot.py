# BASIC STRATEGY BOT

import json
import pandas as pd
from collections import defaultdict



# Standard deck composition
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}


class Hand:
    def __init__(self, total=0, soft=False):
        self.total = total
        self.soft = soft

    def __str__(self):
        softness = "Soft" if self.soft else "Hard"
        return f"{softness} {self.total}"

    def copy(self):
        # Create a new Hand object with the same attributes
        new_hand = Hand(self.total, self.soft)
        return new_hand

    def add_card(self, rank):
        self.total += VALUES[rank]
        if rank == 'A':
            self.soft = True
        if self.total > 21 and self.soft:
            self.total -= 10
            self.soft = False



class BasicStrategyBot:
    def __init__(self):
        # Memorization for expensive calculations
        self.dealer_probabilities = {}
        self.stand_evs = {}
        self.hit_evs = {}
        try:
            with open('basic_strategy_chart.json', 'r') as f:
                json_data = json.load(f)
                self.decision_chart = {}
                for keystring, decisionArray in json_data.items():
                    key = eval(keystring)
                    self.decision_chart[key] = decisionArray
                for (player_hand, dealer_hand), decisionArray in  self.decision_chart.items():
                    self.hit_evs[player_hand, dealer_hand] = decisionArray[1]
                    self.stand_evs[player_hand, dealer_hand] = decisionArray[2]
                print("SUCCESSFULLY LOADED JSON")
        except:
            self.stand_evs = {}
            self.hit_evs = {}
            self.decisionchart = {}

    def dealer_outcomes(self, dealer_hand):
        # Check cache
        if str(dealer_hand) in self.dealer_probabilities:
            return self.dealer_probabilities[str(dealer_hand)]

        # Calculate if not in cache
        def calc_outcomes(self, dealer_hand):
            # Dealer busts
            if dealer_hand.total > 21:
                return{"bust": 1.0}
            
            # Dealer stands
            if dealer_hand.total >= 17:
                return {dealer_hand.total: 1.0}
            
            # Dealer must hit
            outcomes = defaultdict(float) # Initialize outcomes dictionary
            for rank in RANKS:
                # Create a new hand
                new_hand = dealer_hand.copy()
                probability = 1/13 # Basic strategy assumes no change in probability (No card-counting)
                new_hand.add_card(rank)
                suboutcomes = calc_outcomes(self, new_hand)
                for outcome, prob in suboutcomes.items():
                    outcomes[outcome] += probability*prob

            return dict(outcomes)
    
        result = calc_outcomes(self, dealer_hand)
        self.dealer_probabilities[dealer_hand] = result
        return result
    


    def stand_expected_value(self, player_hand, dealer_hand):
        # Check cache
        if (str(player_hand), str(dealer_hand)) in self.stand_evs:
            return self.stand_evs[(str(player_hand), str(dealer_hand))]
        
        # If not in cache
        else:
            player_value = player_hand.total
            dealer_probs = self.dealer_outcomes(dealer_hand)

            ev = 0.0

            for dealer_outcome, probability in dealer_probs.items():
                if dealer_outcome == "bust":
                    ev += probability * 1.0 # Player wins
                else:
                    if player_value > dealer_outcome: 
                        ev += probability * 1.0 # Player wins
                    elif dealer_outcome > player_value:
                        ev += probability * -1.0 # Dealer wins
                    else:
                        ev += probability * 0.0 # Push
            self.stand_evs[(str(player_hand), str(dealer_hand))] = ev
            return ev
    

    def hit_expected_value(self, player_hand, dealer_hand):
        # Check cache
        if (str(player_hand), str(dealer_hand)) in self.hit_evs:
            return self.hit_evs[(str(player_hand), str(dealer_hand))]
        
        # Not in cache
        else:
            ev = 0.0
            for rank in RANKS: # For every possible hit option
                new_hand = player_hand.copy()
                new_hand.add_card(rank)
                probability = 1/13

                if new_hand.total > 21: # Player busts
                    ev += probability * -1.0

                else:
                    decision, hit_ev, stand_ev = self.analyse(new_hand, dealer_hand)
                    optimal_ev = max(hit_ev, stand_ev)
                    ev += probability * optimal_ev
            self.hit_evs[(str(player_hand), str(dealer_hand))] = ev
            return ev



    def analyse(self, player_hand, dealer_hand):
        if player_hand.total > 21:
            return "bust", -1.0, -1.0
        
        stand_ev = self.stand_expected_value(player_hand, dealer_hand)
        hit_ev = self.hit_expected_value(player_hand, dealer_hand)
        
        if hit_ev > stand_ev:
            return 'hit', hit_ev, stand_ev
        else:
            return 'stand', hit_ev, stand_ev
        

    def create_json(self):

        print("CREATING JSON")

        decision_chart = {}

        # HARD HAND CHART
        for player_total in range(4, 22): # For every possible soft hand from 4 to 21
            player_hand = Hand(player_total, soft=False)
            for dealer_rank in RANKS:
                dealer_hand = Hand(VALUES[dealer_rank], soft = True if dealer_rank == 'A' else False) # Dealer hand can be soft or hard
                decision, hit_ev, stand_ev = self.analyse(player_hand, dealer_hand)
                decision_chart[(str(player_hand), str(dealer_hand))] = [decision, hit_ev, stand_ev]
        
        # SOFT HAND CHART
        for player_total in range(12, 22): # For every possible soft hand from A,A to A,10
            player_hand = Hand(player_total, soft=True)
            for dealer_rank in RANKS:
                dealer_hand = Hand(VALUES[dealer_rank], soft = True if dealer_rank == 'A' else False) # Dealer hand can be soft or hard
                decision, hit_ev, stand_ev = self.analyse(player_hand, dealer_hand)
                decision_chart[(str(player_hand), str(dealer_hand))] = [decision, hit_ev, stand_ev]

        json_chart = {}
        for key, value in decision_chart.items():
            # A tuple of Hand objects, e.g., (player_hand, dealer_hand), cannot be dumped. We must convert it to a string.
            json_chart[str(key)] = value
        

        with open('basic_strategy_chart.json', 'w') as f:
            json.dump(json_chart, f, indent=4)



    def display_chart(self):
        """
        Displays the decision chart in a spreadsheet-like format using pandas.
        """
        if not self.decision_chart:
            print("Decision chart is empty. Please run create_json() first.")
            return

        # Separate hard and soft hands
        hard_hands = {}
        soft_hands = {}

        for (player_hand_str, dealer_hand_str), decisionArray in self.decision_chart.items():
            player_hand_type = player_hand_str.split()[0]
            if player_hand_type == 'Hard':
                hard_hands[(player_hand_str, dealer_hand_str)] = decisionArray
            else:
                soft_hands[(player_hand_str, dealer_hand_str)] = decisionArray

        # Display Hard Hands
        print("\n--- Hard Hands Chart ---")
        df_hard = self._create_dataframe(hard_hands)
        print(df_hard)
        print("\n" + "-"*30)

        # Display Soft Hands
        print("\n--- Soft Hands Chart ---")
        df_soft = self._create_dataframe(soft_hands)
        print(df_soft)
        print("\n" + "-"*30)

    def _create_dataframe(self, data):
        """
        Helper method to create a pandas DataFrame from the data.
        """
        player_totals = sorted(list(set(key[0] for key in data.keys())),
                                    key=lambda x: -1*(int(x.split()[-1])))
        
        dealer_upcards = sorted(list(set(key[1] for key in data.keys())), 
                                key=lambda x: (int(x.split()[-1])))
        
        # Create a DataFrame to hold the decisions
        df = pd.DataFrame(index=player_totals, columns=dealer_upcards)

        for (player_hand_str, dealer_hand_str), value in data.items():
            decision = value[0]
            df.loc[player_hand_str, dealer_hand_str] = decision
        
        return df

def main():
    print("BASIC STRATEGY BOT")
    calc = BasicStrategyBot()
    
    # You need to call create_json() at least once to generate the file
    # before you can display the chart.
    calc.create_json() 

    # Now you can display the chart from the loaded JSON
    calc.display_chart()




if __name__ == "__main__":
    main()