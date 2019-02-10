# Module is made for representation of liner program,
# both standard and slack form
# the forms of representation could be changed by appropriate functions
# simplex method solves problem
# In all cases all variables: X1, ... , Xn are >= 0

import copy
import numpy as np


# returns a list of opposite elements of input list
def make_opposite_list(a):
    return [-e for e in a]


# Scalar product
def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


# Returns a j column of matrix
def column(a, j):
    return [row[j] for row in a]


# returns string "c1X1 + .. + cnXn" when [c1, ... ,cn] list given
def make_expression(coefficients_list):
    if len(coefficients_list) == 0:
        return "Expression does not have any variables or coefficients"
    else:
        expression = ""
        for i in range(len(coefficients_list)):
            if i == 0:
                expression += str(coefficients_list[i]) + '*x{} '.format(i+1)
                continue

            if coefficients_list[i] < 0:
                expression += (str(coefficients_list[i]) + '*x{} '.format(i+1))

            if coefficients_list[i] >= 0:
                expression += ('+' + str(coefficients_list[i]) + '*x{} '.format(i+1))

    return expression


# Linear problem  form representation:
#     E: c_j * x_j -> MAX
#     E: a_ij * X_j < b_i , x_j > 0
class LinearProgram:
    def __init__(self, c=None, b=None, a=None, signs=None, maximization=True,):
        if a is None:
            self.a = []
        else:
            self.a = a
        if b is None:
            self.b = []
        else:
            self.b = b
        if c is None:
            self.c = []
        else:
            self.c = c
        if signs is None:
            self.signs = []
        else:
            self.signs = signs
        self.maximization = maximization

    def __str__(self):

        linear_program = [make_expression(self.c)]
        if self.maximization:
            linear_program.append(" --> MAX \n\n")
        else:
            linear_program.append(" --> MIN \n\n")

        for i in range(len(self.a)):
            linear_program.append("\t{}) ".format(i+1))
            linear_program.append(make_expression(self.a[i]) + " " + str(self.signs[i]) + " " + str(self.b[i]) + "\n")

        linear_program.append("\t{}) ".format(len(self.a) + 1))
        for i in range(len(self.c)-1):
            linear_program.append("x{} , ".format(i+1))
        linear_program.append("x{} >= 0".format(len(self.c)))

        return "".join(linear_program)

    def __repr__(self):

        linear_program_repr = [str(self.c) + " , ["]
        for row in self.a:
            linear_program_repr.append(str(row) + ' ')
        linear_program_repr.append("] , " + str(self.signs) + " , ")
        linear_program_repr.append(str(self.b) + " , ")
        linear_program_repr.append("maximization = " + str(self.maximization))

        return "".join(linear_program_repr)

    @classmethod
    def from_input(cls):
        c, b, signs = [], [], []

        for i in range(int(input("How many variables does goal function have: "))):
            c.append(int(input("Type in a value of coefficient for {} variable: ".format(i+1))))

        optimization_type = input("Chose want you want to do with function: 'MIN' for minimization or "
                                  "'MAX' for maximization: ")
        optimization_type.upper()
        if optimization_type.upper() == 'MAX':
            maximization = True
        else:
            maximization = False

        restrictions_number = int(input("How many restriction you want to add: "))
        a = [[] * i for i in range(restrictions_number)]
        for i in range(restrictions_number):
            print("Restriction no. {}".format(i + 1))
            for j in range(len(c)):
                a[i].append(int(input("Type in a value for coefficient for {} variable: ".format(j + 1))))
            signs.append(input("Type in a relation sign: "))
            b.append(input("Type in a constant term: "))

        return cls(c, b, a, signs, maximization)


# In Standard form:
#     - optimization type must be maximization
#     - all restriction must be '<='
class StandardForm(LinearProgram):
    def __init__(self, c=None, b=None, a=None, signs=None, maximization=True,):

        if signs is not None and any(sign != "<=" for sign in signs):
            raise ValueError

        if not maximization:
            raise ValueError

        super().__init__(c, b, a, signs, True)

    @classmethod
    def from_input(cls):
        print("\tIn standard form: \n- goal function is maximize\n- all restrictions are '<='\n")
        c, b, signs = [], [], []

        for i in range(int(input("How many variables does goal function have: "))):
            c.append(int(input("Type in a value of coefficient for {} variable: ".format(i + 1))))

        restrictions_number = int(input("How many restriction you want to add: "))
        a = [[] * i for i in range(restrictions_number)]
        for i in range(restrictions_number):
            print("Restriction no. {}".format(i + 1))
            for j in range(len(c)):
                a[i].append(int(input("Type in a value for coefficient for {} variable: ".format(j + 1))))
            b.append(input("Type in a constant term: "))

        for i in range(restrictions_number):
            signs.append("<=")

        return cls(c, b, a, signs, True)

    @classmethod
    def make_standard_form(cls, linear_program):
        if type(linear_program) != LinearProgram:
            raise ValueError

        a, b, c, signs = [], [], [], []
        a_size = len(linear_program.a)

        if not linear_program.maximization:
            for j in range(len(linear_program.c)):
                c.append(linear_program.c[j] * (-1))
        else:
            for j in range(len(linear_program.c)):
                c.append(linear_program.c[j])

        for i in range(len(linear_program.signs)):
            if linear_program.signs[i] == '=':
                a_size += 1

        for i in range(len(linear_program.signs)):
            if linear_program.signs[i] == '=':
                signs.append('<=')
                signs.append('<=')
                b.append(linear_program.b[i])
                b.append(linear_program.b[i] * (-1))
                a.append(linear_program.a[i])
                a.append((make_opposite_list(linear_program.a[i])))

            elif linear_program.signs[i] == '>=':
                signs.append('<=')
                b.append(linear_program.b[i] * (-1))
                a.append((make_opposite_list(linear_program.a[i])))

            else:
                signs.append('<=')
                b.append(linear_program.b[i])
                a.append(linear_program.a[i])

        return cls(c, b, a, signs, True)


# In Slack form:
#   - all restrictions must be "="
#   - when restriction was changed slack variable must be added with coefficient of value 0
class SlackForm(LinearProgram):
    def __init__(self, c=None, b=None, a=None, signs=None, maximization=True, slack_variables_indexes=None):
        if signs is not None and any(sign != "=" for sign in signs):
            raise ValueError

        if not maximization:
            raise ValueError

        super().__init__(c, b, a, signs, maximization)
        if slack_variables_indexes is None:
            self.cb_indexes = []
        else:
            self.cb_indexes = slack_variables_indexes

    def __repr__(self):
        return super().__repr__() + ', [' + str(self.cb_indexes) + ']'

    @classmethod
    def from_input(cls):
        c, b, signs = [], [], []

        for i in range(int(input("How many variables does goal function have (without slack variables): "))):
            c.append(int(input("Type in a value of coefficient for {} variable: ".format(i + 1))))

        restrictions_number = int(input("How many restriction you want to add: "))
        a = [[] * i for i in range(restrictions_number)]
        for i in range(restrictions_number):
            print("Restriction no. {}".format(i + 1))
            for j in range(len(c)):
                a[i].append(int(input("Type in a value for coefficient for {} variable: ".format(j + 1))))
            b.append(input("Type in a constant term: "))

        for i in range(restrictions_number):
            signs.append("<=")

        return cls().make_slack_form(StandardForm(c, b, a, signs, True))

    @classmethod
    def make_slack_form(cls, standard_form):

        a = copy.deepcopy(standard_form.a)
        b = copy.deepcopy(standard_form.b)
        c = copy.deepcopy(standard_form.c)
        cb_indexes, signs = [], []

        for i in range(len(standard_form.signs)):
            signs.append("=")
            c.append(0)
            cb_indexes.append(len(standard_form.c) + i)
            for j in range(len(standard_form.signs)):
                if j == i:
                    a[i].append(1)
                else:
                    a[i].append(0)

        del standard_form
        return cls(c, b, a, signs, True, cb_indexes)


class SimplexTable(SlackForm):
    def __init__(self, c=None, b=None, a=None, cb_indexes=None):

        super().__init__(c, b, a, None, True, cb_indexes)

        self.cb = []
        self.z = []
        self.c_z = []

        if self.cb_indexes is not None:
            for j in self.cb_indexes:
                self.cb.append(c[j])

        for j in range(len(self.c)):
            self.z.append(dot(self.cb, column(self.a, j)))
            self.c_z.append(self.c[j] - self.z[j])

    @classmethod
    def make_simplex_table(cls, slack_form):
        a = copy.deepcopy(slack_form.a)
        b = copy.deepcopy(slack_form.b)
        c = copy.deepcopy(slack_form.c)
        cb_indexes = copy.deepcopy(slack_form.cb_indexes)

        del slack_form
        return cls(c, b, a, cb_indexes)

    def __str__(self):

        line = "-" * ((len(self.c) + 2) * 8 + 1) + "\n"

        simplex_table = ["|  cj\t|"]
        for j in range(len(self.c)):
            simplex_table.append("\t{}\t|".format(self.c[j]))
        simplex_table.append("\tbi\t|\n")
        simplex_table.append(line)

        simplex_table.append("|  cb\t")
        for i in range(len(self.c)):
            simplex_table.append("|\tx{}\t".format(i+1))
        simplex_table.append('|\tbi\t|\n' + line)

        for i in range(len(self.cb)):
            simplex_table.append('|{}\t|x{}\t'.format(self.cb[i], self.cb_indexes[i]+1))
            for j in range(len(self.a[i])):
                simplex_table.append("|{:>7.4f}".format(self.a[i][j]))
            simplex_table.append('|{:>7.4f}|\n'.format(self.b[i]))
        simplex_table.append(line)

        simplex_table.append('|  zj\t')
        for j in range(len(self.z)):
            simplex_table.append('|{:>7.4f}'.format(self.z[j]))
        simplex_table.append("|\t\t|\n")

        simplex_table.append('| cj-zj\t')
        for j in range(len(self.c_z)):
            simplex_table.append('|{:>7.4f}'.format(self.c_z[j]))
        simplex_table.append("|\t\t|\n")

        return ''.join(simplex_table)

    @classmethod
    def from_input(cls):
        pass

    def new_simplex_table(self):
        # entry condition
        e = 0
        max_coefficient = self.c_z[0]
        for j in range(len(self.c_z)):
            if self.c_z[j] > max_coefficient:
                max_coefficient = self.c_z[j]
                e = j

        ratio = []
        for i in range(len(self.cb_indexes)):
            ratio.append(self.b[i] / column(self.a, e)[i])

        # leaving condition
        l = 0
        min_ratio = ratio[0]
        for i in range(len(ratio)):
            if ratio[i] < min_ratio:
                min_ratio = ratio[i]
                l = i

        B = [[] * i for i in range(len(self.cb))]
        for j in range(len(self.cb)):
            for i in self.cb_indexes:
                if i != self.cb_indexes[l]:
                    B[j].append(self.a[j][i])
                else:
                    B[j].append(self.a[j][e])

        # ToDO: check if dot works
        B_inv = np.linalg.inv(B)

        a = np.zeros((len(self.b), len(self.c)))

        for i in range(len(a)):
            for j in range(len(a[0])):
                for k in range(len(a)):
                    a[i][j] += B_inv[i][k] * self.a[k][j]

        for i in range(len(a)):
            for j in range(len(a[0])):
                self.a[i][j] = a[i][j]

        new_b = []
        for i in range(len(self.b)):
            new_b.append(dot(B_inv[i], self.b))

        self.b = new_b

        self.cb[l] = self.c[e]
        self.cb_indexes[l] = e

        for j in range(len(self.c)):
            self.z[j] = dot(self.cb, column(self.a, j))
            self.c_z[j] = self.c[j] - self.z[j]

    def solve(self, show=False):
        if show:
            print(self, '\n')

        while True:

            self.new_simplex_table()
            if show:
                print(self, '\n')

            if all(coefficient <= 0 for coefficient in self.c_z):
                solution = dot(self.cb, self.b)
                break

        if show:
            for i in range(len(self.cb)):
                print("x{} = {} ".format(self.cb_indexes[i], self.b[i]))
            for i in range(len(self.cb) - 1):
                print('x{} + '.format(self.cb_indexes), end='')
            print("x{} = {}".format(self.cb_indexes[-1], solution))

        return solution, self.cb, self.cb_indexes
