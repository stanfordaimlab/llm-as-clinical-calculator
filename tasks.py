"""
TASKS.PY - INVOKE SCRIPT

-- Invoke is Make for Python ---

Invoke and Fabric are Python libraries designed to streamline task execution and automation in software projects.
Invoke, the successor to Fabric's task execution API, provides a clean, high-level API for defining and organizing
task functions in Python. It allows developers to create command-line task runners that can replace traditional build
tools or shell scripts. Invoke is particularly useful for automating repetitive tasks, build processes, deployment
scripts, and other DevOps-related activities. Fabric, building on top of Invoke, extends these capabilities to include
 SSH connection management and remote execution, making it ideal for system administration tasks and remote
  deployments.
"""

from invoke import task
from llm_calc.util import util
import os

print("Reminder: This script must be run from the root directory of the project.")


@task(aliases=["rs"])
def run_omc_server(c):
    """Run the llmcalc"""
    with c.prefix("source ~/.virtualenvs/llm-calc/bin/activate"):
        c.run("uvicorn llm_calc.tools.openmedcalc:app --reload --log-level debug")


@task(aliases=["r"])
def run_llmcalc(c):
    """Run the llmcalc CLI."""
    with c.prefix("source ~/.virtualenvs/llm-calc/bin/activate"):
        c.run("llmcalc experiment new --disable-git-warn")


@task(
    aliases=["b", "backup", "commit", "c"],
    help={
        "commit_message": "The message to use for the commit",
        "m": "Alias for commit_message",
    },
)
def git_commit(c, commit_message=None, m=None):
    """Add all files, commit them, and push to origin."""
    message = m if m is not None else commit_message
    if message is None:
        raise ValueError("Please provide a commit message.")
    util.title("Git Workflow")
    util.h1("Precommit Build Scripts")
    lint(c)
    util.h1("Adding & Committing")
    c.run("git add .")
    c.run(f'git commit -m "{message}"')
    util.h1("Pusing to Origin")
    c.run("git push origin main")


@task(
    aliases=["fr"],
)
def full_run(c):
    """Full run"""
    c.run("clear")
    c.run(
        "llmcalc experiment new --disable-git-warn --no-verbose "
        '--description "full run, 10 cases, 5 retries" --number-of-cases 10'
    )


@task(aliases=["l"], help={"check": "Only check the files without modifying them"})
def lint(c, check=False):
    """Find all Python files and reformat them using black."""
    util.h2("Linting with Black")

    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    # Join all file paths with a space
    files_arg = " ".join(python_files)

    # Run black
    if check:
        c.run(f"black --check {files_arg}")
    else:
        c.run(f"black {files_arg}")


from invoke import task
import os

VENV_PATH = "~/.virtualenvs/llm-calc/bin/activate"
LATEX_DIR = "/Users/alexandergoodell/code/llm-calc/docs/manuscript/llm_calc_version_2"
PAPERPILE_BIB_URL = "https://paperpile.com/eb/eDohDsmysU"


@task
def bbb(c):
    """Building CV with pdflatex"""
    print("Building with pdflatex")
    with c.prefix(f"source {VENV_PATH}"):
        build_pdflatex(c)
        build_bib(c)
        build_pdflatex(c)
        git_commit(c, "updated manuscript")


# get paperpile bibliography
# wget --content-disposition -N https://paperpile.com/eb/vdluygrPcA


@task
def get_bib(c):
    """Get the bibliography from Paperpile"""
    with c.prefix(f"source {VENV_PATH}"):
        with c.cd(LATEX_DIR):
            c.run(f"wget --content-disposition -N {PAPERPILE_BIB_URL}")


@task
def build(c):
    """Building  with pdflatex"""
    print("Building with pdflatex")
    with c.prefix(f"source {VENV_PATH}"):
        build_pdflatex(c)
        build_bib(c)
        build_pdflatex(c)
        build_pdflatex(c)
        build_supp(c)



@task
def build_doc(c):
    """Build the docx with Pandoc"""
    with c.prefix(f"source {VENV_PATH}"):
        with c.cd(LATEX_DIR):
            c.run(f"pandoc -s index.tex -o index.docx")


@task
def build_pdflatex(c):
    """Run the llmcalc"""
    with c.prefix(f"source {VENV_PATH}"):
        with c.cd(LATEX_DIR):
            c.run(
                f"pdflatex -shell-escape -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -output-directory={LATEX_DIR} index.tex"
            )

@task
def build_diff(c):
    """Run the llmcalc"""
    with c.prefix(f"source {VENV_PATH}"):
        with c.cd(LATEX_DIR):
            c.run(
                f"pdflatex -shell-escape -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -output-directory={LATEX_DIR} diff.tex"
            )
@task
def build_parts(c):
    """Run the llmcalc"""
    with c.prefix(f"source {VENV_PATH}"):
        with c.cd(LATEX_DIR):
            c.run(f"bibtex text_only")
            c.run(
                f"pdflatex -shell-escape -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -output-directory={LATEX_DIR} text_only.tex"
            )
            c.run(f"bibtex text_only")
            c.run(
                f"pdflatex -shell-escape -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -output-directory={LATEX_DIR} figures_and_tables.tex"
            )



@task
def build_supp(c):
    """Run the llmcalc"""
    with c.prefix(f"source {VENV_PATH}"):
        with c.cd(LATEX_DIR):
            c.run(
                f"pdflatex -shell-escape -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -output-directory={LATEX_DIR} supplement.tex"
            )


@task
def build_bib(c):
    """Run the llmcalc"""
    with c.prefix(f"source {VENV_PATH}"):
        with c.cd(LATEX_DIR):
            c.run(f"bibtex index")

@task
def build_diff_bib(c):
    """Run the llmcalc"""
    with c.prefix(f"source {VENV_PATH}"):
        with c.cd(LATEX_DIR):
            c.run(f"bibtex diff")


# @task
# def build_lua(c):
#     with c.prefix(f"source {VENV_PATH}"):
#         c.run(
#             f"lualatex -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -output-directory={LATEX_PATH}"
#         )
