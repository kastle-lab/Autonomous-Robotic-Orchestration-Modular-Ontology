# -*- coding: utf-8 -*-
import re

def convert_subclass(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    a, b = axiom_string.split('SubClassOf')
    return f"All x where x is of type {a.strip()} implies that x is of type {b.strip()}"


def convert_disjoint(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    a, b = axiom_string.split('DisjointWith')

    disjoint = f"For all x where x is of type {a.strip()} implies x is not of " \
    f"type {b.strip()} and where x is of type {b.strip()} implies x is not of " \
    f"type {a.strip()}"

    return disjoint

def convert_global_domain(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    r, a = axiom_string.split('some owl:Thing SubClassOf')

    domain = f"For all x, if there exists a relationship {r.strip()} with x and "\
       f"x is of type {a.strip()}"

    return domain


def convert_scoped_domain(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    r, ba = axiom_string.split('some')
    b, a = ba.split('SubClassOf')

    domain = f"For all x, if there exists a relationship {r.strip()} with x and "\
        f"y and y is of type {b.strip()} implies x is of type {a.strip()}"

    return domain

def convert_global_range(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    axiom_string = axiom_string.replace('owl:Thing SubClassOf', '')
    r, b = axiom_string.split('only')

    range = f"For all x and y, if there exists a relationship {r.strip()} with x "\
        f"and y and implies y is of type {b.strip()}"

    return range

def convert_scoped_range(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    a, rb = axiom_string.split('SubClassOf')
    r, b = rb.split('only')

    range = f"For all x, if x is of type {a.strip()} and there exists a relationship "\
        f"{r.strip()} with x and y and implies y is of type {b.strip()}"

    return range

def convert_existential(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    a, rb = axiom_string.split('SubClassOf')
    r, b = rb.split('some')

    exist = f"For all x where x is of type {a.strip()} implies there exists a y and a "\
        f"relationship {r.strip()} with x and y and y is of type {b.strip()}"

    return exist

def convert_inverse_existential(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    b, ra = axiom_string.split('SubClassOf inverse')
    r, a = ra.split('some')

    exist = f"For every x that is of type {b.strip()} there has to be an inverse "\
        f"{r.strip()}-filler that connects y and x such that y is of type {a.strip()}"

    return exist


def convert_functionality(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    axiom_string = axiom_string.replace('owl:Thing SubClassOf', '')
    r = axiom_string.replace('max 1 owl:Thing', '')

    funct = f"For all x implies either there does not exist a y and a relationship "\
        f"{r.strip()} with x and y or there exists exactly 1 y and a relationship "\
        f"{r.strip()} with x and y."

    return funct


def convert_qualified_functionality(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    axiom_string = axiom_string.replace('owl:Thing SubClassOf', '')
    r, b = axiom_string.split('max 1')

    funct = f"For all x implies either there does not exist a y and a relationship "\
        f"{r.strip()} with x and y or there exists exactly 1 y and a relationship "\
        f"{r.strip()} with x and y and y is of type {b.strip()}."

    return funct


def convert_scoped_functionality(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    axiom_string = axiom_string.replace('max 1 owl:Thing', '')
    a, r = axiom_string.split('SubClassOf')

    funct = f"For all x where x is of type {a.strip()} implies either there does not "\
        f"exist a y and a relationship {r.strip()} with x and y or there exists exactly "\
        f"1 y and a relationship {r.strip()} with x and y."

    return funct

def convert_qualified_scoped_functionality(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    a, rb = axiom_string.split('SubClassOf')
    r, b = rb.split('max 1')

    funct = f"For all x where x is of type {a.strip()} implies either there does not "\
        f"exist a y and a relationship {r.strip()} with x and y or there exists exactly "\
        f"1 y and a relationship {r.strip()} with x and y and y is of type {b.strip()}."

    return funct


def convert_inverse_functionality(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    axiom_string = axiom_string.replace('owl:Thing SubClassOf inverse', '')
    r = axiom_string.replace('max 1', '')

    funct = f"For all y implies either there does not exist a x and an inverse "\
        f"relationship {r.strip()} with y and x or there exists exactly 1 x and "\
        f"an inverse relationship {r.strip()} with y and x."

    return funct

def convert_inverse_qualified_functionality(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    axiom_string = axiom_string.replace('owl:Thing SubClassOf inverse', '')
    r, a = axiom_string.split('max 1')

    funct = f"For all y implies either there does not exist a x and an inverse "\
        f"relationship {r.strip()} with x and y or there exists exactly 1 y and "\
        f"an inverse relationship {r.strip()} with y and x and x is of type {a.strip()}."

    return funct

def convert_inverse_scoped_functionality(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    axiom_string = axiom_string.replace('max 1 owl:Thing', '')
    b, r = axiom_string.split('SubClassOf inverse')

    funct = f"For all y where y is of type {b.strip()} implies either there does "\
        f"not exist a x and an inverse relationship {r.strip()} with y and x or "\
        f"there exists exactly 1 x and a relationship {r.strip()} with y and x."

    return funct


def convert_inverse_qualified_scoped_functionality(axiom_string):

    axiom_string = axiom_string.replace('`', '').replace('`', '')
    b, ra = axiom_string.split('SubClassOf inverse')
    r, a = ra.split('max 1')

    funct = f"For all y where y is of type {b.strip()} implies either there does "\
        f"not exist a y and an inverse relationship {r.strip()} with y and x or "\
        f"there exists exactly 1 x and a relationship {r.strip()} with y and x is "\
        f"of type {a.strip()}."

    return funct


# Proposed change by Fable analysis as quoted below 

"""
generate_structural_tautology's SubClassOf branch emits malformed syntax. 
When the input contains SubClassOf, it returns `{b} SubClassOf min 0 {a}` — a cardinality restriction with no property in front of it, which isn't parseable Manchester. 
It also then feeds that into convert_structural_tautology, which splits on 'min 0' and yields an empty relationship name.
Empty in this run (st = []), but broken when used.
"""

# def convert_structural_tautology(axiom_string):
#     axiom_string = axiom_string.replace('`', '')
 
#     if 'min 0' in axiom_string:
#         a, rb = axiom_string.split('SubClassOf')
#         r, b = rb.split('min 0')
 
#         ax17 = f"For all x where x is of type {a.strip()} implies there may exist a y "\
#             f"and a relationship {r.strip()} with x and y and y is of type {b.strip()}."
#     else:
#         # Class-only tautology of the form `A SubClassOf owl:Thing` (no property involved)
#         a, b = axiom_string.split('SubClassOf')
 
#         ax17 = f"For all x where x is of type {a.strip()}, x is of type {b.strip()}, "\
#             f"which is trivially true."
 
#     return ax17

def convert_structural_tautology(axiom_string):
    axiom_string = axiom_string.replace('`', '').replace('`', '')
    a, rb = axiom_string.split('SubClassOf')
    r, b = rb.split('min 0')

    ax17 = f"For all x where x is of type {a.strip()} implies there may exist a y "\
        f"and a relationship {r.strip()} with x and y and y is of type {b.strip()}."

    return ax17



def generate_subclass(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`{a} SubClassOf {b}`"


def generate_disjoint(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`{a} DisjointWith {b}`"

def generate_global_domain(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`{r} some owl:Thing SubClassOf {a}`"

def generate_scoped_domain(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`{r} some {b} SubClassOf {a}`"

def generate_global_range(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`owl:Thing SubClassOf {r} only {b}`"


def generate_scoped_range(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`{a} SubClassOf {r} only {b}`"

def generate_existential(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`{a} SubClassOf {r} some {b}`"


def generate_inverse_existential(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`{b} SubClassOf inverse {r} some {a}`"


def generate_functionality(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`owl:Thing SubClassOf {r} max 1 owl:Thing`"


def generate_qualified_functionality(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`owl:Thing SubClassOf {r} max 1 {b}`"

def generate_scoped_functionality(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`{a} SubClassOf {r} max 1 owl:Thing`"



def generate_qualified_scoped_functionality(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`{a} SubClassOf {r} max 1 {b}`"


def generate_inverse_functionality(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`owl:Thing SubClassOf inverse {r} max 1 owl:Thing`"

def generate_inverse_qualified_functionality(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`owl:Thing SubClassOf inverse {r} max 1 {a}`"

def generate_inverse_scoped_functionality(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`{b} SubClassOf inverse {r} max 1 owl:Thing`"

def generate_inverse_qualified_scoped_functionality(axiom_string):

    a, r, b = axiom_string.split(' ')

    return f"`{b} SubClassOf inverse {r} max 1 {a}`"

def generate_structural_tautology(axiom_string):
    
    if re.search('SubClassOf ', axiom_string):
        axiom_string = axiom_string.replace('SubClassOf ', '')

        a, b = axiom_string.split(' ')
        r = 'SubClassOf'
        return f"`{b} SubClassOf min 0 {a}`"
    else:
        a, r, b = axiom_string.split(' ')

        return f"`{b} SubClassOf {r} min 0 {a}`"

def print_zipped(orig_list, created_statements):
    for x,y in zip(orig_list, created_statements):
        print("`" + x.strip() + "`")
        print(y)

def convert_run_all(relation_list, name_string, results_dict):
    rl_lst = []
    rl_nl = []

    for x in relation_list:
        if name_string == "subclass":
            rl_lst.append(generate_subclass(x))
            rl_nl.append(convert_subclass(generate_subclass(x)))

        elif name_string == "disjoint":
            rl_lst.append(generate_disjoint(x))
            rl_nl.append(convert_disjoint(generate_disjoint(x)))

        elif name_string == "global domain":
            rl_lst.append(generate_global_domain(x))
            rl_nl.append(convert_global_domain(generate_global_domain(x)))

        elif name_string == "scoped domain":
            rl_lst.append(generate_scoped_domain(x))
            rl_nl.append(convert_scoped_domain(generate_scoped_domain(x)))

        elif name_string == "global range":
            rl_lst.append(generate_global_range(x))
            rl_nl.append(convert_global_range(generate_global_range(x)))

        elif name_string == "scoped range":
            rl_lst.append(generate_scoped_range(x))
            rl_nl.append(convert_scoped_range(generate_scoped_range(x)))

        elif name_string == "existential":
            rl_lst.append(generate_existential(x))
            rl_nl.append(convert_existential(generate_existential(x)))

        elif name_string == "inverse existential":
            rl_lst.append(generate_inverse_existential(x))
            rl_nl.append(convert_inverse_existential(generate_inverse_existential(x)))

        elif name_string == "functionality":
            rl_lst.append(generate_functionality(x))
            rl_nl.append(convert_functionality(generate_functionality(x)))

        elif name_string == "qualified functionality":
            rl_lst.append(generate_qualified_functionality(x))
            rl_nl.append(convert_qualified_functionality(generate_qualified_functionality(x)))

        elif name_string == "scoped functionality":
            rl_lst.append(generate_scoped_functionality(x))
            rl_nl.append(convert_scoped_functionality(generate_scoped_functionality(x)))

        elif name_string == "qualified scoped functionality":
            rl_lst.append(generate_qualified_scoped_functionality(x))
            rl_nl.append(convert_qualified_scoped_functionality(generate_qualified_scoped_functionality(x)))

        elif name_string == "inverse functionality":
            rl_lst.append(generate_inverse_functionality(x))
            rl_nl.append(convert_inverse_functionality(generate_inverse_functionality(x)))

        elif name_string == "inverse qualified functionality":
            rl_lst.append(generate_inverse_qualified_functionality(x))
            rl_nl.append(convert_inverse_qualified_functionality(generate_inverse_qualified_functionality(x)))

        elif name_string == "inverse scoped functionality":
            rl_lst.append(generate_inverse_scoped_functionality(x))
            rl_nl.append(convert_inverse_scoped_functionality(generate_inverse_scoped_functionality(x)))

        elif name_string == "inverse qualified scoped functionality":
            rl_lst.append(generate_inverse_qualified_scoped_functionality(x))
            rl_nl.append(convert_inverse_qualified_scoped_functionality(generate_inverse_qualified_scoped_functionality(x)))

        elif name_string == "structural tautology":
            rl_lst.append(generate_structural_tautology(x))
            rl_nl.append(convert_structural_tautology(generate_structural_tautology(x)))

        results_dict.setdefault(name_string, []).append((x, rl_lst[-1], rl_nl[-1]))

    # Sort results_dict by unique name_strings
    sorted_results_dict = dict(sorted(results_dict.items()))

    return sorted_results_dict
    print(sorted_results_dict['subclass'])

    # Add all items to final_list
    for name_string, items in sorted_results_dict.items():
        for item in items:
            final_list.append(item)

    return final_list


def reorganize_keys(final_dict):
    return_dict = {}

    for k, v in final_dict.items():
        axiom_names = [x[0] for x in v]
        axiom_manchester = [x[1] for x in v]
        axiom_natural_language = [x[2] for x in v]

        for index, n in enumerate(axiom_names):
            return_dict.setdefault(n, {}).setdefault('axiom', []).append(k)
            return_dict.setdefault(n, {}).setdefault('manchester', []).append(axiom_manchester[index])
            return_dict.setdefault(n, {}).setdefault('natural_language', []).append( axiom_natural_language[index])

    return return_dict

def write_file(class_name, class_values, print_list = ['manchester']):

    with open(f'{class_name}_axioms.md', 'w') as file:
        for k,dictvals in class_values.items():
            file.write(f"# {k}\n")

            for ax_index, ax_value in enumerate(dictvals['axiom']):
                file.write(f"{ax_value}: ")

                if 'manchester' in print_list:
                    file.write(f"{dictvals['manchester'][ax_index]}\n")
                    file.write("\n")

                if 'natural_language' in print_list:
                    file.write(f"{dictvals['natural_language'][ax_index]}\n")
                    file.write("\n")


if __name__ == "__main__":

    type_value = "Autonomous-Robotic-Orchestration-Modular-Ontology"

    if type_value =="Autonomous-Robotic-Orchestration-Modular-Ontology":

        sc = [
            "Constructor SubClassOf Archetype",
            "Harvestor SubClassOf Archetype",
            "Inspector SubClassOf Archetype",
            "Explorer SubClassOf Archetype",
            "Sentinel SubClassOf Archetype",
            "Painter SubClassOf Archetype",
            "Hauler SubClassOf Archetype",
            "Digger SubClassOf Archetype"
        ]

        dis = [
            "Goal hasDeadline TemporalExtent",
            "Goal isWithinBounds SpatialExtent",
            "Goal hasOperationalExtent SpatialExtent",
            "Goal hasSuccessState State",
            "Goal hasTask Task",
            "Task providesRole Role",
            "Task requiresSpatialThing SpatialThing",
            "Task requiresArchetype Archetype",

        ]

        gd = [
            "Goal hasDeadline TemporalExtent",
            "Goal isWithinBounds SpatialExtent",
            "Goal hasOperationalExtent SpatialExtent",
            "Task requiresSpatialThing SpatialThing",
            "Task requiresArchetype Archetype",
        ]

        sd = [
            "Goal hasSubGoal Goal",
            "Goal hasTask Task",
            "Task dependsOnTask Task",
            "Task hasNextTask Task",
        ]

        gr = [
            "Goal hasDeadline TemporalExtent",
            "Goal isWithinBounds SpatialExtent",
            "Goal hasOperationalExtent SpatialExtent",
            "Goal hasInstructionalText xsd:string",
            "Goal hasSuccessState State",
            "Task requiresSpatialThing SpatialThing",
            "Task requiresArchetype Archetype",
        ]

        sr = [
            "Goal hasSubGoal Goal",
            "Goal hasTask Task",
            "Task dependsOnTask Task",
            "Task hasNextTask Task",
            "Task providesRole Role",

        ]

        ex = [
            "Goal hasDeadline TemporalExtent",
            "Goal hasSuccessState State",
            "Task requiresSpatialThing SpatialThing",
            "Task requiresArchetype Archetype",
        ]

        iex = [
            "Goal hasTask Task",
            "Task providesRole Role",

        ]

        fun = [

        ]

        qfun = [

        ]

        sf = [

        ]

        qsf = [
            "Goal hasDeadline TemporalExtent",
            "Goal hasInstructionalText xsd:string",
            "Goal hasTask Task",
            "Task requiresArchetype Archetype",
        ]

        ifun = [

        ]

        iqf = [

        ]

        isf = [

        ]

        iqsf = [

        ]

        st = [
            "Goal isWithinBounds SpatialExtent",
            "Goal hasOperationalExtent SpatialExtent",

        ]

        flist = {}
        flist = convert_run_all(sc, "subclass", flist)
        flist = convert_run_all(dis, "disjoint", flist)
        flist = convert_run_all(gd, "global domain", flist)
        flist = convert_run_all(sd, "scoped domain", flist)
        flist = convert_run_all(gr, "global range", flist)
        flist = convert_run_all(sr, "scoped range", flist)
        flist = convert_run_all(ex, "existential", flist)
        flist = convert_run_all(iex, "inverse existential", flist)
        flist = convert_run_all(fun, "functionality", flist)
        flist = convert_run_all(qfun, "qualified functionality", flist)
        flist = convert_run_all(sf, "scoped functionality", flist)
        flist = convert_run_all(qsf, "qualified scoped functionality", flist)
        flist = convert_run_all(ifun, "inverse functionality", flist)
        flist = convert_run_all(iqf, "inverse qualified functionality", flist)
        flist = convert_run_all(isf, "inverse scoped functionality", flist)
        flist = convert_run_all(iqsf, "inverse qualified scoped functionality", flist)
        flist = convert_run_all(st, "structural tautology", flist)

        flist = reorganize_keys(flist)

        write_file(type_value, class_values = flist, print_list = ['manchester'])