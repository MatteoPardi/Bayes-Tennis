from typing import Any
import torch
import time


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
            return x.to(dtype=torch_dtype, device=device)
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


class TicToc:
    """
    TicToc class to easily measure time with tic() and toc() functions.

    Usage example:
        timer = TicToc()
        timer.tic()
        ...
        timer.toc()
    """

    def __init__ (self) -> None:
        """
        Constructor of the class
        """

        self._tic = None
        self._toc = None


    def tic (self) -> None:
        """
        Reset the timer.

        Args:
            None

        Returns:
            None
        """

        print("(tic)", flush=True)
        self._tic = time.time()


    def toc (self) -> float:
        """
        Measure the time elapsed since the last call to tic() and print it to the console.

        Args:
            None

        Returns:
            measure : float
                The time elapsed since the last call to tic(). In seconds.
        """

        measure = time.time() - self._tic
        print(f"(toc) {self._pretty_format(measure)}", flush=True)
        return measure
    

    def _pretty_format (self, seconds: float) -> str: 
        """
        Format the time in seconds as a string with nice units.
        """

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
        