# zplab python style guide
Author: Zachary Pincus  
Date: 2018-07-29  
http://zplab.wustl.edu


1. In general follow [PEP 8](https://www.python.org/dev/peps/pep-0008/), though *never* to the detriment of readability. In particular, the one main exception to PEP 8 in the lab is that lines longer than 79 characters are permitted. Awkward breaks are worse than the occasional 100-character line. (Everyone should watch Raymond Hettinger's [PyCon talk](https://www.youtube.com/watch?v=wf-BqAjZb8M), for how to write beautiful, pythonic code. Hint: severe adherence to PEP 8, and in particular line length limits, is silly.)

2. Import statements:
    1. Group imports into the following sections, separated by one blank line):
        - standard library imports
        - "standard extra packages" such as scipy or numpy (may be in the first group if either group is small)
        - zplab packages such as freeimage, ris_widget, zplib, etc.
        - local imports (e.g. `from .foo import bar`)
        
    2. **All** imported functions/classes should be distinguishable from locally-defined ones by having exactly one level of namespace still attached (e.g. `numpy.in1d`). Thus it is always absolutely clear whether any code is using a local or imported definition. Thus,
        - Never import a whole namespace (e.g. `from matplotlib.pyplot import *`).
        - Do not import individual functions, classes &c. from a namespace (e.g. `from numpy import in1d`).
        - Use the `from` syntax to import specific sub-modules.
            
        **Wrong:**
        ```python
        from scipy.ndimage import binary_closing
        binary_closing(image)
        ```
        **Wrong:**
         ```python
        import scipy.ndimage
        scipy.ndimage.binary_closing(image)
        ```
        **Right:**
         ```python
        from scipy import ndimage
        ndimage.binary_closing(image)
        ``` 
        
    3. Most guides recommend "shortened" imports for `numpy`, `scipy`, and so forth (i.e. `np`, `sp`). The zplab style is to **spell out** all imports for clarity, and not use abbreviations. That is, do not use the `import foo as bar` syntax.
        - Feel free to make your life easier in interactive sessions by using abbreviations, but in library code, use the full names. Tab-completion makes `numpy` no more onerous to type than `np`. 
        - *Exception:* `import matplotlib.pyplot as plt` is fine. The name `pyplot` is visually hard to read.

3. Variable naming conventions are as follows:
    1. Classes are named in `CapitalizedWords` case. (Acronyms stay in all caps: `HTTPServer`, not `HttpServer`.)
    2. Global variables or class-level variables are in `UPPERCASE_WITH_UNDERSCORES`.
    3. All other names (modules, functions, methods, and local variables) are in `lowercase_with_underscores`.
    4. Helper functions, methods, or classes that are not part of the public API and really are just for use within a given module should be prepended with a single underscore. If some code outside of the defining module uses these helpers, then they are, *ipso facto*, part of the public API and should be promoted to properly-named and documented functions/methods/classes.
    5. The `mixedCase` convention is an abomination and must not be used for new code.
    6. Variable names should be descriptive. Prefer longer names to short/highly abbreviated names. Exception: use `i`, `j`, `k` for loop indices, array axes, etc., rather than `index`, `index1` or whatnot. 

4. Strings should be defined with single-quotes where possible (`x = 'a string'`), but use double-quotes where the string itself has a single-quote in it (`x = "a 'string' so to speak"`). 

5. All public API components should have docstrings.
    1. Docstrings should be triple-quoted (even if only one line) with double quotes.
    2. Single-line docstrings have the closing triple-quotes on the same line; multi-line docstrings have the closing quotes on a new line.
    3. All docstrings start with a short *one-line* summary. A multiline summary after a blank line is optional.
    4. Docstrings should define the parameters and return values in specific indented blocks, delimited with colons.
    5. After the parameters and return summary, an examples block is recommended.
    
    Basic example:
    
        """Do something.

        A longer summary of the function; usually several lines worth describing
        important caveate.
        
        Parameters:
            foo: a description of a single parameter.
            min, max: two related parameters can be described together.
            bar: another parameter.
            
        Returns: the resulting quux value.

        Examples: 
            some examples
        """
    If multiple values are returned, document the return as follows:
    
        Returns: (foo, bar)
            foo: a description
            bar: another description

4. Except in rare cases, the return value (or number of return values) of a function should not depend on a specific parameter. Similarly, functions that behave differently based on a "flag" parameter that takes a `True` or `False` value should generally just be factored into two different functions.

5. Don't copy-paste code! Try to refactor it into helper-functions that can be used modularly. However, it's better to have a few lines duplicated in a few places than to try to pull every single two-line pattern into a helper function. Let clarity be your guide.

6. Not all one- or two-line functions need to exist in a public API. The users of the code can be trusted to write simple things. 

7. Make use of duck-typing wherever possible. Allow code to naturally fail when given obviously-wrong input (e.g. a string instead of an array), rather than performing extensive type-checking. (I.e. use a "we're all consenting adults" mind-set.) Exception: in cases where subtle or hard-to-debug errors could arise, type-checking is a good idea. 
