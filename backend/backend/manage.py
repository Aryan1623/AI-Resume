#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


    class Pokemon:
        def __init__(self, name, type):
            self.name = name
            self.type = type
            
        def attack(self):
            return f"{self.name} attacks!"

    class Pikachu(Pokemon):
        def __init__(self, name="Pikachu"):
            super().__init__(name, "Electric")
            
        def thunderbolt(self):
            return f"{self.name} uses Thunderbolt!"

    # Example usage
    pikachu = Pikachu()
    print(pikachu.attack())  # Prints: Pikachu attacks!
    print(pikachu.thunderbolt())  # Prints: Pikachu uses Thunderbolt!

