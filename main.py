import re
import time 

def _tokenize_s_exp_string(text):
    token_patterns = re.compile(
        r'"(?:[^"\\]|\\.)*"|'
        r"'(?:[^'\\]|\\.)*'|"
        r'\(|\)|'
        r'[^\s()\'"]+'
    , re.UNICODE)
    return [match.group(0) for match in token_patterns.finditer(text)]

def parse_s_expression(tokens_iter):
    s_exp = []
    while True:
        try:
            token = next(tokens_iter)
        except StopIteration:
            return s_exp

        if token == '(':
            s_exp.append(parse_s_expression(tokens_iter))
        elif token == ')':
            return s_exp
        elif (token.startswith('"') and token.endswith('"')) or \
             (token.startswith("'") and token.endswith("'")):
            s_exp.append(token)
        else:
            s_exp.append(token)

def s_exp_to_re_pattern(s_exp_list):
    if not isinstance(s_exp_list, list):
        if s_exp_list == "alpha":
            return r'[a-zA-ZÀ-ÿ]'  # Added Unicode support for Spanish characters
        elif s_exp_list == "digit":
            return r'\d'
        elif s_exp_list == "_":
            return r'_'
        elif s_exp_list == "\\s":
            return r'\s'
        elif s_exp_list == "\\b":
            return r'\b'
        elif s_exp_list == "\\n":
            return r'\n'
        elif s_exp_list == "\\t":
            return r'\t'
        elif s_exp_list == "\\r":
            return r'\r'
        elif s_exp_list == "\n":  # Handle literal newline
            return r'\n'
        elif s_exp_list == "\t":  # Handle literal tab
            return r'\t'
        elif s_exp_list == "\r":  # Handle literal carriage return
            return r'\r'
        elif s_exp_list == " ":
            return r' '
        elif s_exp_list == "dot-char":  # Fixed: removed quotes and list check
            return r'.'

        if (s_exp_list.startswith('"') and s_exp_list.endswith('"')) or \
           (s_exp_list.startswith("'") and s_exp_list.endswith("'")):
            content = s_exp_list[1:-1]
            return re.escape(content)
        else:
            return re.escape(s_exp_list)

    operator = s_exp_list[0]

    if operator in ["star", "plus", "any-char-except", "escape-char"] and len(s_exp_list) < 2:
        raise ValueError(f"{operator} requiere al menos un operando: {s_exp_list}")

    if operator == "escape-char":
        escaped_char = s_exp_list[1]
        # Handle both quoted and unquoted escape characters
        if (escaped_char.startswith('"') and escaped_char.endswith('"')) or \
           (escaped_char.startswith("'") and escaped_char.endswith("'")):
            escaped_char = escaped_char[1:-1]
        return r'\\' + re.escape(escaped_char)

    elif operator == "any-char-except":
        char_literal_arg = s_exp_list[1]

        if (char_literal_arg.startswith('"') and char_literal_arg.endswith('"')) or \
           (char_literal_arg.startswith("'") and char_literal_arg.endswith("'")):
            content_to_exclude = char_literal_arg[1:-1]
        else:
            content_to_exclude = char_literal_arg

        regex_set_content = ""
        i = 0
        while i < len(content_to_exclude):
            char = content_to_exclude[i]
            if char == '\\':
                if i + 1 < len(content_to_exclude):
                    next_char = content_to_exclude[i+1]
                    if next_char == 'n':
                        regex_set_content += r'\n'
                    elif next_char == 't':
                        regex_set_content += r'\t'
                    elif next_char == 'r':
                        regex_set_content += r'\r'
                    elif next_char == '"':
                        regex_set_content += r'"'
                    elif next_char == "'":
                        regex_set_content += r"'"
                    elif next_char == '\\':
                        regex_set_content += r'\\'
                    else:
                        regex_set_content += '\\' + next_char
                    i += 2
                    continue
            
            if char in r'-[]^':
                regex_set_content += '\\' + char
            else:
                regex_set_content += char
            i += 1

        return f'[^{regex_set_content}]'

    operands = [s_exp_to_re_pattern(op) for op in s_exp_list[1:]]

    if operator == "or":
        return r'(?:' + '|'.join(operands) + r')'
    elif operator == "concat":
        return r'(?:' + ''.join(operands) + r')'
    elif operator == "star":
        return r'(?:' + operands[0] + r')*'
    elif operator == "plus":
        return r'(?:' + operands[0] + r')+'
    else:
        return re.escape(operator)

def load_lexical_rules(filepath):
    rules_by_language = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content_without_comments = re.sub(r';;.*$', '', content, flags=re.MULTILINE)
    all_tokens = _tokenize_s_exp_string(content_without_comments)
    tokens_iterator = iter(all_tokens)

    while True:
        try:
            token = next(tokens_iterator)
            if token != '(':
                if token.strip() == '':
                    continue
                raise ValueError(f"S-expression malformada: Se esperaba '(' pero se encontró '{token}' en el nivel superior.")
        except StopIteration:
            break

        parsed_s_exp = parse_s_expression(tokens_iterator)

        if not (len(parsed_s_exp) >= 2 and parsed_s_exp[0] == 'language'):
            print(f"Advertencia: S-expression parseada de nivel superior no es de tipo 'language': {parsed_s_exp}")
            continue

        language_name = parsed_s_exp[1]
        current_lang_tokens = []

        for sub_exp in parsed_s_exp[2:]:
            if len(sub_exp) >= 3 and sub_exp[0] == 'token':
                token_name = sub_exp[1]
                pattern_s_exp_list = sub_exp[2]

                # Patrones específicos mejorados para cada lenguaje
                if token_name == "STRING":
                    if language_name == "Haskell":
                        # Patrón mejorado para strings de Haskell con escape sequences
                        python_regex = r'"(?:[^"\\]|\\[\\\"nrtbfav]|\\[0-9]+|\\x[0-9a-fA-F]+)*"'
                    elif language_name == "Pascal":
                        # Patrón para strings de Pascal (comillas simples)
                        python_regex = r"'(?:[^']|'')*'"
                    elif language_name == "Cpp":
                        # Patrón mejorado para strings de C++
                        python_regex = r'(?:"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
                    else:
                        python_regex = s_exp_to_re_pattern(pattern_s_exp_list)
                
                elif token_name == "CHAR":
                    if language_name == "Haskell":
                        # Patrón para caracteres de Haskell
                        python_regex = r"'(?:[^'\\]|\\[\\\'nrtbfav]|\\[0-9]+|\\x[0-9a-fA-F]+)'"
                    else:
                        python_regex = s_exp_to_re_pattern(pattern_s_exp_list)
                
                elif token_name == "COMMENT":
                    if language_name == "Haskell":
                        # Comentarios de Haskell: -- hasta fin de línea y {- ... -}
                        python_regex = r'(?:--[^\n]*|{-(?:[^-]|-(?!}))*-})'
                    elif language_name == "Pascal":
                        # Comentarios de Pascal: { ... }, (* ... *), // ...
                        python_regex = r'(?:{[^}]*}|\(\*(?:[^*]|\*(?!\)))*\*\)|//[^\n]*)'
                    elif language_name == "Cpp":
                        python_regex = r'(?://[^\n]*|/\*[\s\S]*?\*/)'
                    else:
                        python_regex = s_exp_to_re_pattern(pattern_s_exp_list)
                
                elif token_name == "WHITESPACE":
                    # Patrón directo para espacios en blanco
                    python_regex = r'[ \t\n\r]+'
                
                elif token_name == "NUMBER":
                    if language_name == "Haskell":
                        # Números de Haskell (enteros y flotantes)
                        python_regex = r'(?:\d+\.\d+|\d+)'
                    elif language_name == "Pascal":
                        # Números de Pascal (enteros, flotantes, científicos)
                        python_regex = r'(?:\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\d+)'
                    else:
                        python_regex = s_exp_to_re_pattern(pattern_s_exp_list)
                
                elif token_name == "IDENTIFIER":
                    if language_name == "Haskell":
                        # Identificadores de Haskell (pueden incluir ')
                        python_regex = r"\b[a-zA-Z_][a-zA-Z0-9_']*\b"
                    elif language_name == "Pascal":
                        # Identificadores de Pascal (case insensitive)
                        python_regex = r'\b[a-zA-Z][a-zA-Z0-9_]*\b'
                    else:
                        python_regex = s_exp_to_re_pattern(pattern_s_exp_list)
                
                elif token_name == "KEYWORD":
                    if language_name == "Pascal":
                        # Keywords de Pascal (case insensitive)
                        keywords = pattern_s_exp_list[1:]  # Skip 'or'
                        keyword_pattern = '|'.join([re.escape(kw.strip('"\'')) for kw in keywords])
                        python_regex = rf'\b(?:{keyword_pattern})\b'
                    else:
                        python_regex = s_exp_to_re_pattern(pattern_s_exp_list)
                        # Agregar word boundaries para keywords
                        if not (python_regex.startswith(r'\b') and python_regex.endswith(r'\b')):
                            python_regex = r'\b' + python_regex + r'\b'
                
                elif token_name == "OPERATOR_IDENTIFIER" and language_name == "Haskell":
                    # Operadores especiales de Haskell
                    python_regex = r'[~!@#$%^&*\-+=|\\/<>.:?]+'
                
                else:
                    python_regex = s_exp_to_re_pattern(pattern_s_exp_list)

                current_lang_tokens.append((token_name, python_regex))
            else:
                print(f"Advertencia: S-expression de token no reconocida dentro de '{language_name}': {sub_exp}")

        # Orden de prioridad fijo
        order_priority = {
            'WHITESPACE': 0,
            'COMMENT': 1,
            'STRING': 2,
            'CHAR': 3,
            'NUMBER': 4,
            'KEYWORD': 5,
            'OPERATOR': 6,
            'DELIMITER': 7,
            'OPERATOR_IDENTIFIER': 8,
            'IDENTIFIER': 9
        }
        current_lang_tokens.sort(key=lambda x: (order_priority.get(x[0], 99), -len(x[1]), x[0]), reverse=False)

        rules_by_language[language_name] = current_lang_tokens

    return rules_by_language

def tokenize_code(code_filepath, language_rules):
    try:
        with open(code_filepath, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{code_filepath}' no fue encontrado.")
        return []

    tokens = []
    current_pos = 0
    code_length = len(code_content)

    while current_pos < code_length:
        longest_match = None
        longest_match_type = None
        longest_match_length = 0

        for token_type, pattern in language_rules:
            try:
                match = re.match(pattern, code_content[current_pos:], re.DOTALL | re.UNICODE | re.IGNORECASE)
                if match:
                    match_text = match.group(0)
                    if len(match_text) > longest_match_length:
                        longest_match_length = len(match_text)
                        longest_match = match_text
                        longest_match_type = token_type
            except re.error as e:
                print(f"Error en regex para {token_type}: {pattern}")
                print(f"Error: {e}")
                continue

        if longest_match:
            tokens.append((longest_match_type, longest_match))
            current_pos += len(longest_match)
        else:
            char = code_content[current_pos]
            print(f"Error léxico: Carácter no reconocido '{char}' (ASCII: {ord(char)}) en la posición {current_pos} del archivo {code_filepath}")
            
            # Show context around the error
            start = max(0, current_pos - 10)
            end = min(code_length, current_pos + 10)
            context = code_content[start:end]
            print(f"Contexto: '{context}' (posición del error marcada)")
            
            current_pos += 1

    return tokens

def generate_html_output(filepath, lang_name, tokens, elapsed_time):
    # CSS for syntax highlighting and table styling
    css_styles = """
      span {
        cursor: default;
      }
      span:hover {
        background-color: rgba(255,255,255,0.1);
      }
      body { font-family: monospace; background-color: #282c34; color: #abb2bf; }
      .code-container {
          background-color: #21252b;
          border: 1px solid #3b4048;
          padding: 15px;
          border-radius: 5px;
          margin: 20px;
          white-space: pre-wrap;
          word-wrap: break-word;
      }
      .PREPROCESSOR_DIRECTIVE { color: #56b6c2; }
      .KEYWORD { color: #c678dd; }
      .IDENTIFIER { color: #e06c75; }
      .DELIMITER { color: #abb2bf; }
      .OPERATOR { color: #56b6c2; }
      .STRING { color: #98c379; }
      .NUMBER { color: #d19a66; }
      .COMMENT { color: #5c6370; font-style: italic; }
      .CHAR { color: #98c379; }
      .OPERATOR_IDENTIFIER { color: #e06c75; }
      .WHITESPACE { color: #abb2bf; }
      .ERROR { background-color: red; color: white; }
      table.token-summary {
        margin: 20px;
        border-collapse: collapse;
        width: 400px;
        background-color: #21252b;
        color: #abb2bf;
      }
      table.token-summary th, table.token-summary td {
        border: 1px solid #3b4048;
        padding: 8px;
        text-align: left;
      }
      table.token-summary th {
        background-color: #3b4048;
      }
    """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tokenized Code - {filepath} ({lang_name})</title>
        <style>
            {css_styles}
        </style>
    </head>
    <body>
        <h1>Tokenized Code: {filepath} ({lang_name})</h1>
        <div class="code-container">
    """

    for token_type, token_value in tokens:
        escaped_token_value = token_value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        html_content += f'<span class="{token_type}" title="{token_type}">{escaped_token_value}</span>'

    html_content += "</div>"

    total_tokens = sum(1 for t in tokens if t[0] != 'WHITESPACE')
    count_by_type = {}
    for token_type, _ in tokens:
        if token_type == 'WHITESPACE':
            continue
        count_by_type[token_type] = count_by_type.get(token_type, 0) + 1

    html_content += f"""
    <h2>Estadísticas de Tokenización</h2>
    <p><strong>Tiempo de ejecución:</strong> {elapsed_time:.4f} segundos</p>
    <table class="token-summary">
        <thead>
            <tr><th>Tipo de Token</th><th>Cantidad</th><th>Porcentaje</th></tr>
        </thead>
        <tbody>
    """

    for token_type, count in sorted(count_by_type.items(), key=lambda x: -x[1]):
        percentage = (count / total_tokens) * 100 if total_tokens > 0 else 0
        html_content += f"<tr><td class={token_type}>{token_type}</td><td>{count}</td><td>{percentage:.2f}%</td></tr>"

    html_content += f"""
        <tr><th>Total</th><th>{total_tokens}</th><th>100%</th></tr>
        </tbody>
    </table>
    </body>
    </html>
    """

    output_html_filepath = f"{filepath}.html"
    with open(output_html_filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ HTML output saved to {output_html_filepath}")



def main():
    total_start_time = time.time()

    expr_s_file = "lexical_definitions.txt"
    files_to_process = {
        "input.cpp": "Cpp",
        "input.hs": "Haskell", 
        "input.pas": "Pascal"
    }

    token_patterns = load_lexical_rules(expr_s_file)
    
    for filepath, lang_name in files_to_process.items():
        if lang_name in token_patterns:
            print(f"\n--- Tokenizando {filepath} ({lang_name}) ---")

            file_start_time = time.time()

            language_rules = token_patterns[lang_name]
            tokens = tokenize_code(filepath, language_rules)

            for token_type, token_value in tokens:
                print(f"  {token_type:<20} : '{token_value}'")

            file_end_time = time.time()
            file_elapsed = file_end_time - file_start_time

            generate_html_output(filepath, lang_name, tokens, file_elapsed)

            total_tokens = sum(1 for t in tokens if t[0] != 'WHITESPACE')
            print(f"🔢 Total de tokens: {total_tokens}")
            print(f"⏱️ Tiempo de ejecución para {filepath}: {file_elapsed:.4f} segundos")
        else:
            print(f"❌ Error: No se encontraron reglas léxicas para el lenguaje '{lang_name}'.")

    total_end_time = time.time()
    total_elapsed = total_end_time - total_start_time
    print(f"\n✅ Tiempo total de ejecución: {total_elapsed:.4f} segundos")



if __name__ == "__main__":
    main()