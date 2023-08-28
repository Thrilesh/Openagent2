import pyparsing as pp

# Test Case1
string_literal = pp.Group(pp.Suppress('"') + pp.ZeroOrMore(pp.CharsNotIn('"')) + pp.Suppress('"') | pp.Suppress("'") + pp.ZeroOrMore(pp.CharsNotIn("'")) + pp.Suppress("'"))("string_literal")

test_input = '"Hello, World!"'
parsed_result = string_literal.parseString(test_input)
print(parsed_result)
# output:[['Hello, World!']]

# Test Case2
pp.ParserElement.enablePackrat()

command_start = pp.Suppress("{{")
command_end = pp.Suppress("}}")

regular_command = pp.Combine(command_start + pp.OneOrMore(pp.CharsNotIn("}")) + command_end)("regular_command")
gen_command = pp.Combine(command_start + "gen" + pp.OneOrMore(pp.CharsNotIn("}")) + command_end)("gen_command")

test_input = "{{my_command}}"
parsed_result = regular_command.parseString(test_input)
print(parsed_result)

test_input = "{{gen 'write'}}"
parsed_result = gen_command.parseString(test_input)
print(parsed_result)



# Test Case3
pp.ParserElement.enablePackrat()

command_start = pp.Suppress("{{")
command_end = pp.Suppress("}}")

string_literal = pp.Group(pp.Suppress('"') + pp.ZeroOrMore(pp.CharsNotIn('"')) + pp.Suppress('"') | pp.Suppress("'") + pp.ZeroOrMore(pp.CharsNotIn("'")) + pp.Suppress("'"))("string_literal")
regular_command = pp.Combine(command_start + pp.OneOrMore(pp.CharsNotIn("}")) + command_end)("regular_command")
gen_command = pp.Combine(command_start + "gen" + pp.OneOrMore(pp.CharsNotIn("}")) + command_end)("gen_command")

literal_chunk = string_literal | regular_command | gen_command

test_input = "{{my_command}} 'Hello, World!' {{gen 'write'}}"
parsed_result = pp.OneOrMore(literal_chunk).parseString(test_input)
print(parsed_result) #['my_command',['Hello,World!'],"gen 'write'"]

import pyparsing as pp

pp.ParserElement.enablePackrat()

command_start = pp.Suppress("{{")
command_end = pp.Suppress("}}")
string_literal = pp.quotedString.setName("string_literal")

# Define regular_command component
regular_command = pp.Combine(command_start + pp.Word(pp.alphas) + command_end).setName("regular_command")

# Define gen_command component
gen_command = pp.Combine(command_start + pp.Keyword("gen") + pp.quotedString + command_end).setName("gen_command")

# Define your individual parsing components here

literal_chunk = string_literal | regular_command | gen_command

program_chunk = pp.Forward()
program_chunk <<= literal_chunk + program_chunk | pp.Empty()

program = pp.Group(pp.OneOrMore(program_chunk))("program")

grammar = (program + pp.StringEnd()).parseWithTabs()


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

