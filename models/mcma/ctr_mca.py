"""
Handle data structure and control flows of the MCMA
"""
import sys      # needed from stdout
import os
# import numpy as np
from crit import Crit


class CtrMca:
    def __init__(self, ana_dir):
        self.ana_dir = ana_dir  # wrk dir for the current analysis
        self.f_payoff = ana_dir + '/payoff.txt'     # file with payoff values
        self.pay_upd = False  # set to true, if current payOff differs from the store one
        self.cr = []        # objects of Crit class, each representing the corresponding criterion
        self.n_crit = 0     # number of defined criteria == len(self.cr)
        self.stages = {'ini': 0, 'utop': 1, 'nad0': 2, 'nad1': 3, 'pref': 4, 'end': 5}
        self.cur_stage = 0  # initialization
        self.cur_cr = None  # cr_index passed to self.set_pref()
        # self.cur_uto = None   # cr-index of currently computed utopia
        # self.cur_nad = None   # cr-index of currently approximated nadir

    def addCrit(self, cr_name, typ, var_name):
        """
        Add definition of a criterion.

        :param cr_name: criterion name
        :type cr_name:  str
        :param var_name: name of the corresponding model variable
        :type var_name:  str
        :param typ: criterion type (either 'min' or 'max')
        :type typ:  str
        :return:  None
        """
        # todo: add checking cr_name duplication
        self.cr.append(Crit(cr_name, var_name, typ))
        self.n_crit = len(self.cr)

    def cr_ind(self, cr_name):  # return index (in self.cr) of criterion having name cr_name
        for (i, crit) in enumerate(self.cr):
            if crit.name == cr_name:
                return i
        raise Exception(f'cr_ind(): unknown criterion name: "{cr_name}".')

    # todo: check, if set_payOff is really needed
    #   used only in rd_payoff (below)?
    '''
    def set_payOff(self, cr_name, utopia=None, nadir=None):   # set the provided utopia/nadir values (if not None)
        print(f'Crit. "{cr_name}": checking update of {utopia=}, {nadir=} values.')
        i = self.cr_ind(cr_name)    # get the criterion index in cr[]
        updated = False
        # todo: add tolerances for checks of old and new values
        if utopia:  # value provided
            if self.cr[i].utopia != utopia:
                updated = True
                print(f'Crit. "{cr_name}": utopia value {cr_name.utopia} updated to {utopia}.')
                self.cr[i].utopia = utopia
        if nadir:  # value provided
            if self.cr[i].nadir != nadir:
                updated = True
                print(f'Crit. "{cr_name}": nadir value {cr_name.nadir} updated to {nadir}.')
                self.cr[i].nadir = nadir
        if updated:
            self.pay_upd = True ???
    '''

    def rd_payoff(self):    # read stored utopia/nadir values and store them as self.cr attributes
        if os.path.exists(self.f_payoff):
            with open(self.f_payoff, "r") as reader:
                print(f"\nReading payoff table stored in file '{self.f_payoff}':")
                n_def = 0
                for n_line, line in enumerate(reader):
                    line = line.rstrip("\n")
                    # print(f'line {line}')
                    words = line.split()
                    n_words = len(words)
                    assert(n_words == 3), f'line {line} has {n_words} instead of the required three.'
                    # todo: don't store every line ?
                    # self.set_payOff(words[0], words[1], words[2])
                    n_def += 1
            assert (self.n_crit == n_def), f'stored payOff table has {n_def} values for {self.n_crit} defined criteria.'
        else:
            print(f"\nFile '{self.f_payoff}' with stored payoff table not available.")

    def prn_payoff(self):   # store current values of utopia/nadir in a file for subsequent use
        # to create a dir: os.makedirs(dir_name, mode=0o755)
        # create file for writing (over-writes previous, if exists)
        print(f'\nCurrent values of the payoff table written to file "{self.f_payoff}":')
        f_payOff = open(self.f_payoff, "w")
        for crit in self.cr:
            line = f'{crit.name} {crit.utopia} {crit.nadir}'
            print(line)
            f_payOff.write(line + '\n')
        f_payOff.close()

    def chk_utopia(self):    # return crit-index of criterion, whose utopia was not computed yet
        for (i, crit) in enumerate(self.cr):
            if not crit.utopia:
                return i
        print(f'All utopia components computed.')
        return -1

    def set_stage(self):
        """Define and return analysis stage; provide (in self.cur_cr) info for mc.set_pref()."""

        # preferences predefined in stages 1, 2, 3 and 4 (A and R used only in stage 4)
        # stage 5: user-defined preferences by A, R; optionally activity to excl. criterion from the Tchebyshev term
        if self.cur_stage == 0:     # initialization
            print('Initialization finished, checking, if all utopia components computed.')
            self.cur_stage = 1
        if self.cur_stage == 1:     # computing utopia
            i_cr = self.chk_utopia()   # check, if all utopias computed
            if i_cr > -1:   # utopia of i_cr-th criterion needs to be computed
                self.cur_cr = i_cr
                print(f'Utopia of criterion "{self.cr[i_cr].name}" shall be computed.')
            else:   # all utopia computed, start 1st stage of nadir approximation
                print('All utopia components computed. Start first stage of nadir approximation.')
                self.cur_stage = 2
                self.cur_cr = 0     # start with 0-th criterion
            return self.cur_stage   # crit activity set in mc_set_pref()
        elif self.cur_stage == 2:  # 1st approximation of Nadir
            if self.cur_cr + 1 < self.n_crit:   # not all crit used?
                self.cur_cr += 1    # use next (not yet used) criterion
                print(f'Appr. Nadir of crit. other than {self.cr[self.cur_cr].name} (stage {self.cur_stage}).')
            else:   # move to the 2nd stage of nadir appr.
                print('Finished first nadir approximations. Start the 2nd nadir approximations.')
                self.cur_stage = 3
                self.cur_cr = 0     # start 2nd nedir appr with 0-th criterion
                raise Exception(f'set_stage(): nadir2 stage NOT implemented yet.')
            return self.cur_stage
        elif self.cur_stage == 3:  # second approximation of Nadir
            raise Exception(f'set_stage(): nadir2 stage NOT implemented yet.')
        elif self.cur_stage > 3:  # second approximation of Nadir
            raise Exception(f'set_stage(): stage {self.cur_stage} NOT implemented yet.')

        print('PayOff table available. Ready to handle preferences.')
        return self.cur_stage

    def set_pref(self):     # set crit attributes (activity, A/R, possibly adjust nadir app).
        assert self.cur_stage > 0, f'CtrMca::set_pref() should not be called for cur_stage {self.cur_stage}.'
        if self.cur_stage == 1:  # set only currently computed utopia criterion to be active
            for (i, crit) in enumerate(self.cr):
                if self.cur_cr == i:
                    crit.is_active = True
                else:
                    crit.is_active = False
            return
        elif self.cur_stage == 2:     # set one crit active in first appr. of Nadir
            print(f'---\nMcma::set_pref(): TESTING for stage: {self.cur_stage}.')
            for (i, crit) in enumerate(self.cr):
                if self.cur_cr == i:
                    crit.is_active = True
                else:
                    crit.is_active = False
            return

        sys.stdout.flush()  # needed for printing exception at the output end
        raise Exception(f'Mcma::set_pref() not implemented yet for stage: {self.cur_stage}.')

    def store_sol(self, crit_val):  # crit_val: dict of values of all criteria
        print(f'Processing criteria values of the current iteration: {crit_val}')
        if self.cur_stage == 1:     # utopia computed for the only one active criterion
            for crit in self.cr:
                val = crit_val.get(crit.name)
                crit.val = val
                if crit.is_active:
                    crit.setUtopia(val)  # utopia computed
                crit.updNadir(self.cur_stage, val)
        elif self.cur_stage == 2:   # update nadir values
            print(f'---\nMcma::store_sol(): TESTING for stage {self.cur_stage}.')
            for crit in self.cr:
                val = crit_val.get(crit.name)
                crit.val = val
                if crit.is_active:  # nothing to store/update
                    print(f'NOT updating nadir for active crit "{crit.name}" = {val}')
                else:
                    crit.updNadir(self.cur_stage, val)   # update nadir value
        else:
            sys.stdout.flush()  # needed for printing exception at the output end
            raise Exception(f'Mcma::store_sol() not implemented yet for stage: {self.cur_stage}.')