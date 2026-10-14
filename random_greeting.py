"""Print a random greeting phrase."""

import random

GREETINGS = [
    "Ahoj! Jak se máš?",
    "Čau! Co je nového?",
    "Dobré ráno! Krásný den, že?",
    "Dobrý den, vítám tě!",
    "Nazdar! Dáváš si kávu?",
    "Hello there! What are you working on?",
    "Hi! Long time no see.",
    "Hey! How's it going?",
    "Hola! ¿Cómo estás?",
    "Salut! Comment ça va?",
]


def main() -> None:
    print(random.choice(GREETINGS))


if __name__ == "__main__":
    main()
