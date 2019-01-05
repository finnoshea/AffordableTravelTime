#!/usr/bin/env python
"""Data analysis main file.
"""

__license__ = "GPL"
__version__ = "0.0"
__status__ = "Development"

# Principal is the initial loan amount.
# interest is the MONTHLY interest.  i.e. is the yearly interst is 4% then
# interest = 0.04/12
# months is the length of the loans in months.
def calculate_monthly_payment(principal, interest, months):
    monthly_payment = principal * \
                      (interest * (1 + interest)**months) / \
                      ((1+interest)**months - 1)
    return(monthly_payment)