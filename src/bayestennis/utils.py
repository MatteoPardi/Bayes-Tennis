from typing import Any, Union
import torch


def as_torch_tensor (x: Any, torch_dtype: torch.dtype) -> torch.Tensor:
    """
    Transform x into a torch tensor of type torch_dtype

    Usage example:
        x = as_torch_tensor([1, 2, 3], torch.float)

    Args:
        x : any
            The object to transform into a torch tensor
        torch_dtype : torch.dtype
            The type of the torch tensor

    Returns:
        x_as_torch_tensor : torch.Tensor
            The object transformed into a torch tensor   
    """

    if isinstance(x, torch.Tensor): 
        if x.dtype == torch_dtype:
            return x
        else:
            return x.to(torch_dtype)
    else: 
        return torch.tensor(x, dtype=torch_dtype)
