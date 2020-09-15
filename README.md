# stock-analysis
BIT - F4E stock price analysis script.

## Goal
Create a script that returns financial data 

## Notes
- YFinance can throw an IndexError on institutional holders. This can be fixed by adding a try-except block at the holders part of the `_get_fundamentals`-function.

```Python
try:
            self._institutional_holders = holders[1]
        except IndexError as e:
            self._institutional_holders = "NaN"
```