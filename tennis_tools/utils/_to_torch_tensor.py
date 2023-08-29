import torch as th


def to_torch_tensor (x, th_dtype):

    if isinstance(x, th.Tensor): 
        if x.dtype == th_dtype: return x
        else: x.to(th_dype)
    else: return th.tensor(x, dtype=th_dtype)
