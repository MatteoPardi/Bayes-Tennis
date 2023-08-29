import time
_tic = 0.


def _pretty_format (seconds):

    if seconds < 1e-6:
        return "{:.2f} ns".format(seconds*1e9)
    elif seconds < 1e-3:
        return "{:.2f} us".format(seconds*1e6)
    elif seconds < 1:
        return "{:.2f} ms".format(seconds*1e3)
    elif seconds < 60:
        return "{:.2f} s".format(seconds)
    elif seconds < 3600:
        return "{:.2f} min".format(seconds/60)
    else:
        return "{:.2f} h".format(seconds/3600)
 
 
# -------------------------------------------------------------
#    tic, toc
# -------------------------------------------------------------


def tic ():
    global _tic
    print("(tic)", flush=True)
    _tic = time.time()
    
    
def toc ():
    measure = time.time() - _tic
    print("(toc) " + _pretty_format(measure), flush=True)
    return measure