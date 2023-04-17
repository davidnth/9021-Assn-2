import re
def is_valid_syntax(line):
    if valid_a(line) or valid_c(line) or valid_d(line):
        return True

    return False
def valid_d(line):
    search = re.search('^(0|[1-9]\d*)(?:,([1-9]\d*))?d(?:0|[1-9]\d*)$', line)
    if not search:
        return False
    left_range = search.groups()
    if left_range[0] and left_range[1] and int(left_range[1]) <= int(left_range[0]):
        return False

    return True

def valid_a(line):
    search = re.search('^(?:0|[1-9]\d*)a(0|[1-9]\d*)(?:,([1-9]\d*))?$', line)
    if not search:
        return False
    right_range = search.groups()
    if right_range[0] and right_range[1] and int(right_range[1]) <= int(right_range[0]):
        return False
    return True

def valid_c(line):
    search = re.search('^(0|[1-9]\d*)(?:,([1-9]\d*))?c(0|[1-9]\d*)(?:,(0|[1-9]\d*))?$', line)
    if not search:
        return False

    left_ranges = search.groups()[:2]
    right_ranges = search.groups()[2:]
    if left_ranges[0] and left_ranges[1] and int(left_ranges[1]) <= int(left_ranges[0]):
        return False
    if right_ranges[0] and right_ranges[1] and int(right_ranges[1]) <= int(right_ranges[0]):
        return False

    return True

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
class DiffCommandsError(ValueError):
    pass
class DiffCommands:

    def __init__(self, diff_txtfile):
        try:
            self.original_diff = []
            self.formatted_commands = []
            with open(diff_txtfile, 'r') as file:
                for line in file:
                    if not is_valid_syntax(line):
                        raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
                    line = line.strip()
                    self.original_diff.append(line)
                    self.format_command(line, self.formatted_commands)
                    if not valid_sequence(self.formatted_commands):
                        raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')
        except DiffCommandsError as e:
            raise e

    def __str__(self):
        return '\n'.join(self.original_diff)
    def format_command(self, line, arr):
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
    def valid_sequence(self, formatted_commands):
        for i in range(len(formatted_commands)):
            if i == 0:
                if not (formatted_commands[i][0] >= 0 and formatted_commands[i][3] >= 0 and \
                        formatted_commands[i][0] == formatted_commands[i][3]):
                    # print('invalid first command')
                    return False
                continue

                # Check starting range of next command is strictly greater than end range
                # of previous command on both sides
            if not (formatted_commands[i][0] > formatted_commands[i - 1][1] and \
                    formatted_commands[i][3] > formatted_commands[i - 1][4]):
                # print('sequence ranges overlap')
                return False

            if not (formatted_commands[i][0] - formatted_commands[i - 1][1] == \
                    formatted_commands[i][3] - formatted_commands[i - 1][4]):
                # print('different block size')
                return False

        return True

class OriginalNewFiles:
    def __init__(self, file1, file2):
        with open(file1) as file1:
            self.file_1 = [line.strip() for line in file1]
        with open(file2) as file2:
            self.file_2 = [line.strip() for line in file2]
        self.lcs_table = self.lcs(self.file_1, self.file_2)

    def is_a_possible_diff(self, diff_obj):
        if not self.blocks_are_identical(diff_obj.formatted_commands, self.file_1, self.file_2):
            return False

        nbr_common_lines = self.lcs_table[len(self.file_1)][len(self.file_2)][0]
        file1_alterations, file2_alterations = 0, 0
        for command in diff_obj.formatted_commands:
            file1_alterations += command[1] - command[0]
            file2_alterations += command[4] - command[3]
        if len(self.file_1) - file1_alterations != nbr_common_lines or len(self.file_2) - file2_alterations != nbr_common_lines:
            # print("LCS between files is different to lines changed in diff")
            return False

        return True

    def blocks_are_identical(self, formatted_commands, file1, file2):
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
                # print('Blocks contain different lines')
                return False

        return True

    def lcs(self, file1, file2):
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
                if file1[i - 1] == file2[j - 1]:
                    d["\\"] = table[i - 1][j - 1][0] + 1
                else:
                    d['<<'] = table[i][j - 1][0]
                    d['^^'] = table[i - 1][j][0]

                max_subsequence = max(d.values())
                table[i][j] = (max_subsequence, [key for key in d.keys() if d[key] == max_subsequence])

        # for row in table:
        #     print(row)
        return table

    def output_diff(self, diff_obj):
        for i, command in enumerate(diff_obj.formatted_commands):
            print(diff_obj.original_diff[i])
            if 'a' in command:
                output_start = command[3]
                output_end = command[4]
                for line in self.file_2[output_start:output_end]:
                    print('>', line)
            if 'd' in command:
                output_start = command[0]
                output_end = command[1]
                for line in self.file_1[output_start:output_end]:
                    print('<', line)
            if 'c' in command:
                output_start_l = command[0]
                output_end_l = command[1]
                for line in self.file_1[output_start_l:output_end_l]:
                    print('<', line)
                print('---')
                output_start_r = command[3]
                output_end_r = command[4]
                for line in self.file_2[output_start_r:output_end_r]:
                    print('>', line)
    def output_unmodified_from_original(self, diff_obj):
        ranges = []
        for command in diff_obj.formatted_commands:
            if 'd' in command:
                for i in range(command[0], command[1]):
                    ranges.append(i)
            if 'c' in command:
                for i in range(command[0], command[1]):
                    ranges.append(i)

        common_line = True
        for i, line in enumerate(self.file_1):
            if i in ranges and common_line:
                common_line = False
                print('...')
            if i not in ranges:
                common_line = True
                print(line)

    def output_unmodified_from_new(self, diff_obj):
        ranges = []
        for command in diff_obj.formatted_commands:
            if 'a' in command:
                for i in range(command[3], command[4]):
                    ranges.append(i)
            if 'c' in command:
                for i in range(command[3], command[4]):
                    ranges.append(i)

        common_line = True
        for i, line in enumerate(self.file_2):
            if i in ranges and common_line:
                common_line = False
                print('...')
            if i not in ranges:
                common_line = True
                print(line)

d = DiffCommands('Diff_1.txt')
pair_of_files = OriginalNewFiles('file_1_1.txt', 'file_1_2.txt')
pair_of_files.output_diff(d)
print(pair_of_files.is_a_possible_diff(d))
print(pair_of_files.lcs_table)