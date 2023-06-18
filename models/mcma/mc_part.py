import pyomo.environ as pe       # more robust than using import *


class McMod:
    def __init__(self, mc, m1):
        self.mc = mc    # Mcma class handling data and statues of the MCMA
        self.m1 = m1    # instance of the core model (first block of the aggregate model)

        self.cr_names = []   # names of all criteria
        self.var_names = []  # names of variables defining criteria
        for (i, crit) in enumerate(mc.cr):
            self.cr_names.append(mc.cr[i].name)
            self.var_names.append(mc.cr[i].var_name)

    def mc_itr(self):
        m = pe.ConcreteModel('MC_block')   # instance of the MC-part (second block of the aggregate model)
        act_cr = []     # indices of active criteria
        for (i, crit) in enumerate(self.mc.cr):
            if crit.is_active:
                act_cr.append(i)

        print(f'mc_itr(): stage {self.mc.cur_stage}, {len(act_cr)} active criteria.')
        if self.mc.cur_stage == 1:   # utopia component, selfish optimization
            if len(act_cr) != 1:
                raise Exception(f'mc_itr(): computation of utopia component: {len(act_cr)} active criteria '
                                f'instead of one.')
            id_cr = act_cr[0]
            print(f'\nComputing utopia value of crit "{self.cr_names[id_cr]}" defined by variable '
                  f'"{self.var_names[id_cr]}".')

        # m1_obj = self.m1.component_map(ctype=pe.Objective)  # all objectives of the m1 (core model)

        # link (through constraints) the corresponding variables of the m1 (core) and m (MC-part) models
        m1_vars = self.m1.component_map(ctype=pe.Var)  # all variables of the m1 (core model)
        m.af = pe.Var()     # Achievement Function (AF), to be maximized  (af = caf_min + caf_reg)
        if self.mc.cur_stage == 1:   # utopia component, selfish optimization
            # special case, only one m1 variable used and linked with the AF variable
            # only one criterion active for utopia calculation
            m.af = pe.Var()  # Achievement Function (AF), to be maximized  (af = caf_min + caf_reg)
            var_name = self.var_names[act_cr[0]]    # name of m1-variable representing the active criterion
            m1_var = m1_vars[var_name]  # object of core model var. named m1.var_name
            mult = self.mc.cr[act_cr[0]].mult   # multiplier (1 or -1, for max/min criteria, respectively)
            print(f'{var_name=}, {m1_var=}, {m1_var.name=}, {mult=}')
            m.afC = pe.Constraint(expr=(m.af == mult * m1_var))  # constraint linking the m1 and m (MC-part) submodels
            m.goal = pe.Objective(expr=m.af, sense=pe.maximize)
            m.goal.activate()  # objective of m1 block is deactivated
            print(f'mc_itr(): concrete model "{m.name}" for computing utopie of criterion "{var_name}" generated.')
            return m
        else:
            raise Exception(f'mc_itr(): handling of stage {self.mc.cur_stage} not implemented yet.')

        # MC-part variables needed for defining Achievement Function (AF), to be maximized
        # m.af = pe.Var()     # Achievement Function (AF), to be maximized  (af = caf_min + caf_reg)
        # af = caf_min + caf_reg
        # m.caf_min = pe.Var()     # min of CAFs
        # m.caf_reg = pe.Var()     # regularizing term (scaled sum of all CAFs)
        # for id_cr in var_names:     # var_names contains list of names of variables representing criteria
        #     m.add_component('caf_' + id_cr, pe.Var())  # CAF: component achievement function of crit. named 'id_cr'
        #     m.add_component('pwl_' + id_cr, pe.Var())  # PWL: of CAF of criterion named 'id' (may not be needed)?
        #
        # return m
    # print('\ncore model display: -----------------------------------------------------------------------------')
    # (populated) variables with bounds, objectives, constraints (with bounds from data but without definitions)
    # m1.display()     # displays only instance (not abstract model)
    # print('end of model display: ------------------------------------------------------------------------\n')
    # m1.inc.display()
    # m1.var_names[0].display() # does not work, maybe a cast could help?
    # xx = var_names[0]
    # print(f'{xx}')
    # m1.xx.display()     # also does not work

    # print(f'{m.af.name=}')
    # xx = m.af
    # print(f'{m.af=}')
    # print(f'{xx=}')
    # print(f'{xx.name=}')
    # zz = xx.name
    # print(f'{zz=}')
    # m.var_names[0] = pe.Var()  # does not work
    # var_names.append('x')     # tmp: second variable only needed for testing

    # variables defining criteria (to be linked with the corresponding vars of the core model m1)
    # for id in var_names:     # var_names contains list of names of variables to be linked between blocks m and m1
    #     m.add_component(id, pe.Var())
    #     # m.add_component(id, pe.Constraint(expr=(m.id == m1.id)))  # does not work: m.id is str not object
    #     print(f'variable "{id}" defined in the second block.')
    #     # print(f'{m.name=}') # print the block id
    #     # print(f'{m.id=}') # error, Block has no attribute id
    # m.incC = pe.Constraint(expr=(m.inc == 100. * m1.inc))  # linking variables of two blocks
    # print(f'{m.inc.name=}, {m.inc=}')

    def mc_sol(self, rep_vars=None):   # extract from m1 solution values of all criteria
        # cf regret::report() for extensive processing
        cri_val = {}    # all criteria values in current solution
        m1_vars = self.m1.component_map(ctype=pe.Var)  # all variables of the m1 (core model)
        for (i, var_name) in enumerate(self.var_names):     # loop over m1.vars of all criteria
            m1_var = m1_vars[var_name]
            # val = m1_var.extract_values() # for indexed variables
            val = m1_var.value
            cr_name = self.cr_names[i]
            cri_val.update({cr_name: val})
            print(f'Value of variable "{var_name}" defining criterion "{cr_name}" = {val}')
        self.mc.store_sol(cri_val)  # process and store criteria values

        sol_val = {}    # dic with values of variables requested in rep_var
        for var_name in rep_vars:     # loop over m1.vars of all criteria
            m1_var = m1_vars[var_name]
            # todo: indexed variables needs to be detected and handled accrdingly (see regret::report())
            # val = m1_var.extract_values() # for indexed variables
            val = m1_var.value
            sol_val.update({var_name: val})
            print(f'Value of report variable {var_name} = {val}')
        print(f'values of selected variables: {sol_val}')
        return sol_val