"""
Clue randomization system for Rattlesnake Ridge murder mystery game.
Handles random killer selection, motive assignment, and clue distribution.
"""

import random
import yaml
from typing import Dict, List, Any
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class MurderScenario:
    """Contains the truth about the murder and distributed clues"""
    killer: str
    motive: str
    clue_distribution: Dict[str, List[str]]

    def is_correct_guess(self, guess: str) -> bool:
        """Check if player's guess matches the actual killer"""
        return guess.lower() == self.killer.lower()


class ClueRandomizer:
    """Handles randomization of killer, motive, and clue distribution"""

    def __init__(self, clue_bank_path: str = "server/data/clue_bank.yaml"):
        """Load the clue bank from YAML file"""
        with open(clue_bank_path, 'r') as file:
            data = yaml.safe_load(file)

        self.clue_bank = {
            'clara': data['clara'],
            'flint': data['flint'],
            'whistle': data['whistle'],
            'billy': data['billy']
        }
        self.available_motives = data['motives']
        self.character_names = ['Whistle', 'Clara', 'Flint', 'Billy']

    def generate_scenario(self) -> MurderScenario:
        """Generate a random murder scenario with distributed clues"""
        # Pick random killer and motive
        killer = random.choice(self.character_names)
        motive = random.choice(self.available_motives)

        # Distribute clues based on killer and motive
        clue_distribution = self._distribute_clues(killer, motive)

        return MurderScenario(
            killer=killer,
            motive=motive,
            clue_distribution=clue_distribution
        )

    def _distribute_clues(self, killer: str, motive: str) -> Dict[str, List[str]]:
        """
        Distribute clues to each character based on the killer and motive.
        Ensures logical consistency and solvability.
        """
        distribution = {}
        has_strong_clue = False

        for character_name in self.character_names:
            # Get the character's clue bank (lowercase for yaml keys)
            char_bank = self.clue_bank.get(character_name.lower(), [])

            # Filter clues that work for this killer/motive combination
            valid_clues = []
            for clue in char_bank:
                # Check if clue supports this killer
                killer_match = (
                    killer in clue.get('supports_killer', []) or
                    'any' in clue.get('supports_killer', []) or
                    (character_name == killer and not clue.get('supports_killer'))  # Red herrings
                )

                # Check if clue supports this motive
                motive_match = (
                    motive in clue.get('supports_motive', []) or
                    'any' in clue.get('supports_motive', []) or
                    not clue.get('supports_motive')  # Red herrings
                )

                # Don't let characters incriminate themselves directly
                not_self_incriminating = (
                    character_name != killer or
                    character_name not in clue.get('supports_killer', [])
                )

                if killer_match and motive_match and not_self_incriminating:
                    valid_clues.append(clue)

            # Select 2-3 clues for this character
            num_clues = min(max(len(valid_clues), 2), 3)

            # Ensure at least one strong clue exists somewhere
            if not has_strong_clue and valid_clues:
                strong_clues = [c for c in valid_clues if c.get('strength') == 'strong']
                if strong_clues:
                    selected = [random.choice(strong_clues)]
                    has_strong_clue = True
                    # Add more clues
                    remaining = [c for c in valid_clues if c not in selected]
                    if remaining:
                        selected.extend(random.sample(
                            remaining,
                            min(num_clues - 1, len(remaining))
                        ))
                else:
                    selected = random.sample(valid_clues, min(num_clues, len(valid_clues)))
            else:
                selected = random.sample(valid_clues, min(num_clues, len(valid_clues))) if valid_clues else []

            # Format the clue text with the actual killer's name
            formatted_clues = []
            for clue in selected:
                text = clue['text'].replace('{killer}', killer)
                formatted_clues.append(text)

            # Add some red herrings if needed
            if len(formatted_clues) < 2:
                red_herrings = [c for c in char_bank if not c.get('supports_killer')]
                for rh in red_herrings[:2-len(formatted_clues)]:
                    formatted_clues.append(rh['text'])

            distribution[character_name] = formatted_clues

        # Ensure solvability - if no strong clue was added, force one
        if not has_strong_clue:
            self._ensure_solvability(distribution, killer, motive)

        return distribution

    def _ensure_solvability(self, distribution: Dict[str, List[str]], killer: str, motive: str):
        """
        Ensure the mystery is solvable by adding a crucial clue if needed.
        """
        # Pick a random non-killer character to have seen something
        witnesses = [name for name in self.character_names if name != killer]
        witness = random.choice(witnesses)

        # Add a direct observation
        crucial_clue = f"I saw {killer} near the mine around the time of the murder"
        if witness in distribution:
            distribution[witness].append(crucial_clue)
        else:
            distribution[witness] = [crucial_clue]


def inject_scenario_into_agents(agents: List[Any], scenario: MurderScenario, prompts: dict):
    """
    Inject the murder scenario into agent prompts and knowledge.
    Modifies agents in-place to include their clues and guilty/innocent status.
    """
    #took this out for now
    return scenario
