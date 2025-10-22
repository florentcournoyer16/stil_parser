#!/bin/tcsh


################################################################
echo "[INFO] ---- PARSING ARGS ----"
################################################################


setenv ENV_VERBOSE 0
set _i = 1
while ( $_i <= $#argv )
    set _a = "$argv[$_i]"
    if ( "$_a" == "-h" || "$_a" == "--help" ) then
        echo "[INFO] Usage: source scripts/env_setup.csh [-v|--verbose] [-cd|--anaconda_dir <Aanaconda installation directory>]"
        exit
    else if ( "$_a" == "-v" || "$_a" == "--verbose" ) then
        setenv ENV_VERBOSE 1
    else if ( "$_a" == "-ad" || "$_a" == "--anaconda_dir" ) then
        @ _i++
        setenv ANACONDA_DIR $argv[$_i]
    else
        echo "[WARNING] Argument '$_a' ignored (see help (-h|--help) for supported arguments)"
    endif
    @ _i++
end


################################################################
echo "[INFO] ---- PROJECT ENV VARS ----"
################################################################


# check if $ANACONDA_DIR already exists
if ( ! $?ANACONDA_DIR ) then
    setenv ANACONDA_DIR $HOME/anaconda3
endif

# base environement variables
setenv PROJECT_NAME         STIL_PARSER                         # project name will also be Anaconda env. name


if ( $ENV_VERBOSE == 1 ) then
    echo "[INFO] base environement variables:"
    echo "[INFO] PROJECT_NAME           = $PROJECT_NAME"
endif


################################################################
echo "[INFO] ---- CREATING CONDA ENV ----"
################################################################


# init conda
if ( ! $?CONDA_EXE ) then
    if ( $ENV_VERBOSE == 1 ) then
        echo "[INFO] Conda not initialised... Initializing"
    endif
    if ( -f "$ANACONDA_DIR/etc/profile.d/conda.csh" ) then
        source "$ANACONDA_DIR/etc/profile.d/conda.csh" 
    else
        echo "[ERROR] conda.csh init script not found, manual setup/installation may be needed -- See README.md for further instructions"
        exit
    endif
endif

# create conda env.
set _env_list = (`conda env list | awk '{print $1}'`)
if ( "$_env_list" !~ *$PROJECT_NAME* ) then
    setenv PATH "/usr/bin:$PATH" # making sure the right gcc is used
    set _env_python_yml = $PROJECT_ROOT/conda_dependencies.yml
    if ( $ENV_VERBOSE == 1 ) then
        echo "[INFO] Conda environment '$PROJECT_NAME' not found -> creating it"
        conda env create --file "$_env_python_yml" --name $PROJECT_NAME
    else
        conda env create --file "$_env_python_yml" --name $PROJECT_NAME --quiet
    endif
    if ( $status != 0 ) then
        echo "[ERROR] 'conda env create' from $_env_python_yml failed (status=$status)"
        exit
    endif
else if ( $ENV_VERBOSE == 1 ) then
    echo "[INFO] Conda enviornment already exists"
    conda env list
endif

# source conda environment from file
conda activate $PROJECT_NAME
if ( $status != 0 ) then
    echo "[ERROR] 'conda activate $PROJECT_NAME' failed (status=$status)"
    exit
endif

# ensure the correct python aliases are defined
setenv PYTHON   $ANACONDA_DIR/envs/$PROJECT_NAME/bin/python
setenv PYTHON3  $ANACONDA_DIR/envs/$PROJECT_NAME/bin/python

if ( $ENV_VERBOSE == 1 ) then
    echo "[INFO] python environmement variables:"
    echo "[INFO] PYTHON             = $PYTHON"
    echo "[INFO] PYTHON3            = $PYTHON3"
endif
