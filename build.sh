#!/usr/bin/env bash

USAGE=$(cat <<-END
USAGE: $0 <command> <options>*

    init: install all development dependencies

        --no-auto-refresh: skip the step of refreshing this build.sh script from
            the tip of master in the boom-pylib repository
        --nuke: completely remove the ./usr directory before initializing

    edit: launch vim with settings to use the project’s version of python

    lint: run various programs to catch programming & style errors

    test: run automated tests. By default, all tests are run once, and then the
        script exits. There are a number of options to change this default. Some
        conflict with one another (e.g., --watch and --functional). Whichever is
        declared last will take precedence.

        Unit tests are those which run completely within the process space of
        the test runner (i.e., no disk or network access).

        Functional tests are those which require no 3rd-party software be
        installed or servers set up, but which otherwise do anything else.

        Integration tests have no limits on what they may require.

        --all (optional) turn on all test types
        --circle-ci: (optional) only run tests which can pass in CircleCI.
            Implies --no-integration.
        --format: (optional) either "progress" or "documentation"
        --messy: (optional) leave scratch directories behind in ./tmp
        --watch: (optional) watch all the source files and repeat the tests
            when things change. Implies --no-functional and --no-integration.
        --(no-)functional: (optional) turn on/off functional tests
        --(no-)unit: (optional) turn on/off unit tests
        --(no-)integration: (optional) turn on/off integration tests
        --none: (optional) turn off all test types

    clean: remove temporary or one-off data from the ./tmp directory

    python: start a Python REPL console which is sure to use the correct
        version of Python pre-initialized with all the correct versions of
        this package’s dependencies

    publish: publish this package as an official release on GemFury. This should
        only be performed on the master branch, and only after a change has been
        merged which updates the package version.

    refresh: refresh this build script and its related helper files. This will
        download the latest version from the boom-pylib repo and replace the
        files in your current repo.

    upgrade: upgrade any Python dependencies which have new versions available
END
)

AUTO_REFRESH="YES"
BUILD_CONFIG=".build_cfg.sh"
CIRCLE_CI="NO"
COMMAND="help"
CONFIRM="NO"
ENV_FILE=".env"
FORMAT="progress"
LINT_INCLUDE="src"
LINT_EXCLUDE="--exclude=.ropeproject"
MESSY="NO"
NUKE="NO"
PYTHON=$(which python)
PYTHON_VERSION="3.6"
TEST_FILE=".pylib.testing"
TEST_FUNCTIONAL="YES"
TEST_INTEGRATION="YES"
TEST_RUN=1
TEST_UNIT="YES"
VIRTUAL_ENV="./usr"
WATCH="NO"

[[ "$USER" == "" ]] && USER=$(whoami)
VIRTUAL_BIN="$VIRTUAL_ENV/bin"

# Helper Functions #####################################################################################################

function build-native-component {
    # do nothing. Packages may override this function if they have a native component to build.
    return 0
}

function build-python-env {
    PYTHON_ENV="MESSY=$MESSY USER=$USER"
}

function check-python-version {
    if ! $PYTHON --version | grep -q $PYTHON_VERSION; then
        echo "Please update PYTHON in .env to refer to a Python $PYTHON_VERSION executable."
        exit 1
    fi

    return 0
}

function die {
    printf "$*\n"
    echo
    exit 1
}

function execute-functional-tests {
    if [[ "$TEST_FUNCTIONAL" == "YES" ]]; then
        printf "\nRunning functional tests...\n"
        eval $PYTHON_ENV $VIRTUAL_BIN/mamba run src --format=$FORMAT -t functional
        return $?
    fi
    return 0
}

function execute-integration-tests {
    if [[ "$TEST_INTEGRATION" == "YES" ]]; then
        printf "\nRunning integration tests...\n"
        eval $PYTHON_ENV $VIRTUAL_BIN/mamba run src --format=$FORMAT -t integration
        return $?
    fi
    return 0
}

function execute-test-run {
    echo "Starting test run $TEST_RUN at $(date):"
    echo "unit: $TEST_UNIT, functional: $TEST_FUNCTIONAL, integration: $TEST_INTEGRATION"

    build-python-env
    build-native-component \
        && execute-unit-tests \
        && execute-functional-tests \
        && execute-integration-tests \
        || return 1
    return 0
}

function execute-unit-tests {
    if [[ "$TEST_UNIT" == "YES" ]]; then
        printf "\nRunning unit tests...\n"
        eval $PYTHON_ENV $VIRTUAL_BIN/mamba run src --format=$FORMAT -t unit
        return $?
    fi
    return 0
}

function init-custom {
    # do nothing. repos with custom initialization can override this function
    return 0
}

function on-unknown-argument {
    die "Unknown argument: $1"
}

function usage {
    die "$*\nTry \"$0 help\" for details"
}

function watch-source-files {
    fswatch -o -r src -e '.*' -i '\.cpp$' -i '\.h$' -i '\.py$' -m poll_monitor
}

function write-build-config {
    [[ -e "$BUILD_CONFIG" ]] && rm "$BUILD_CONFIG"

    echo "# This file allows you to configure how the build.sh script operates. It will" >> $BUILD_CONFIG
    echo "# be sourced immediately before running a build command. Feel free to leave it" >> $BUILD_CONFIG
    echo "# empty if you don't need any modifications." >> $BUILD_CONFIG
}

function write-env-file {
    [[ -e "$ENV_FILE" ]] && rm "$ENV_FILE"

    echo '# The location of a `python` executable for Python v3.6'  >> $ENV_FILE
    echo "PYTHON=$PYTHON"                                           >> $ENV_FILE
    echo '# The authentication token used for uploading to GemFury' >> $ENV_FILE
    echo "GEMFURY_TOKEN=$GEMFURY_TOKEN"                             >> $ENV_FILE
}

# Local Commands #######################################################################################################

function command-build {
    build-native-component
}

function command-clean {
    if [[ "$CONFIRM" == "YES" ]]; then
        rm -rf ./tmp
    else
        echo "Removing ./tmp... (skipped)"
        echo ""
    fi

    [[ "$CONFIRM" == "YES" ]] || printf "This was a dry run. To actually delete files, add: --confirm\n\n"
}

function command-edit {
    source $VIRTUAL_BIN/activate
    export VIRTUAL_ENV
    $EDITOR
}

function command-help {
    echo "$USAGE" | more
    echo ""
    exit
}

function command-init {
    if [[ "$AUTO_REFRESH" == "YES" ]]; then
        command-refresh-build || exit 1
    fi
    check-python-version || exit 1

    [[ "$NUKE" == "YES" && -d $VIRTUAL_ENV ]] && rm -rf $VIRTUAL_ENV
    $PYTHON -m venv --copies $VIRTUAL_ENV
    ./usr/bin/pip install --upgrade pip

    unset PYTHONPATH
    export PYTHONPATH
    $VIRTUAL_BIN/pip install -r requirements.txt
    init-custom

    $VIRTUAL_BIN/pip freeze | grep -v '^-e' > .pip.lock
}

function command-lint {
    $VIRTUAL_BIN/pycodestyle $LINT_INCLUDE $LINT_EXCLUDE
    (( RESULT = $RESULT + $? ))

    $VIRTUAL_BIN/pydocstyle $LINT_INCLUDE
    (( RESULT = $RESULT + $? ))

    $VIRTUAL_BIN/pyflakes $LINT_INCLUDE
    (( RESULT = $RESULT + $? ))

    return $RESULT
}

function command-publish {
    CURRENT_BRANCH=$(git branch | grep '^\*' | awk '{print $2}')

    if [[ "$CURRENT_BRANCH" == "master" ]]; then
        [[ "$GEMFURY_TOKEN" == "" ]] && die "Please make sure GEMFURY_TOKEN is defined in $ENV_FILE"

        $VIRTUAL_BIN/python setup.py sdist
        PACKAGE="dist/$(ls dist | head -n1)"

        PUBLISHED_VERSION=$( \
            curl -s https://$GEMFURY_TOKEN@pypi.fury.io/boomtechnology/$PACKAGE \
            | grep boom-pylib- \
            | sed "s/.*$PACKAGE-\([0-9.].*\).tar.gz.*/\1/" \
            | tail -n1
        )
        CURRENT_VERSION=$(cat setup.py | grep version= | sed 's/.*version="\(.*\)".*/\1/')

        if [[ "$PUBLISHED_VERSION" != "$CURRENT_VERSION" ]]; then
            curl -F package=@$PACKAGE https://$GEMFURY_TOKEN@push.fury.io/boomtechnology \
                || die "\nUploading package failed!"
        else
            echo "Version $CURRENT_VERSION has already been published, skipping publish..."
        fi

        rm -rf dist 2>/dev/null
    else
        echo "Not on master branch, skipping publish..."
    fi
}

function command-python {
    source $VIRTUAL_BIN/activate
    eval $PYTHON_ENV $VIRTUAL_BIN/python
}

function command-refresh-build {
    # Install the Git Hooks
    pushd .git/hooks >/dev/null
    ls ../../src/hooks | while read HOOK_FILE; do
        ln -sf "../../src/hooks/$HOOK_FILE" .
    done
    popd >/dev/null

    if cat .git/config | grep 'url =' | head -n1 | grep -q boom-pylib; then
        # We're already in the boom-pylib repo.
        return 0
    fi

    # Download the current version of boom-pylib
    TMP_REPO=".boom-pylib"
    rm -rf $TMP_REPO 2>/dev/null
    git clone -q --depth 1 git@github.com:boomtechnology/boom-pylib.git $TMP_REPO

    # Copy over the files we need, replacing existing copies
    mkdir -p src
    rm -rf src/hooks 2>/dev/null
    cp $TMP_REPO/build.sh .build.sh.new
    cp -R $TMP_REPO/src/hooks src/hooks

    # Get rid of the boom-pylib repo
    rm -rf $TMP_REPO 2>/dev/null

    (sleep 1; mv .build.sh.new build.sh) &
}

function command-test {
    RESULT=0

    function do-watched-run {
        rm -rf ./tmp 2>/dev/null
        execute-test-run > $TEST_FILE.out 2>&1
        RESULT=$?

        clear
        cat "$TEST_FILE.out"
        rm "$TEST_FILE.out"
        rm "$TEST_FILE"
        printf "\nWaiting for changes...\n"
    }

    if [[ "$WATCH" == "YES" ]]; then
        clear
        execute-test-run
        echo "Waiting for changes..."

        rm $TEST_FILE 2> /dev/null
        watch-source-files | while read FILE; do
            if [[ ! -e $TEST_FILE ]]; then
                touch $TEST_FILE
                (( TEST_RUN = TEST_RUN + 1 ))
                printf "\nChanges detected! Re-running tests...\n"
                do-watched-run &
            fi
        done
    else
        execute-test-run
        RESULT=$?
    fi

    [[ "$MESSY" == "NO" ]] && rm -rf ./tmp 2>/dev/null

    return $RESULT
}

function command-upgrade-pip {
    $VIRTUAL_BIN/pip install -r requirements.txt --upgrade
    $VIRTUAL_BIN/pip freeze | grep -v '^-e' > .pip.lock
}

# Process Arguments ####################################################################################################

[[ -e $ENV_FILE ]] && source $ENV_FILE
[[ -e $BUILD_CONFIG ]] || write-build-config
source $BUILD_CONFIG
write-env-file

while [[ "$1" != "" ]]; do
    case "$1" in
        build) COMMAND="build";;
        clean) COMMAND="clean";;
        edit) COMMAND="edit";;
        help|--help|-h|-?) COMMAND="help";;
        init) COMMAND="init";;
        lint) COMMAND="lint";;
        python) COMMAND="python";;
        publish) COMMAND="publish";;
        refresh) COMMAND="refresh-build";;
        test) COMMAND="test";;
        upgrade) COMMAND="upgrade-pip";;

        --all) TEST_UNIT="YES"; TEST_FUNCTIONAL="YES"; TEST_INTEGRATION="YES";;
        --no-refresh) AUTO_REFRESH="NO";;
        --circle-ci) CIRCLE_CI="YES"; TEST_INTEGRATION="NO";;
        --confirm) CONFIRM="YES";;
        --format) shift; FORMAT="$1";;
        --functional) TEST_FUNCTIONAL="YES";;
        --integration) TEST_INTEGRATION="YES";;
        --messy) MESSY="YES";;
        --no-functional) TEST_FUNCTIONAL="NO";;
        --no-integration) TEST_INTEGRATION="NO";;
        --no-unit) TEST_UNIT="NO";;
        --none) TEST_UNIT="NO"; TEST_FUNCTIONAL="NO"; TEST_INTEGRATION="NO";;
        --nuke) NUKE="YES";;
        --unit) TEST_UNIT="YES";;
        --watch) TEST_FUNCTIONAL="NO"; TEST_INTEGRATION="NO"; WATCH="YES";;

        *) on-unknown-argument $1;;
    esac
    shift
done

# Script ###############################################################################################################

"command-$COMMAND"
