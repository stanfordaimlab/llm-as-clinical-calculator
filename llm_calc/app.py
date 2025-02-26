import typer
from typing_extensions import Annotated
from llm_calc.util.util import (
    title,
    h1,
    h2,
    h3,
    h1_style,
    h2_style,
    h3_style,
    log_task,
    log_mini_task,
    tab,
)
from llm_calc.lib.datamodel import ArmSlug, CalculatorSlug

from llm_calc.view.live import LLMDisplay
from rich.text import Text
from llm_calc.util import util

display = LLMDisplay()
import subprocess
import select

# display.start_display()


title("LLM Calc")
log_task("Using Database Available at https://alx.gd/llm-calc-view-database")

app = typer.Typer(
    pretty_exceptions_show_locals=False, no_args_is_help=True, rich_markup_mode="rich"
)


# ----------------- UTILITIES -----------------


@app.command("tmp")
def tmp():
    """
    Temporary function for testing
    """
    from llm_calc.tools.openmedcalc import calculate_caprini, CalcRequestCapriniVte

    calc = CalcRequestCapriniVte(age=45)
    result = calculate_caprini(calc)
    print(result.score)


@app.command()
def view_config():
    """
    View **config** page :sparkles:

    * See global variables in the config file
    :return: None
    """
    from llm_calc.lib.config import config
    from llm_calc.util import util

    util.h1("View config")
    util.console.print(config.config_table())


@app.command()
def rebuild_database():
    """
    Rebuild the database
    :return:
    """
    from llm_calc.util import util
    from llm_calc.lib import database

    util.h1("Build database")
    database.build_inputs_database()


@app.command()
def interpreter():
    """
    Start an iPython interpreter in the current context
    :return:
    """
    from IPython import embed as ipython_embed
    from llm_calc.util import util

    util.h1("iPython interpreter")
    ipython_embed()


@app.command()
def vignettes():
    """
    Build the vignettes
    :return:
    """
    from llm_calc.lib.vignette import gen_all_cases as build_the_vignettes
    from llm_calc.util import util

    util.h1("build vignettes")
    build_the_vignettes()


# ----------------- TESTING -----------------
test_app = typer.Typer()
app.add_typer(test_app, name="test", help="Run tests")


@test_app.command("single-vignette")
def generate_single_vignette(
    calc_slug: Annotated[CalculatorSlug, typer.Option(help="Generate one")] = False,
):
    """
    Run all tests; this will rebuild the inputs database
    and experiments database and run sample tests of each arm
    :return:
    """
    from llm_calc.unit_tests import testing
    from llm_calc.util import util
    from llm_calc.lib.vignette import build_single_vignette

    # rebuild_database()
    util.title("llmcalc Testing Suite: vig")
    case = build_single_vignette(calc_slug)[0]
    print(case)


@test_app.command("all")
def run_tests():
    """
    Run all tests; this will rebuild the inputs database
    and experiments database and run sample tests of each arm
    :return:
    """
    from llm_calc.unit_tests import testing
    from llm_calc.util import util

    util.title("llmcalc Testing Suite: All")
    rebuild_database()
    rebuild_experiments_database()
    util.h1("Run tool tests")
    testing.all_tools()


@test_app.command("rag")
def run_tests_rag():
    """
    Run RAG tests
    :return:
    """
    from llm_calc.unit_tests import testing
    from llm_calc.util import util

    util.title("llmcalc Testing Suite: RAG")
    testing.rag_agent()


@test_app.command("base")
def run_tests_base():
    """
    Run base agent tests
    :return:
    """
    from llm_calc.unit_tests import testing
    from llm_calc.util import util

    util.title("llmcalc Testing Suite: BASE")
    testing.base_agent()


@test_app.command("ci")
def run_tests_code():
    """
    Run code interpreter tests
    :return:
    """
    from llm_calc.unit_tests import testing

    util.title("llmcalc Testing Suite: CI")
    testing.code_interpreter()


@test_app.command("omc")
def run_tests_omc():
    """
    Run openmedicalcalc tests
    :return:
    """
    from llm_calc.unit_tests import testing
    from llm_calc.util import util

    util.title("llmcalc Testing Suite: OMC")
    testing.open_med_calc()


@test_app.command("omc-tools")
def run_tests_omc_tools():
    """
    Run openmedicalcalc tests
    :return:
    """
    from llm_calc.unit_tests import testing
    from llm_calc.util import util

    util.title("llmcalc Testing Suite: OMC Tools")
    testing.omc_tools()


@test_app.command("endpoints")
def run_tests_omc_endpoints():
    """
    Run openmedicalcalc endpoint tests - server must be running
    :return:
    """
    from llm_calc.unit_tests import testing
    from llm_calc.util import util

    util.title("llmcalc Testing Suite: OMC Endpoints")
    testing.test_omc_endpoints()


# ----------------- EXPERIMENT MANAGEMENT -----------------

experiment_app = typer.Typer()
app.add_typer(experiment_app, name="experiment", help="Manage experiments")


@experiment_app.command("rebuild")
def rebuild_experiments_database():
    """
    Rebuild the experiments database
    :return:
    """
    from llm_calc.util import util
    from llm_calc.lib import database

    util.h1("Build database")
    database.build_experiments_database()


@experiment_app.command("new")
def new_experiment(
    disable_git_warn: Annotated[
        bool, typer.Option(help="Disable prompt to stash")
    ] = False,
    number_of_cases: Annotated[int, typer.Option(help="Number of cases to run")] = None,
    include_only_one_arm: Annotated[
        ArmSlug,
        typer.Option(help="Only include one arm in the run, need to give the " "slug"),
    ] = None,
    verbose: Annotated[bool, typer.Option(help="Enable verbose output")] = False,
    description: Annotated[
        str, typer.Option(help="Description of the experiment")
    ] = None,
    use_last_dataset: Annotated[
        bool,
        typer.Option(
            help="Disable creation of new dataset and use the most recent one in the database"
        ),
    ] = False,
):
    from llm_calc.lib.config import config
    from llm_calc.util import util
    from llm_calc.lib import experiment

    # config.set("DEFAULT_SELECTED_CALCULATORS_SLUGS", [CalculatorSlug.gad7])

    util.h1("New experiment")

    # Gather all local variables (options) into a dictionary
    config = locals()

    # Remove the 'experiment' import from the config
    config.pop("experiment", None)
    config.pop("util", None)

    # Call the experiment function with the gathered options
    experiment.new_experiment(**config)


@experiment_app.command("list")
def list_experiments():
    """
    List all experiments
    """
    from llm_calc.util import util
    from llm_calc.lib import experiment

    util.h1("List experiments")
    experiment.list_experiments()


@experiment_app.command("clear")
def clear_experiments():
    """
    List all experiments
    """
    from llm_calc.util import util
    from llm_calc.lib import experiment

    util.h1("List experiments")
    experiment.clear_experiments()


@experiment_app.command("run")
def run_given_experiment(
    experiment_slug: Annotated[str, typer.Option(help="slug of experiment")] = "last"
):
    """
    List all experiments
    """
    from llm_calc.util import util
    from llm_calc.lib import experiment

    util.h1("Run experiment")

    experiment.load_and_run_experiment(experiment_slug)


# ----------------- MENU VERSION -----------------


def menu_exit():
    exit()


def route(action):
    # from llm_calc.lib.config import DEFAULT_LLM, config_table
    from llm_calc.view.menu.main_menu import MainMenu, MainMenuChoices

    router = dict()
    router[MainMenuChoices.view_config] = view_config
    router[MainMenuChoices.rebuild_database] = rebuild_database
    router[MainMenuChoices.run_tests] = run_tests
    router[MainMenuChoices.interpreter] = interpreter
    router[MainMenuChoices.exit] = menu_exit

    func = router[action]
    func()


@app.command()
def menu():
    """
    Start the main menu
    :return:
    """
    from llm_calc.util import util
    from llm_calc.view.menu.main_menu import MainMenu, MainMenuChoices

    util.title("LLM-Calc")
    main_menu = MainMenu()
    while True:
        action = main_menu.display()
        route(action)


@app.command()
def live():
    """
    Start the main menu
    :return:
    """
    from llm_calc.view.live import LLMDisplay
    from rich.text import Text
    from llm_calc.util import util

    display = LLMDisplay()
    import subprocess
    import select

    # display.start_display()
    with display.live as live:
        while True:
            f = subprocess.Popen(
                ["tail", "-F", "logs/log.txt"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            p = select.poll()
            p.register(f.stdout)
            while True:
                if p.poll(1):
                    display.log(f.stdout.readline())
                util.wait(3)


@experiment_app.command("new_with_display")
def new_experiment_with_display(
    disable_git_warn: Annotated[
        bool, typer.Option(help="Disable prompt to stash")
    ] = False,
    number_of_cases: Annotated[int, typer.Option(help="Number of cases to run")] = None,
    include_only_one_arm: Annotated[
        ArmSlug,
        typer.Option(help="Only include one arm in the run, need to give the " "slug"),
    ] = None,
    verbose: Annotated[bool, typer.Option(help="Enable verbose output")] = False,
    description: Annotated[
        str, typer.Option(help="Description of the experiment")
    ] = None,
    use_last_dataset: Annotated[
        bool,
        typer.Option(
            help="Disable creation of new dataset and use the most recent one in the database"
        ),
    ] = False,
):
    from llm_calc.lib.config import config
    from llm_calc.util import util
    from llm_calc.lib import experiment

    # config.set("DEFAULT_SELECTED_CALCULATORS_SLUGS", [CalculatorSlug.gad7])

    util.h1("New experiment")

    # Gather all local variables (options) into a dictionary
    config = locals()

    # Remove the 'experiment' import from the config
    config.pop("experiment", None)
    config.pop("util", None)

    # Call the experiment function with the gathered options
    with display.live as live:
        experiment.new_experiment(**config)


@app.command()
def logger():
    """
    Start the main menu
    :return:
    """
    from llm_calc.util import util
    from faker import Faker

    fake = Faker()
    i = 0
    while True:
        if i % 10 == 0:
            util.log_warning(fake.name())
        if i % 5 == 0:
            util.log_mini_task(fake.name())
            util.log_error(fake.name())
        util.wait(0.5)
        util.log(fake.name())
        i += 1


if __name__ == "__main__":
    app()
