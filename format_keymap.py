import re

filepath = '/home/nick/Code/chirality/config/boards/shields/chirality/chirality.keymap'
with open(filepath, 'r') as f:
    content = f.read()

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
    "ESCAPE": "ESC", "RETURN": "RET",
    "LEFT": "LEFT", "RIGHT": "RIGHT", "UP": "UP", "DOWN": "DOWN"
}

def replace_aliases(token):
    for k, v in aliases.items():
        token = re.sub(r'\b' + k + r'\b', v, token)
    return token

def format_layer(match):
    prefix = match.group(1)
    bindings_text = match.group(2)
    suffix = match.group(3)
    
    # extract tokens
    tokens = re.findall(r'&[^&>]+', bindings_text)
    tokens = [t.strip() for t in tokens]
    
    # Check if this is a main layer (38 tokens)
    if len(tokens) == 38:
        tokens = [replace_aliases(t) for t in tokens]
        
        # 4 rows: 10, 10, 10, 10 (with 1st and last being empty string on thumb row)
        rows = [
            tokens[0:10],
            tokens[10:20],
            tokens[20:30],
            ['', tokens[30], tokens[31], tokens[32], tokens[33], tokens[34], tokens[35], tokens[36], tokens[37], '']
        ]
        
        col_widths = [0] * 10
        for r_idx, row in enumerate(rows):
            for c_idx, token in enumerate(row):
                if len(token) > col_widths[c_idx]:
                    col_widths[c_idx] = len(token)
                    
        formatted_rows = []
        for r_idx, row in enumerate(rows):
            formatted_tokens = []
            for c_idx, token in enumerate(row):
                if token == '' and r_idx == 3:
                    # just padding
                    formatted_tokens.append(' ' * col_widths[c_idx])
                else:
                    # use spaces to align to a specific length so it looks like a grid
                    formatted_tokens.append(token.ljust(col_widths[c_idx]))
            
            # Use 2 spaces as delimiter between columns
            line = '  '.join(formatted_tokens)
            # Remove trailing spaces
            line = line.rstrip()
            formatted_rows.append("        " + line)
            
        return prefix + "\n" + '\n'.join(formatted_rows) + "\n      " + suffix
    else:
        return match.group(0)

new_content = re.sub(r'(bindings\s*=\s*<)\s*(.*?)\s*(>;)', format_layer, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(new_content)
print("Done formatting.")
