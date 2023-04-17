import re
import sys

def is_valid_syntax(line):
    if valid_a(line) or valid_c(line) or valid_d(line):
        return True

    return False


def valid_d(line):
    search = re.search('^(\d+)(?:,(\d+))?d\d+$', line)
    if not search:
        return False
    left_range = search.groups()
    print(left_range)
    if left_range[0] and left_range[1] and int(left_range[1]) <= int(left_range[0]):
        return False

    return True

def valid_a(line):
    search = re.search('^\d+a(\d+)(?:,(\d+))?$', line)
    if not search:
        return False
    right_range = search.groups()
    print(right_range)
    if right_range[0] and right_range[1] and int(right_range[1]) <= int(right_range[0]):
        return False
    return True

def valid_c(line):
    search = re.search('^(\d+)(?:,(\d+))?c(\d+)(?:,(\d+))?$', line)
    if not search:
        return False

    left_ranges = search.groups()[:2]
    right_ranges = search.groups()[2:]

    if left_ranges[0] and left_ranges[1] and int(left_ranges[1]) <= int(left_ranges[0]):
        return False
    if right_ranges[0] and right_ranges[1] and int(right_ranges[1]) <= int(right_ranges[0]):
        return False

    return True


# normalises command to l1 l2 c r1 r2 format and appends to array
def format_command(line, arr):
    if 'a' in line:
        left, right = (line.split('a'))
        right = right.split(',')
        if len(right) == 2:
            start_r = int(right[0]) - 1
            end_r = int(right[1])
        else:
            start_r = int(right[0]) - 1
            end_r = int(right[0])

        arr.append((int(left), int(left), 'a', start_r, end_r))

    if 'd' in line:
        left, right = line.split('d')
        left = left.split(',')
        if len(left) == 2:
            start_l = int(left[0]) - 1
            end_l = int(left[1])
        else:
            start_l = int(left[0]) - 1
            end_l = int(left[0])

        arr.append((start_l, end_l, 'd', int(right), int(right)))

    if 'c' in line:
        left, right = line.split('c')
        left = left.split(',')
        right = right.split(',')
        if len(left) == 2:
            start_l = int(left[0]) - 1
            end_l = int(left[1])
        else:
            start_l = int(left[0]) - 1
            end_l = int(left[0])

        if len(right) == 2:
            start_r = int(right[0]) - 1
            end_r = int(right[1])
        else:
            start_r = int(right[0]) - 1
            end_r = int(right[0])

        arr.append((start_l, end_l, 'c', start_r, end_r))

def valid_sequence(formatted_commands):
    for i in range(len(formatted_commands)):
        if i == 0:
            if not (formatted_commands[i][0] >= 0 and formatted_commands[i][3] >= 0 and\
            formatted_commands[i][0] == formatted_commands[i][3]):
                #print('invalid first command')
                return False
            continue

            # Check starting range of next command is strictly greater than end range
            # of previous command on both sides
        if not (formatted_commands[i][0] > formatted_commands[i-1][1] and\
                formatted_commands[i][3] > formatted_commands[i-1][4]):
            #print('sequence ranges overlap')
            return False

        if not (formatted_commands[i][0] - formatted_commands[i-1][1] ==\
                formatted_commands[i][3] - formatted_commands[i-1][4]):
            #print('different block size')
            return False

    return True


def DiffCommands(filename):
    diff_obj = []
    formatted_commands = []
    with open(filename, 'r') as file:
        for line in file:

            if not is_valid_syntax(line):
                print('Cannot possibly be the commands for the diff of two files')
                return
            line = line.strip()
            diff_obj.append(line)
            format_command(line, formatted_commands)
        # print(diff_obj, formatted_commands)
        for i in range(len(formatted_commands)):
            # print(f'{diff_obj[i]} \t {formatted_commands[i]}')
            if not valid_sequence(formatted_commands):
                print('Cannot possibly be the commands for the diff of two files')
                return False

    return diff_obj, formatted_commands


diffs, formatted_commands = DiffCommands('diff_1.txt')
print('d',diffs)
# for i in obj:
#     print(i)


def OriginalNewFiles(filename_1, filename_2):
    with open(filename_1) as file1:
        file1 = [line.strip() for line in file1]

    with open(filename_2) as file2:
        file2 = [line.strip() for line in file2]
    # find the positions of the blocks in the files
    print(blocks_are_identical(formatted_commands, file1, file2))
    print('minimal edit distance: ', minimal_edit_distance(file1, file2))
    print('total cost from diff: ', total_cost(formatted_commands))
    print(formatted_commands)
    lcs_table = lcs(file1, file2)
    nbr_common_lines = lcs_table[len(file1)][len(file2)][0]
    print('LCS: ', nbr_common_lines)
    file1_alterations, file2_alterations = 0, 0
    for command in formatted_commands:
        file1_alterations += command[1] - command[0]
        file2_alterations += command[4] - command[3]
    if len(file1) - file1_alterations != nbr_common_lines or len(file2) - file2_alterations != nbr_common_lines:
        print('Does not add up')
    else:
        print('LCS (unchanged lines) + total lines changed = total file size')

    back_traces = [[column[1] for column in row] for row in lcs_table]
    for row in back_traces:
        print(*row)
    def find_common_lines(i, j):
        if i == 1 or j == 1:
            yield [], []
        if '\\' in back_traces[i][j]:
            for pair in find_common_lines(i - 1, j - 1):
                print(pair)
                if file1[i] == file2[j]:
                    pair[0].append(i)
                    pair[1].append(j)
                    yield(pair[0], pair[1])

        if '<<' in back_traces[i][j]:
            find_common_lines(i, j - 1)
            # for pair in find_common_lines(i, j - 1):
            #     if file1[i] == file2[j]:
            #         return pair[0].append(i), pair[1].append(j)
        if '^^' in back_traces[i][j]:
            find_common_lines(i - 1, j)
            # for pair in find_common_lines(i - 1, j):
            #     if file1[i] == file2[j]:
            #         return pair[0].append(i), pair[1].append(j)
    print(list(find_common_lines(len(file1), len(file2))))
    # print(list(find_common_lines(len(file1), len(file2))))
    ####################################################################################
    # output_diff
    # for i, command in enumerate(formatted_commands):
    #     print(diffs[i])
    #     if 'a' in command:
    #         output_start = command[3]
    #         output_end = command[4]
    #         for line in file2[output_start:output_end]:
    #             print('>', line)
    #     if 'd' in command:
    #         output_start = command[0]
    #         output_end = command[1]
    #         for line in file1[output_start:output_end]:
    #             print('<', line)
    #     if 'c' in command:
    #         output_start_l = command[0]
    #         output_end_l = command[1]
    #         for line in file1[output_start_l:output_end_l]:
    #             print('<', line)
    #         print('---')
    #         output_start_r = command[3]
    #         output_end_r = command[4]
    #         for line in file2[output_start_r:output_end_r]:
    #             print('>', line)
    ###################################################################################
    # output_unmodified_from_original########################################################
    # ranges = []
    # for command in formatted_commands:
    #     if 'd' in command:
    #         for i in range(command[0], command[1]):
    #             ranges.append(i)
    #     if 'c' in command:
    #         for i in range(command[0], command[1]):
    #             ranges.append(i)
    #
    # common_line = True
    # for i, line in enumerate(file1):
    #     if i in ranges and common_line == True:
    #         common_line = False
    #         print('...')
    #     if i not in ranges:
    #         common_line = True
    #         print(line)
    # output_unmodified_from_new############################################################
    # ranges = []
    # for command in formatted_commands:
    #     if 'a' in command:
    #         for i in range(command[3], command[4]):
    #             ranges.append(i)
    #     if 'c' in command:
    #         for i in range(command[3], command[4]):
    #             ranges.append(i)
    #
    # common_line = True
    # for i, line in enumerate(file2):
    #     if i in ranges and common_line == True:
    #         common_line = False
    #         print('...')
    #     if i not in ranges:
    #         common_line = True
    #         print(line)
    ###############################################################################


def blocks_are_identical(formatted_commands, file1, file2):
    # Find positions of blocks in files
    left_block_ranges = []
    right_block_ranges = []
    if len(formatted_commands) == 1:
        left_block_ranges.append((0, formatted_commands[0][0]))
        right_block_ranges.append((0, formatted_commands[0][3]))
    else:
        for i in range(len(formatted_commands) - 1):
            left_block_ranges.append((formatted_commands[i][1], formatted_commands[i + 1][0]))
            right_block_ranges.append((formatted_commands[i][4], formatted_commands[i + 1][3]))

    # print(left_block_ranges, right_block_ranges)
    # check if corresponding blocks in each file have the same content
    for i in range(len(left_block_ranges)):
        left_block = file1[left_block_ranges[i][0]:left_block_ranges[i][1]]
        right_block = file2[right_block_ranges[i][0]:right_block_ranges[i][1]]
        # print(left_block, right_block)
        if left_block != right_block:
            print('Blocks contain different lines')
            return False

    return True

def minimal_edit_distance(file1, file2):
    print(file1)
    insertion_cost, deletion_cost = 1, 1
    change_cost = 2

    # initialise distance
    distance = [[(0, []) for _ in range(len(file2) + 1)] for _ in range(len(file1) + 1)]
    len_f2 = len(file2) + 1
    len_f1 = len(file1) + 1

    # initialise first row and column
    for i in range(1, len_f1):
        distance[i][0] = i, ['|']
    for j in range(1, len_f2):
        distance[0][j] = j, ['-']

    d = {}
    for i in range(1, len_f1):
        for j in range(1, len_f2):
            d['-'] = distance[i][j - 1][0] + deletion_cost
            d['|'] = distance[i - 1][j][0] + insertion_cost
            if file2[j - 1] == file1[i - 1]:
                d['/'] = distance[i - 1][j - 1][0]
            else:
                d['/'] = distance[i - 1][j-1][0] + change_cost

            min_cost = min(d.values())
            distance[i][j] = min_cost, [operation for operation in d if d[operation] == min_cost]

    # return bottom right corner
    for row in distance:
        print(row)
    min_operations = distance[len_f1 - 1][len_f2 - 1][0]
    print(min_operations)
    return min_operations

def lcs(file1, file2):
    nbr_rows = len(file1) + 1
    nbr_cols = len(file2) + 1
    table = [[(0, []) for _ in range(nbr_cols)] for _ in range(nbr_rows)]

    d = {}
    for i in range(1, nbr_rows):
        table[i][0] = 0, []
    for j in range(1, nbr_cols):
        table[0][j] = 0, []

    for i in range(1, nbr_rows):
        for j in range(1, nbr_cols):
            if file1[i-1] == file2[j-1]:
                d["\\"] = table[i - 1][j - 1][0] + 1
            else:
                d['<<'] = table[i][j - 1][0]
                d['^^'] = table[i - 1][j][0]

            max_subsequence = max(d.values())
            table[i][j] = (max_subsequence, [key for key in d.keys() if d[key] == max_subsequence])

    # for row in table:
    #     print(row)
    return table


def total_cost(formatted_commands):
    cost = 0
    for command in formatted_commands:
        if 'a' in command:
            cost += command[4] - command[3]
        if 'd' in command:
            cost += command[1] - command[0]
        if 'c' in command:
            cost += command[1] - command[0]
            cost += command[4] - command[3]

    return cost

OriginalNewFiles('file_1_1.txt', 'file_1_2.txt')
