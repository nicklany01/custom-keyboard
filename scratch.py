import re

content = open('/home/nick/Code/chirality/config/boards/shields/chirality/chirality.keymap').read()

aliases = {
    "NUMBER_1": "N1", "NUMBER_2": "N2", "NUMBER_3": "N3", "NUMBER_4": "N4",
    "NUMBER_5": "N5", "NUMBER_6": "N6", "NUMBER_7": "N7", "NUMBER_8": "N8",
    "NUMBER_9": "N9", "NUMBER_0": "N0",
    "BACKSLASH": "BSLH", "UNDERSCORE": "UNDER",
    "LEFT_PARENTHESIS": "LPAR", "RIGHT_PARENTHESIS": "RPAR",
    "LEFT_BRACE": "LBRC", "RIGHT_BRACE": "RBRC",
    "DOUBLE_QUOTES": "DQT", "LESS_THAN": "LT", "GREATER_THAN": "GT",
    "LEFT_BRACKET": "LBKT", "RIGHT_BRACKET": "RBKT",
    "DOWN_ARROW": "DOWN", "UP_ARROW": "UP",
    "BACKSPACE": "BSPC", "PAGE_DOWN": "PG_DN", "PAGE_UP": "PG_UP",
    "K_CONTEXT_MENU": "K_CMENU", "SEMICOLON": "SEMI",
    "LEFT_SHIFT": "LSHFT", "RIGHT_SHIFT": "RSHFT",
    "LEFT_META": "LMETA", "RIGHT_META": "RMETA",
    "LEFT_ALT": "LALT", "RIGHT_ALT": "RALT",
    "ESCAPE": "ESC", "RETURN": "RET"
}

def replace_aliases(token):
    for k, v in aliases.items():
        token = re.sub(r'\b' + k + r'\b', v, token)
    return token

def format_layer(match):
    prefix = match.group(1)
    bindings_text = match.group(2)
    suffix = match.group(3)
    
    tokens = re.findall(r'&[^&>]+', bindings_text)
    tokens = [t.strip() for t in tokens]
    tokens = [replace_aliases(t) for t in tokens]
    
    if len(tokens) != 38:
        print(f"Warning: skipped layer because it has {len(tokens)} tokens instead of 38")
        return match.group(0)
        
    rows = [
        tokens[0:10],
        tokens[10:20],
        tokens[20:30],
        ['', '', '', tokens[30], tokens[31], tokens[32], tokens[33], tokens[34], tokens[35], tokens[36], tokens[37]]
    ]
    # Wait, the 4th row has 8 thumb keys. We should align them with the main grid.
    # The columns for thumbs usually go like:
    # col 3, 4, 5, 6 for left? No, 8 keys.
    # let's just do:
    # ['', '', '', thumb1, thumb2, thumb3, thumb4, thumb5, thumb6, thumb7, thumb8] -> 11 items.
    pass

