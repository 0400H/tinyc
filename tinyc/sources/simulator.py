#!/usr/bin/python3

import argparse
import os, sys, time


def get_input(msg):
    return input(msg)

def read_file(file_path):
    with open(file_path, 'r') as fp:
        return fp.readlines()


class simulator(object):
    def __init__(self):
        self.xip = 0
        self.code = []
        self.stack = []
        self.var_table = {}
        self.label_table = {}
        self.func_table = {}
        self.output = []
        self.comment_mark = ";%"
        self.tui_enable = False
        self.tui_pause = False
        self.code_lines_num = 24
        self.output_lines_num = 8

    def trim(self, s, size):
        if len(s) > size:
            return s[:size-3] + "..."
        else:
            return s

    def display(self):
        if os.system("clear"):
            os.system('cls')
        print("%32s%-40s|  %-10s  |  Bind Var" % ("", "Code", "Stack"))
        stack_size = len(self.stack)
        j = 0
        for i in range(max(self.xip+1-self.code_lines_num, 0), \
                       max(self.xip+1, self.code_lines_num) ):
            label, line = "", ""
            if i < len(self.code):
                label, dire, arg = self.code[i]
                line = self.trim(dire + " " + arg, 40)
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

    def check_label(self, label):
        if label == "":
            return False
        func, sep, func_name = label.partition(' @')
        if sep:
            if func.strip() != 'FUNC' \
                or not self.is_valid_identifier(func_name) \
                or self.table_has_key(self.func_table, func_name):
                return False
            else:
                self.func_table[func_name] = len(self.code)
                return True
        else:
            if not self.is_valid_identifier(label) \
                or self.table_has_key(self.func_table, label) \
                or self.table_has_key(self.label_table, label):
                return False
            else:
                self.label_table[label] = len(self.code)
                return True

    def assemb_error(self, line, msg):
        self.display()
        print(line)
        print("^^^Error at last line: %s" % msg)
        exit(-1)

    def check_line_label(self, label, line):
        if not self.check_label(label):
            self.assemb_error(line, "Wrong label")

    def assemb(self, asm_file, tui_mode):
        if tui_mode:
            self.tui_enable = True
            if "p" in tui_mode:
                self.tui_pause = True
            if "a" in tui_mode:
                self.code.append(('', '$main', ''))
                self.code.append(('', 'exit', '~'))
        label = ""
        code_lines = read_file(asm_file)
        for line in code_lines:
            line = line.strip()
            if line == "" or line[0] in self.comment_mark:
                continue
            _label, sep, ist = line.partition(':')
            if sep and _label.find('"') == -1 and _label.find("'") == -1:
                _label, ist = _label.strip(), ist.strip()
                self.check_line_label(_label, line)
                label = '%s,%s' % (label, _label) if label else _label
                if ist == "" or ist[0] in self.comment_mark:
                    continue
            elif len(line) >= 7 and line[:7] == 'ENDFUNC':
                label = '%s,%s' % (label, 'ENDFUNC') if label else 'ENDFUNC'
                ist = 'ret'
            else:
                ist = line
            dire, sep, arg = ist.partition(' ')
            if len(dire) > 4 and \
                (dire[-4:] == '.arg' or dire[-4:] == '.var'):
                dire = dire[-3:]
            self.code.append([label, dire, arg.strip()])
            label = ""
        self.code.append(('', 'exit', '0'))

    def run_error(self, msg="Wrong instruction format"):
        self.code[self.xip][0] = "**%s**" % msg
        self.output.append(msg)
        self.display()
        exit(-1)

    def check_identifier(self, identifier):
        if not self.is_valid_identifier(identifier):
            self.run_error("Wrong identifier: %s" % (identifier))

    def call(self, func_name):
        func_entry = None
        arg_list = []
        var_table = {}

        try:
            func_entry = self.func_table[func_name]
        except KeyError:
            self.run_error("Undefined function")

        if self.code[func_entry][1] == "arg":
            arg_list = self.code[func_entry][2].split(',')
        stack_size, arg_nums = len(self.stack), len(arg_list)

        for addr, arg in enumerate(arg_list, stack_size - arg_nums):
            arg = arg.strip()
            if not self.is_valid_identifier(arg) or self.table_has_key(var_table, arg):
                self.run_error("Wrong arg name")
            var_table[arg] = addr
            var_table[addr] = arg

        self.stack.append((arg_nums, self.xip, self.var_table))
        self.var_table = var_table
        self.xip = func_entry if arg_nums else func_entry -1

    def run(self):
        self.xip = 0
        self.stack.clear()
        while True:
            if self.tui_enable:
                self.display()
            label, dire, arg = self.code[self.xip]
            if dire[0] == '$':
                dialect, arg = self.call, dire[1:]
                self.check_identifier(arg)
            else:
                self.check_identifier(dire)
                try:
                    dialect = eval("self.do_" + dire)
                except NameError:
                    self.run_error("Wrong identifier: %s" % (dire))
            dialect(arg)
            self.xip += 1

    def do_var(self, arg):
        if arg == "": return
        for var in arg.split(','):
            var = var.strip()
            if not self.is_valid_identifier(var) or self.table_has_key(self.var_table, var):
                self.run_error("Wrong var name")
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
    parser.add_argument("-f", "--file", type=str, help="asm file path")
    parser.add_argument("-t", "--tui", type=str, default=None, help="tui mode: None(not tui), a(add main), p(pause)")
    args = parser.parse_args()

    sim = simulator()
    sim.assemb(args.file, args.tui)
    sim.run()
