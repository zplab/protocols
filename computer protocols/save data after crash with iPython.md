# How to recover intermediate data using iPython in the event of a crash

If you are doing some kind of computation in Python under iPython and there is a crash at an intermediate step, you can recover your data.

First, enter the ipython debugger by typing `%debug`.

Next, navigate to a function in the call stack (using the `up` command) that has some data you are interested in saving in a local variable.

Then, assuming the variable you want to save is `precious_local_variable`, type these commands:
```python
from IPython import Application
Application.instance().shell.user_global_ns['recovered_data'] = precious_local_variable
exit
```
This exits the debugger and returns you to the iPython shell. You now have access to that data in the main interactive shell . The above code stores the data as a variable named `recovered_data`, but you could of course choose whatever you want.