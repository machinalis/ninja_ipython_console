try:
    from IPython.zmq.ipkernel import IPKernelApp
    from ipythonconsole import INinjaConsole
except ImportError:
    from ipythonconsole_1_1_x_compat import INinjaConsole
