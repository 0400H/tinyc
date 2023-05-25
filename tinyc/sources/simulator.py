#!/usr/bin/python3

import argparse
import os, sys, time


def get_input(msg):
    return input(msg)

def read_file(file_path):
    with open(file_path, 'r') as fp:
        return fp.readlines()


class simulator(object):
    def __init__(self, verbose):
        self.verbose = verbose
        # assemb
        self.code = []
        self.comment_mark = ";%"
        self.label_table = {}
        self.func_table = {}
        # run
        self.xip = 0
        self.stack = []
        self.var_table = {}
        # tui display
        self.tui_enable = False
        self.tui_pause = False
        self.code_lines_num = 24
        self.output_lines_num = 8
        self.output = []

    def assemb(self, asm_file, add_main):
        if not asm_file:
            raise Exception("Wrong asm file path")

        if add_main:
            self.code.append(['', '$main', ''])
            self.code.append(['', 'exit', '~'])

        latest_code = None
        code_lines = read_file(asm_file)
        for line in code_lines:
            line = line.strip()
            if line == "" or line[0] in self.comment_mark:
                continue

            if ":" == line[-1]:            # for label and func dec
                tag = line[:-1]
                if latest_code:
                    latest_code[0] += "," + tag
                else:
                    latest_code = self.new_code()
                    latest_code[0] = tag
                    if line[0] == "_":
                        self.label_table[tag] = len(self.code)
                    else:
                        name = tag[tag.find("@")+1:]
                        self.func_table[name] = len(self.code)
            elif len("ENDFUNC") < len(line) and "ENDFUNC" == line[:len("ENDFUNC")]:
                if latest_code:
                    latest_code[0] += ",ENDFUNC"
                else:
                    latest_code = self.new_code()
                    latest_code[0] = "ENDFUNC"
                latest_code[1] = "ret"
            else:                      # for op
                if not latest_code:
                    latest_code = self.new_code()
                idx = line.find(" ")
                if idx < 0:
                    latest_code[1] = line
                else:
                    op, arg = line[:idx].strip(), line[idx:].strip()
                    if '.arg' in op or '.var' in op:
                        op = op[-3:]
                    latest_code[1] = op
                    latest_code[2] = arg

            if self.append_code(latest_code):
                latest_code = None
                continue

        self.code.append(["", "exit", "0"])
        if self.verbose:
            for line in self.code:
                print(line)

    def run(self, tui_mode):
        if tui_mode:
            self.tui_enable = True
            if tui_mode > 1:
                self.tui_pause = True

        self.xip = 0
        self.stack.clear()

        while True:
            self.display()
            _, op, arg = self.code[self.xip]
            if op[0] == '$':
                op, arg = "call", op[1:]
            try:
                dialect = eval("self.do_" + op)
                dialect(arg)
            except NameError:
                self.run_error("Unknown instruction: %s" % (op))
            self.xip += 1
        self.tui_enable = False

    def display(self):
        if self.tui_enable:
            if os.system("clear"):
                os.system('cls')
            print("%32s%-40s|  %-10s  |  Bind Var" % ("", "Code", "Stack"))
            stack_size = len(self.stack)
            j = 0
            for i in range(max(self.xip+1-self.code_lines_num, 0), \
                           max(self.xip+1, self.code_lines_num) ):
                label, line = "", ""
                if i < len(self.code):
                    label, op, arg = self.code[i]
                    line = self.trim(op + " " + arg, 40)
                    label = self.trim(label, 28) + ":"
                point = " ->" if i == self.xip else ""
                st = self.stack[j] if j < stack_size else ""
                st = "(RetInfo)" if type(st) is tuple else str(st)
                stvar = self.var_table.get(j, "")
                if j == stack_size - 1:
                    stvar += "<-"
                print("%29s%3s%-40s|  %-10s  |  %s" % \
                    (label, point, line, st, stvar))
                j += 1
            print("***Output***")
            out_size = len(self.output)
            for i in range(max(out_size-self.output_lines_num, 0), \
                        max(out_size, self.output_lines_num) ):
                print(self.output[i] if i < out_size else "")
                if i == out_size and not self.tui_pause:
                    break
            if self.tui_pause:
                if get_input("\npress enter to step, press r to run: ") == "r":
                    self.tui_enable = False
            else:
                if self.tui_enable:
                    # time.sleep(0.01)
                    pass

    def new_code(self):
        return ["","",""]

    def append_code(self, code):
        if code and code[1]:
            self.code.append(code)
            return True
        else:
            return False

    def trim(self, s, size):
        if len(s) > size:
            return s[:size-3] + "..."
        else:
            return s

    def is_valid_identifier(self, ident):
        if ident == "":
            return False
        if not (ident[0].isalpha() or ident[0] == '_'):
            return False
        for ch in ident[1:]:
            if not (ch.isalnum() or ch == '_'):
                return False
        return True

    def table_has_key(self, table, key):
        return key in table

    def run_error(self, msg="Wrong instruction format"):
        self.code[self.xip][0] = "**%s**" % msg
        self.output.append(msg)
        self.display()
        exit(-1)

    def run_check(self, var_table, arg):
        if not self.is_valid_identifier(arg) or self.table_has_key(var_table, arg):
            self.run_error("Wrong arg name: %s" % (arg))

    def do_call(self, func_name):
        arg_list = []
        code_idx = self.func_table[func_name]
        if self.code[code_idx][1] == "arg":
            arg_list = self.code[code_idx][2].split(',')

        stack_size, arg_nums = len(self.stack), len(arg_list)
        self.stack.append((arg_nums, self.xip, self.var_table))
        self.xip = code_idx if len(arg_list) else code_idx -1

        var_table = {}
        for addr, arg in enumerate(arg_list, stack_size-arg_nums):
            arg = arg.strip()
            self.run_check(var_table, arg)
            var_table[arg] = addr
            var_table[addr] = arg
        self.var_table = var_table

    def do_var(self, arg):
        if arg == "":
            return
        for var in arg.split(','):
            var = var.strip()
            self.run_check(self.var_table, var)
            self.var_table[var] = len(self.stack)
            self.var_table[len(self.stack)] = var
            self.stack.append("/")

    def do_push(self, arg):
        try:
            arg = int(arg)
        except ValueError:
            try:
                arg = self.stack[self.var_table[arg]]
            except KeyError:
                self.run_error("Undefined variable")
            if type(arg) is not int:
                self.run_error("Cannot push uninitialed value")
        self.stack.append(arg)

    def do_pop(self, arg):
        value = self.stack.pop()
        if arg == "":
            return
        if type(value) is not int:
            self.run_error("Cannot pop non-number value to variable")
        try:
            self.stack[self.var_table[arg]] = value
        except KeyError:
            self.run_error("Undefined variable")

    def do_exit(self, arg):
        exit_code = 0
        if arg == "~":
            exit_code = self.stack[-1]
        elif arg:
            try:
                exit_code = int(arg)
            except ValueError:
                try:
                    exit_code = self.stack[self.var_table[arg]]
                except KeyError:
                    self.run_error("Undefined variable")
        if type(exit_code) is not int:
            self.run_error("Wrong exit code")
        if self.tui_enable:
            self.display()
        exit(exit_code)

    def do_add(self, arg):   self.stack[-2] += self.stack[-1]; self.stack.pop()
    def do_sub(self, arg):   self.stack[-2] -= self.stack[-1]; self.stack.pop()
    def do_mul(self, arg):   self.stack[-2] *= self.stack[-1]; self.stack.pop()
    def do_div(self, arg):   self.stack[-2] /= self.stack[-1]; self.stack.pop()
    def do_mod(self, arg):   self.stack[-2] %= self.stack[-1]; self.stack.pop()
    def do_and(self, arg):   self.stack[-2] = int(self.stack[-2]!=0 and self.stack[-1]!=0); self.stack.pop()
    def do_or(self, arg):    self.stack[-2] = int(self.stack[-2]!=0 or  self.stack[-1]!=0); self.stack.pop()
    def do_cmpeq(self, arg): self.stack[-2] = int(self.stack[-2]==self.stack[-1]);self.stack.pop()
    def do_cmpne(self, arg): self.stack[-2] = int(self.stack[-2]!=self.stack[-1]);self.stack.pop()
    def do_cmpgt(self, arg): self.stack[-2] = int(self.stack[-2]>self.stack[-1]); self.stack.pop()
    def do_cmplt(self, arg): self.stack[-2] = int(self.stack[-2]<self.stack[-1]); self.stack.pop()
    def do_cmpge(self, arg): self.stack[-2] = int(self.stack[-2]>=self.stack[-1]);self.stack.pop()
    def do_cmple(self, arg): self.stack[-2] = int(self.stack[-2]<=self.stack[-1]);self.stack.pop()
    def do_neg(self, arg):   self.stack[-1] = -self.stack[-1]
    def do_not(self, arg):   self.stack[-1] = int(not self.stack[-1])

    def do_jmp(self, label):
        try:
            # note: here we set self.xip just befor the label,
            #       and when back to run(), we do self.xip += 1
            self.xip = self.label_table[label] - 1
        except KeyError:
            self.run_error("Wrong label")

    def do_jz(self, label):
        new_xip = None
        try:
            # set self.xip just befor the label,
            # when back to run(), do self.xip += 1
            new_xip = self.label_table[label] - 1
        except KeyError:
            self.run_error("Wrong label")
        if self.stack.pop() == 0:
            self.xip = new_xip

    def do_ret(self, arg):
        retval = None
        if arg == "~":
            retval = self.stack[-1]
        elif arg:
            try:
                retval = int(arg)
            except ValueError:
                try:
                    retval = self.stack[self.var_table[arg]]
                except KeyError:
                    self.run_error("Undefined variable")
        else:
            retval = '/'
        i = len(self.stack) - 1
        while type(self.stack[i]) is not tuple:
            i -= 1
        argc, self.xip, self.var_table = self.stack[i]
        del self.stack[i-argc:]
        self.stack.append(retval)

    def do_print(self, fmt):
        if len(fmt) < 2 or fmt[0] != fmt[-1] or fmt[0] not in '"\'':
            self.run_error("Format string error")
        argc = fmt.count("%d")
        out = fmt[1:-1] % tuple(self.stack[len(self.stack)-argc:])
        print(out)
        self.output.append(out)
        del self.stack[len(self.stack)-argc:]

    def do_readint(self, msg):
        if len(msg) < 2 or msg[0] != msg[-1] or msg[-1] not in '"\'':
            self.run_error("Message string error")
        msg = msg.strip('"').strip("'")
        if self.tui_enable:
            self.display()
        string = get_input(msg)
        try:
            value = int(string)
        except ValueError:
            value = 0
        self.stack.append(value)
        self.output.append("\n  " + msg + str(value))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, default=None, help="asm file path")
    parser.add_argument("-a", "--add_main", type=int, default=0, help="add $main on the top of code")
    parser.add_argument("-t", "--tui", type=int, default=0, help="tui mode: 0(not tui), 1(tui auto run), 2(tui pause)")
    parser.add_argument("-v", "--verbose", type=int, default=0, help="verbose")
    args = parser.parse_args()

    sim = simulator(args.verbose)
    sim.assemb(args.file, args.add_main)
    sim.run(args.tui)
