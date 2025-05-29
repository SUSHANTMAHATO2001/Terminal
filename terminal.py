import os
import subprocess
import shlex
import readline
import re

# Enable tab completion and command history
readline.parse_and_bind('tab: complete')

def complete(text, state):
    line = readline.get_line_buffer().split()
    if not line:
        return None
    last_token = line[-1]
    try:
        matches = [f for f in os.listdir('.') if f.startswith(last_token)]
    except FileNotFoundError:
        matches = []
    try:
        return matches[state]
    except IndexError:
        return None

readline.set_completer(complete)

def expand_variables(command, variables):
    def replacer(match):
        var_name = match.group(1) or match.group(2)
        if var_name in variables:
            return variables[var_name]
        return os.environ.get(var_name, '')
    pattern = re.compile(r'\$(\w+)|\$\{([^}]+)\}')
    return pattern.sub(replacer, command)

def execute_command(command_input):
    try:
        subprocess.run(command_input, shell=True)
    except Exception as e:
        print(f"Execution error: {e}")

def mahato_terminal():
    username = "mahato"
    hostname = os.uname().nodename
    home = os.path.expanduser("~")

    variables = {}

    print(f"\033[1;36mWelcome to Mahato Terminal — A Powerful Linux-like Shell\033[0m")
    print("Type 'help' to see built-in commands.\n")

    while True:
        try:
            cwd = os.getcwd().replace(home, "~")

            # Colors for prompt parts
            cyan = "\033[1;36m"
            green = "\033[1;32m"
            yellow = "\033[1;33m"
            blue = "\033[1;34m"
            reset = "\033[0m"

            prompt = (
                f"{cyan}┌──({green}{username}{reset}{cyan}㉿{yellow}{hostname}{cyan})-[{blue}{cwd}{cyan}]{reset} "
            )

            command_input = input(prompt).strip()

            if not command_input:
                continue

            # Handle variable assignment: set VAR=value
            if command_input.startswith("set "):
                parts = command_input[4:].split('=', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    var_value = parts[1].strip()
                    variables[var_name] = var_value
                    print(f"Set variable {var_name} = {var_value}")
                else:
                    print("Usage: set VAR=value")
                continue

            # Expand variables in command input
            command_input = expand_variables(command_input, variables)

            # Built-in commands
            if command_input == "exit":
                print("Exiting Mahato Terminal.")
                break
            elif command_input == "history":
                length = readline.get_current_history_length()
                for i in range(1, length + 1):
                    print(f"{i}  {readline.get_history_item(i)}")
            elif command_input.startswith("cd"):
                parts = shlex.split(command_input)
                if len(parts) > 1:
                    try:
                        os.chdir(os.path.expanduser(parts[1]))
                    except FileNotFoundError:
                        print(f"No such directory: {parts[1]}")
                else:
                    os.chdir(home)
            elif command_input == "clear":
                os.system("clear")
            elif command_input == "help":
                print(f"""
{yellow}Mahato Terminal Commands:{reset}
  cd [dir]        Change directory
  clear           Clear the screen
  exit            Exit the terminal
  help            Show this help menu
  set VAR=value   Set a custom environment variable
  history         Show command history

Supports Linux features:
  - Command chaining: command1 && command2 || command3
  - Pipes: ls | grep py
  - Redirection: >, >>, <
  - Command history with arrow keys
  - Tab completion for files and directories
  - All Linux/Termux commands supported
                """)
            else:
                execute_command(command_input)

        except KeyboardInterrupt:
            print("\n(Use 'exit' to quit Mahato Terminal)")
        except EOFError:
            print("\nExiting Mahato Terminal.")
            break
        except Exception as e:
            print(f"Shell Error: {e}")

if __name__ == "__main__":
    mahato_terminal()
