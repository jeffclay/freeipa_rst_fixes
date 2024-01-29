import os
import re


def fix_spaces(line):
    """
    Fix extra spacing between words while preserving any leading spaces for indentation.
    """
    leading_space_count = 0
    if line.startswith(" "):
        leading_space_count = len(line) - len(line.lstrip())
    line_indent = " " * leading_space_count
    new_line = re.sub(r'\s+', ' ', line)
    new_line = line_indent + new_line
    return new_line


def confirm_new_line_terminator(line):
    """
    Make sure that our line has a new line return.
    """
    if not line.endswith("\n"):
        return line + "\n"
    return line


def table_guard(line):
    """
    We shouldn't touch tables, so make some assumptions on what table lines could look like and ignore them.
    """
    if line.strip().startswith('+') and line.endswith('+\n'):
        return True
    if line.strip().startswith('|') and line.endswith('|\n'):
        return True
    return False


def create_literal_blocks(file_path):
    """
    This creates literal blocks by detecting groups of individual "literal" lines.
    This is different from other checks done for existing literal blocks.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    i = 0
    in_block = False

    while i < len(lines):
        line = lines[i]

        # Check for the start of a code block
        if (not in_block and line.startswith('| ``')
                and (i == 0 or lines[i - 1].strip() == '')) and not table_guard(line):
            new_lines.append('::\n\n')  # Adding an extra newline after this line
            in_block = True

        if in_block:
            # Process the code block
            if line.strip() == '':
                # End of the code block
                in_block = False
                new_lines.append('\n')  # Append a newline after the code block
            else:
                if line.startswith('| ``') or line.startswith('| :literal:'):
                    start_index = 4 if line.startswith('| ``') else 12
                    content = line[start_index:].rstrip()
                    if content.endswith('``'):
                        content = content[:-2].rstrip()
                    new_lines.append('    ' + content + '\n')  # Preserving newline within the code block
                else:
                    new_lines.append(line)  # Preserving the line as is within the code block
        else:
            # Directly append lines outside of code blocks
            new_lines.append(line)

        i += 1

    with open(file_path, 'w') as file:
        file.writelines(new_lines)


def fix_existing_literal_blocks(file_path):
    """
    Remove redundant literal block markers from lines in specified file.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # if a line starts with | `` and ends with ``, remove them and preserve existing spacing.
            if line.lstrip().startswith("| ``") and line.endswith('``\n'):
                # remove | ``
                line = line.replace("| ``", "", 1)
                # remove trailing `` and add line terminator back
                line = line[:-3]
                line = confirm_new_line_terminator(line)
            file.write(line)


def remove_literal_literals(file_path):
    """
    Remove '| :literal:' markers from lines in specified file.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # if a line starts with | :literal:, remove it
            if line.lstrip().startswith("| :literal:"):
                line = line.replace("| :literal:", "", 1)
                line = confirm_new_line_terminator(line)
            file.write(line)


def refine_double_asterisk_lines(file_path):
    """
    Clean and format lines beginning with '| **' and ending with '**'.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # if line starts with | ** and ends with ** remove them and all the ` and \ within.
            if line.lstrip().startswith("| **") and line.endswith("**\n"):
                # remove starting | **
                line = line.replace("| **", "", 1)
                # remove extra \ throughout the line
                line = line.replace("\\", "", -1)
                # remove extra ` throughout the line
                line = line.replace("`", "", -1)
                # remove trailing ** and add the line terminator back.
                line = line[:-3] + "\n"
                # fix extra spacing between words
                line = fix_spaces(line)
                # if we're in a code block, match the indentation of the line above it.
                if previous_line.startswith(" "):
                    leading_spaces = len(previous_line) - len(previous_line.lstrip())
                    spaces_for_string = " " * leading_spaces
                    line = spaces_for_string + line
                line = confirm_new_line_terminator(line)
            previous_line = line
            file.write(line)


def refine_double_backtick_asterisk_lines(file_path):
    """
    Clean and format lines beginning with '| `` ``' and ending with '**'.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # if line starts with | `` `` and ends with ** remove them and all the `, * and \ within.
            if line.lstrip().startswith("| `` ``") and line.endswith("**\n"):
                # remove starting | `` ``
                line = line.replace("| `` ``", "", 1)
                # remove extra \ throughout the line
                line = line.replace("\\", "", -1)
                # remove extra `` throughout the line
                line = line.replace("``", "", -1)
                # remove trailing ** and add the line terminator back.
                line = line[:-3] + "\n"
                # remove extra * throughout the line
                line = line.replace("*", "", -1)
                line = confirm_new_line_terminator(line)
            file.write(line)


def refine_single_backtick_asterisk_lines(file_path):
    """
    Clean and format lines beginning with '| ``' and ending with '**'.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # if line starts with | `` and ends with ** remove them and all the `, * and \ within.
            if line.lstrip().startswith("| ``") and line.endswith("**\n"):
                # remove starting | ``
                line = line.replace("| ``", "", 1)
                # remove extra \ throughout the line
                line = line.replace("\\", "", -1)
                # remove extra `` throughout the line
                line = line.replace("``", "", -1)
                # remove trailing ** and add the line terminator back.
                line = line[:-3] + "\n"
                # remove extra * throughout the line
                line = line.replace("*", "", -1)
                line = confirm_new_line_terminator(line)
            file.write(line)


def remove_backslash_asterisk_pattern(file_path):
    """
    Remove '\ **``' from lines.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            if "``\\ **``" in line:
                line = line.replace("``\\ **``", "", -1)
                line = confirm_new_line_terminator(line)
            file.write(line)


def remove_asterisk_backslash_pattern(file_path):
    """
    Remove '``**\ ``' from lines.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            if "``**\\ ``" in line:
                line = line.replace("``**\\ ``", "", -1)
                line = confirm_new_line_terminator(line)
            file.write(line)


def remove_double_backslash_pattern(file_path):
    """
    Remove '``\ ````\ ``' from lines.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # some lines have ``\ ````\ ``  and it should be removed.
            if "``\\ ````\\ ``" in line:
                line = line.replace("``\\ ````\\ ``", "", -1)
                line = confirm_new_line_terminator(line)
            file.write(line)


def remove_asterisk_double_backtick_pattern(file_path):
    """
    Remove '| **``' and '``' if a line begins and ends with them.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # if line starts with | **`` and ends with `` remove them
            if line.lstrip().startswith("| **``") and line.endswith("``\n"):
                # remove starting | **``
                line = line.replace("| **``", "", 1)
                # remove trailing `` and add the line terminator back.
                line = line[:-3] + "\n"
                line = confirm_new_line_terminator(line)
            file.write(line)


def remove_single_asterisk_double_backtick_indent(file_path):
    """
    Remove '| *``' and '`` if a line begins and ends them.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # if line starts with "| *``" and ends with "``", remove it
            if line.strip().startswith("| *``") and line.endswith("``\n"):
                line = line.replace("| *``", "", -1)
                line = line[:-3] + "\n"
                # if we're in a code block, match the indentation of the line above it.
                if previous_line.startswith(" "):
                    leading_spaces = len(previous_line) - len(previous_line.lstrip())
                    spaces_for_string = " " * leading_spaces
                    line = spaces_for_string + line
                line = confirm_new_line_terminator(line)
            previous_line = line
            file.write(line)


def remove_double_backtick_asterisk_end_pattern(file_path):
    """
    Remove '| ``' and '``*' if a line begins and ends with them.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # if line starts with | `` and ends with ``* remove them
            if line.lstrip().startswith("| ``") and line.endswith("``*\n"):
                # remove | '' from the beginning of the line
                line = line.replace("| ``", "", 1)
                line = line[:-4] + "\n"
                line = confirm_new_line_terminator(line)
            file.write(line)


def remove_backslash_asterisk(file_path):
    """
    Remove '``\ *``' if in a line.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            if "``\\ *``" in line:
                line = line.replace("``\\ *``", "", -1)
                line = fix_spaces(line)
                line = confirm_new_line_terminator(line)
            file.write(line)


def remove_asterisk_backslash(file_path):
    """
    Remove '``*\ ``' if in a line.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # some lines have ``*\ ``  and it should be removed.
            if "``*\\ ``" in line:
                line = line.replace("``*\\ ``", "", -1)
                line = fix_spaces(line)
                line = confirm_new_line_terminator(line)
            file.write(line)


def format_continuation_indentation(file_path):
    """
    If a line is only representing a continuation, confirm it matches the indentation of the parent
    line if it is indented.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # if a line is only representing a continuation/abbreviation
            if line.strip() == '....' or line.strip() == '...':
                # if we're in a code block, match the indentation of the line above it.
                if previous_line.startswith(" "):
                    leading_spaces = len(previous_line) - len(previous_line.lstrip())
                    spaces_for_string = " " * leading_spaces
                    line = spaces_for_string + line.strip()
                line = confirm_new_line_terminator(line)
            previous_line = line
            file.write(line)


def remove_single_pipe_lines(file_path):
    """
    If a line is only a '|', remove the line.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # if a line is only a |, remove it
            if line == '|':
                continue
            file.write(line)


def remove_backtick_asterisk_pattern(file_path):
    """
    Remove '``' and '``*' from the beginning and end of any lines when both are present.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            # if line starts with `` and ends with ``* remove them
            if line.lstrip().startswith("``") and line.endswith("``* \n"):
                # remove '' from the beginning of the line
                line = line.replace("``", "", 1)

                line = line[:-5] + "\n"
                line = confirm_new_line_terminator(line)
            file.write(line)


def fix_inline_literals(file_path):
    """
    If a line contains '**``' and '``**', replace '**``' with '``' and replace '``**' with '``\'.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            if '**``' in line and '``**' in line:
                line = line.replace('**``', '``', -1)
                line = line.replace('``**', '``\\ ', -1)
                line = confirm_new_line_terminator(line)
            file.write(line)


def fix_remaining_inline_literal_end_strings_1(file_path):
    """
    If a line contains '``**', replace it with '``'.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            if '``**' in line:
                line = line.replace('``**', '``', -1)
            file.write(line)


def fix_remaining_inline_literal_end_strings_2(file_path):
    """
    If a line contains '``* ', replace it with '`` ' while trying to avoid wildcards.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if table_guard(line):
                file.write(line)
                continue
            if '``* ' in line and '*.*' not in line and '*-' not in line:
                line = line.replace('``* ', '`` ', -1)
                line = confirm_new_line_terminator(line)
            file.write(line)


def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.rst'):
                create_literal_blocks(os.path.join(root, file))
                fix_existing_literal_blocks(os.path.join(root, file))
                remove_literal_literals(os.path.join(root, file))
                refine_double_asterisk_lines(os.path.join(root, file))
                refine_double_backtick_asterisk_lines(os.path.join(root, file))
                refine_single_backtick_asterisk_lines(os.path.join(root, file))
                remove_backslash_asterisk_pattern(os.path.join(root, file))
                remove_asterisk_backslash_pattern(os.path.join(root, file))
                remove_double_backslash_pattern(os.path.join(root, file))
                remove_asterisk_double_backtick_pattern(os.path.join(root, file))
                remove_single_asterisk_double_backtick_indent(os.path.join(root, file))
                remove_double_backtick_asterisk_end_pattern(os.path.join(root, file))
                remove_backslash_asterisk(os.path.join(root, file))
                remove_asterisk_backslash(os.path.join(root, file))
                format_continuation_indentation(os.path.join(root, file))
                remove_single_pipe_lines(os.path.join(root, file))
                remove_backtick_asterisk_pattern(os.path.join(root, file))
                fix_inline_literals(os.path.join(root, file))
                fix_remaining_inline_literal_end_strings_1(os.path.join(root, file))
                fix_remaining_inline_literal_end_strings_2(os.path.join(root, file))


process_directory('/my/path/freeipa.github.io/src/page')
print(f'Done')
