from colorama import init, Fore, Style

# Ініціалізація Colorama
init(autoreset=True)

# Функція для красивого виводу
def print_colored(message, level="info"):
    colors = {
        "info": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "critical": Fore.RED + Style.BRIGHT
    }

    color = colors.get(level, Fore.WHITE)
    print(color + message)


# Функція для виведення кольорового тексту перед input
def colored_input(prompt, color=Fore.WHITE):
    print(color + prompt, end="")
    return input()







