from __future__ import print_function
from pykit import ir
from pykit import types as ptypes
from flypy import extern_support
from flypy.compiler import lltype


def rewrite_externs(func, env):
    """Rewrite external symbol references

    Base on flypy.compiler.lower.constants.rewrite_constants
    """
    if env['flypy.state.opaque']:
        return
    target = env['flypy.target']
    # For each operation
    for op in func.ops:
        # Only for call operation
        if op.opcode == 'call':
            # For each constant
            constants = ir.collect_constants(op)
            new_constants = []
            for c in constants:
                extern = c.const

                if extern_support.is_extern_symbol(extern):
                    # Make a declare-only function
                    argtypes = extern.type.argtypes
                    restype = extern.type.restype

                    if target == "cpu":
                        # Install external symbol for CPU target
                        extern.install()

                    functype = ptypes.Function(lltype(restype),
                                               [lltype(t) for t in argtypes],
                                               extern.type.varargs)
                    # Note: Global value should really be part inserted into
                    # a module.  But there are no module support at this point.
                    replacment = ir.GlobalValue(extern.name, functype,
                                                external=True)
                else:
                    # No change
                    replacment = c
                # Add replacement
                new_constants.append(replacment)
            # Replace
            ir.substitute_args(op, constants, new_constants)

