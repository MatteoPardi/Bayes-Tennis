from typing import Any, Union
import torch


def as_torch_tensor (x: Any, torch_dtype: torch.dtype, device: torch.device = torch.device("cpu")) -> torch.Tensor:
    """
    Transform x into a torch tensor of type torch_dtype

    Usage example:
        x = as_torch_tensor([1, 2, 3], torch.float)

    Args:
        x : any
            The object to transform into a torch tensor
        torch_dtype : torch.dtype
            The type of the torch tensor
        device : torch.device = torch.device("cpu")
            The device to store the tensor

    Returns:
        x_as_torch_tensor : torch.Tensor
            The object transformed into a torch tensor   
    """

    if isinstance(x, torch.Tensor): 
        if x.dtype == torch_dtype and x.device == device:
            return x
        else:
            return x.to(torch_dtype, device=device)
    else: 
        return torch.tensor(x, dtype=torch_dtype, device=device)


def as_2dim_tensor (x: torch.Tensor) -> torch.Tensor:
    """
    Transform x into a 2-dimensional torch tensor

    Usage example:
        x = as_2dim_tensor(torch.tensor([1, 2, 3]))

    Args:
        x : torch.Tensor 1D or 2D
            The 1D or 2D torch tensor to transform into a 2-dimensional torch tensor.
            If x is a 1D tensor, it will be transformed into a 2D tensor with one row.

    Returns:
        x_as_2dim_tensor : torch.Tensor 2D
            The object transformed into a 2-dimensional torch tensor   
    """

    return x if x.dim() == 2 else x[None, :]
