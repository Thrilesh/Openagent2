import pyparsing as pp

pp.ParserElement.enable_packrat()

command_start = pp.Suppress("{{")
command_end = pp.Suppress("}}")
string_literal = pp.quotedString.set_name("string_literal")

# Define regular_command component
regular_command = pp.Combine(command_start + pp.Word(pp.alphas) + command_end).set_name("regular_command")

# Define gen_command component
gen_command = pp.Combine(command_start + pp.Keyword("gen") + pp.quotedString + command_end).set_name("gen_command")

# Define your individual parsing components here

literal_chunk = string_literal | regular_command | gen_command

program_chunk = pp.Forward()
program_chunk <<= literal_chunk + program_chunk | pp.Empty()

program = pp.Group(pp.OneOrMore(program_chunk))("program")

grammar = (program + pp.StringEnd()).parse_with_tabs()


def wrap_with_user_tag(s):
    return "{{#user}}{}\n{{/user}}".format(s)

def wrap_with_assistant_tag(s):
    return "{{#assistant}}{}\n{{/assistant}}".format(s)

def format_chat_template(input_text):
    parsed_program = grammar.parseString(input_text)
    formatted_output = []

    for chunk in parsed_program.program:
        if chunk.name == "regular_command":
            # Regular command, wrap with user tag
            formatted_output.append(wrap_with_user_tag(chunk[0]))
        elif chunk.name == "gen_command":
            # Gen command, wrap with assistant tag
            formatted_output.append(wrap_with_assistant_tag(chunk[0]))
        else:
            # String literal, wrap with user tag
            formatted_output.append(wrap_with_user_tag(chunk[0]))

    # Ensure the template ends with an assistant's completion command
    last_chunk = formatted_output[-1]
    if "{{/assistant}}" not in last_chunk:
        formatted_output.append("{{#assistant}}{{gen 'write'}}{{/assistant}}")

    return "\n".join(formatted_output)


input_text = """Tweak this proverb to apply to model instructions instead. Where there is no guidance{{gen 'rewrite'}}"""
formatted_output = format_chat_template(input_text)
print(formatted_output)
