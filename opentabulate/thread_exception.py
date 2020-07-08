# -*- coding: utf-8 -*-
"""
Thread exceptions.

This was placed in its own file to avoid circular imports.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
Center for Special Business Projects (CSBP) at Statistics Canada.
"""

class ThreadInterruptError(Exception):
    """
    Interrupt exception class. Used for a thread listening for an interrupt event. 
    """