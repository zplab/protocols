# zplab Python Environment
Author: Zachary Pincus  
Date: 2016-08-19  
http://zplab.wustl.edu

## 1. Initial steps:
**On OS X:**

- Get the compilers by running the following in the terminal:

      xcode-select --install

- Install the “homebrew” tool to simplify getting a few additional packages, by running the following:

      ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

- Use homebrew to install the following packages:

      brew install git fftw zsh

- Last, make sure the mac knows about the new zsh shell:

      echo /usr/local/bin/zsh | sudo tee -a /etc/shells

**On Linux:**  
Use the package manager to ensure that you have compilers installed (gcc or clang), and that fftw, git, and zsh are installed too.

## 2. Set up a zsh environment:
- Change your default shell to zsh.

      chsh -s `which zsh`

- Next, set up a `.zshrc` file:

```
cat > ~/.zshrc << 'EOF'
setopt hist_ignore_dups
setopt append_history
HISTSIZE=100000
SAVEHIST=100000
HISTFILE=~/.zsh_history

autoload -U history-search-end
zle -N history-beginning-search-backward-end history-search-end
zle -N history-beginning-search-forward-end history-search-end

autoload -U colors && colors
prompt="%{$bold_color$fg[red]%}[%{$fg[blue]%}%n@%m:%{$fg[green]%}%25<..<%~%<<%{$fg[red]%}]%{$fg[green]%}%(!.#.>)%{$reset_color%} "

setopt correct
export SPROMPT="Correct %{$fg_bold[red]%}%R%{$reset_color%} to %{$fg_bold[green]%}%r%{$reset_color%}? ([No], Yes, Abort, Edit) "

autoload -Uz compinit && compinit

alias grep='grep --color=auto'

export ANACONDA_PATH="$HOME/miniconda/bin"
export PATH=$ANACONDA_PATH:$PATH
EOF
```

- **For OS X** include these further options:

```
cat >> ~/.zshrc << EOF

bindkey -e
bindkey "^[[A" history-beginning-search-backward-end
bindkey "^[[B" history-beginning-search-forward-end

export CLICOLOR=1
export LSCOLORS='ExfxcxdxbxegedabagExEx'
EOF
```

- **For linux** include these further options:

```
cat >> ~/.zshrc << 'EOF'

bindkey -e
bindkey "${key[Up]}" history-beginning-search-backward-end
bindkey "${key[Down]}" history-beginning-search-forward-end

alias ls='ls --color=auto'
EOF
```

- Now close your terminal window and open a new one to start using `zsh`. 

## 3. Set up a Python environment using Anaconda:
- Download [miniconda for Python 3](http://conda.pydata.org/miniconda.html):  
    **On OS X:**
    
        curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh

    **On Linux:**
    
        curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh

- Install miniconda:

        bash Miniconda3-latest-*-x86_64.sh -b -p $HOME/miniconda
        rehash
        source $HOME/miniconda/bin/activate
        conda init zsh
        rm Miniconda3-latest-*-x86_64.sh
        mkdir -p $HOME/miniconda/etc/conda/activate.d
        cat > $HOME/miniconda/etc/conda/activate.d/remove_base_ps1.sh << 'EOF'
        PS1="$(echo $PS1 | sed 's/(base) //')"
        EOF

    (The `rehash` line makes sure that `zsh` knows about the new `conda` command.)

    Here’s a [quick guide](http://conda.pydata.org/docs/test-drive.html) to Anaconda, though note that for basic use you don’t need to know any of this.

- Install the basic suite of zplab tools into the base miniconda environment. Ignore any message about needing to activate the `root` environment: the root (aka `base`) environment is active by default. (On macs, you may need to first do `export MACOSX_DEPLOYMENT_TARGET=10.9` for freeimage to compile correctly.)

```
cat > user_env.yml << EOF
channels:
    - defaults
    - conda-forge

dependencies:
    - python>=3.6
    - ipython
    - numpy
    - scipy
    - scikit-learn
    - pyopengl
    - cython
    - cffi
    - pyfftw
    - pip
    - pip:
        - pyqt5
        - matplotlib
        - scikit-image
        - qtconsole
        - git+https://github.com/zplab/freeimage-py
        - git+https://github.com/zplab/zplib
        - git+https://github.com/zplab/RisWidget
        - git+https://github.com/zplab/elegant
EOF
pip install --upgrade pip
conda update conda
conda env update -n base -f user_env.yml
pip install celiagg --global-option=--no-text-rendering
rm user_env.yml
```

- If you ever need to update to get the latest version of any of the zplab-specific libraries, you can run lines like the following:

      pip install --upgrade git+https://github.com/zplab/freeimage-py
    (for example) to upgrade freeimage-py.

- Configure the ipython environment:

```
ipython profile create
cat > .ipython/profile_default/ipython_config.py << EOF
c.TerminalIPythonApp.display_banner = False
c.TerminalInteractiveShell.confirm_exit = False
c.TerminalInteractiveShell.display_completions = 'readlinelike'
EOF
```

- If you are using a terminal with a light background, also do the following:

      echo "c.InteractiveShell.colors = 'LightBG'" >> .ipython/profile_default/ipython_config.py