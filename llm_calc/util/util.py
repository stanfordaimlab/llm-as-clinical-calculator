###################################################################################
# ALEX'S UTILITIES
#
# alternatively
# url = "https://alx.gd/util"
# with httpimport.remote_repo(url):
#   import util
#
# poetry add pandas tabulate rich lxml sqlalchemy sqlalchemy pymysql load_dotenv

import datetime
import json
import random
import re
import string
import time

import rich
import tabulate
from IPython.display import clear_output
from lxml import etree
from rich import console
from rich.rule import Rule
from rich.style import Style

console = console.Console()

import sys
from dotenv import load_dotenv

load_dotenv()

import os
import pandas as pd

import inspect

# First import the embed function
from IPython.terminal.embed import InteractiveShellEmbed
from traitlets.config import Config

# random words
from wonderwords import RandomWord

# allow saving / uploading of chart to plotly
import chart_studio.plotly as py
import plotly.figure_factory as ff
import chart_studio.plotly as pfig

from llm_calc.lib.config import config

# Configure the prompt so that I know I am in a nested (embedded) shell
cfg = Config()
prompt_config = cfg.PromptManager
prompt_config.in_template = "N.In <\\#>: "
prompt_config.in2_template = "   .\\D.: "
prompt_config.out_template = "N.Out<\\#>: "

# Messages displayed when I drop into and exit the shell.
banner_msg = (
    "\n**Nested Interpreter:\n"
    "Hit Ctrl-D to exit interpreter and continue program.\n"
    "Note that if you use %kill_embedded, you can fully deactivate\n"
    "This embedded instance so it will never turn on again"
)
exit_msg = "**Leaving Nested interpreter"


# Wrap it in a function that gives me more context:
# TODO: pass inspect.currentframe() in higher order function
def ipsh():
    ipshell = InteractiveShellEmbed(config=cfg, banner1=banner_msg, exit_msg=exit_msg)

    frame = inspect.currentframe().f_back
    msg = "Stopped at {0.f_code.co_filename} at line {0.f_lineno}".format(frame)

    # Go back one level!
    # This is needed because the call to ipshell is inside the function ipsh()
    ipshell(msg, stack_depth=2)


pd.set_option("display.max_colwidth", 70)

ROOT_DIR = os.getenv("PROJECT_ROOT_DIR")
PAPER_DIR = os.path.join(ROOT_DIR, "manuscript")
DATA_DIR = os.path.join(ROOT_DIR, "data")
FIG_DIR = os.path.join(PAPER_DIR, "figures")
global CONSOLE_LOG

# ------ logging-------
import logging

# from loguru import logger
# TODO: add loguru

# check if logs directory exists, if not create it
if not os.path.exists(f"{ROOT_DIR}/logs"):
    os.makedirs(f"{ROOT_DIR}/logs")
# configure logging
logging.basicConfig(
    filename=f"{ROOT_DIR}/logs/log.txt",
    filemode="w",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG,
)


class HiddenPrints:
    """
    A context manager that suppresses stdout for its scope, i.e. any print statements
    that would have been printed to stdout will not be printed while within this context manager.
    with HiddenPrints():
        print("This will not be printed")
    print("This will be printed as before")
    """

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ coding utilities ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #


def var_dump(yourObj):
    """
    Print all the attributes of an object; similar to var_dump in PHP
    """
    from inspect import getmembers
    from pprint import pprint

    pprint(getmembers(yourObj))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ figures ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #


def upload_fig(fig, filename):
    plotly_api_key = os.getenv("PLOTLY_API_KEY")
    plotly_username = os.getenv("PLOTY_USERNAME")
    from chart_studio.tools import set_credentials_file

    # Plotly Chart Studio authentication
    set_credentials_file(username=plotly_username, api_key=plotly_api_key)
    chart_url = py.plot(
        fig, filename=filename, auto_open=False, fileopt="overwrite", sharing="public"
    )
    print(f"View this figure on Plotly: {chart_url})")
    return chart_url


def save_fig(fig, filename, upload=False):

    image_types = ["svg", "png", "pdf"]
    image_sizes = [1, 2, 3]
    for image_type in image_types:
        for image_size in image_sizes:
            full_path = (
                config.FIGURE_PATH
                + "/"
                + image_type
                + "/"
                + filename
                + f"-{image_size}x"
                + "."
                + image_type
            )
            fig.write_image(full_path, scale=image_size)
            print(f"Figure saved to {full_path}")
    if upload:
        upload_fig(fig, filename)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ formatting ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #


def format_sigfigs(number, sig_figs):
    if sig_figs == 1:
        return f'{float(f"{number:.1g}"):g}'
    elif sig_figs == 2:
        return f'{float(f"{number:.2g}"):g}'
    elif sig_figs == 3:
        return f'{float(f"{number:.3g}"):g}'
    elif sig_figs == 4:
        return f'{float(f"{number:.4g}"):g}'
    elif sig_figs == 5:
        return f'{float(f"{number:.5g}"):g}'
    else:
        return "Invalid number of significant figures"


# convert to numeric representation with commas and no decimal
def format_number_non_sigfig(number):
    return f"{int(number):,}"


# strip to plaintext without whitespace
def slugify(istring):
    # first strip html
    istring = str(istring)
    parser = etree.HTMLParser()
    tree = etree.fromstring(istring, parser)
    istring = etree.tostring(tree, encoding="unicode", method="text")

    # make lowercase
    istring = istring.lower()

    # replcae spaces with underscores
    istring = istring.replace(" ", "_")

    # then remove all non-alphanum chars except underscore
    regex = re.compile("[^a-zA-Z0-9]")
    return regex.sub("", istring)


def gen_two_word_slug():
    """
    Generate a two word slug, ex silver-blossom
    :return: str
    """
    r = RandomWord()
    phrase = (
        r.word(include_parts_of_speech=["adjectives"])
        + "-"
        + r.word(include_parts_of_speech=["nouns"])
    )
    slugify(phrase)
    return phrase


# strip to plaintext without whitespace
def strip_all_non_alphanum(istring):
    # first strip html
    istring = str(istring)
    parser = etree.HTMLParser()
    tree = etree.fromstring(istring, parser)
    istring = etree.tostring(tree, encoding="unicode", method="text")

    # make lowercase
    istring = istring.lower()
    # then remove all non-alphanum chars
    regex = re.compile("[^a-zA-Z0-9]")
    return regex.sub("", istring)


def get_root_dir():
    # assumes in the root/utilities folder
    return os.path.dirname(os.path.abspath("../../README.md"))


def get_fig_dir():
    return get_root_dir() + "/manuscript/figures"


def generate_random_string():
    return (
        "".join(random.choice(string.ascii_lowercase) for _ in range(2))
        + "".join(random.choice(string.digits) for _ in range(2))
        + "".join(random.choice(string.ascii_lowercase) for _ in range(2))
        + "".join(random.choice(string.digits) for _ in range(2))
        + "".join(random.choice(string.ascii_lowercase) for _ in range(2))
    )


def wait_rand():
    wait_time = random.randint(1, 3)
    time.sleep(wait_time)


def wait(seconds):
    time.sleep(seconds)


def log_and_print(text):
    logging.info(text)
    print(text)


def log(text):
    logging.info(text)


def get_timestamp():
    timestamp = "{:%Y-%m-%d-T-%H-%M-%S}".format(datetime.datetime.now())
    return timestamp


def printl(text):
    print(text, end="")


def cprint(text):
    clear_output(wait=True)
    print(text, flush=True)


def cr_print(text):
    clear_output(wait=True)
    rich.print(text, flush=True)


def log_and_rich_print(text):
    logging.info(text)
    rich.print(text, flush=True)


def rprint(text):
    rich.print(text, flush=True)


def tprint(text):
    """
    for printing a table
    :param text:
    :return:
    """
    rich.print(f"[bright_black]{text}[/bright_black]", flush=True)


def lp(text):
    log_and_rich_print(text)


def start_log_task(text):
    rich.print(f"[yellow] ◕ {text} [/yellow]", flush=True, end="...")
    logging.info(text)


def log_task(text):
    rich.print(f"[light_steel_blue1] ⦿ {text} [/light_steel_blue1]", flush=True)
    logging.info(text)


def end_log_task():
    rich.print(f"[yellow bold] Done [/yellow bold]", flush=True)
    logging.info("Done")


def log_mini_task(text, text2=None, error_code=0):
    """
    Log a mini task
    :param text:
    :param text2:
    :param error_code:
    :return:

    0 - white
    1 - green
    2 - yellow
    3 - red
    """
    if text2:
        text = text + "...\n" + str(text2)
    if error_code == 0:
        console.log(f" ─── {text} ", style="italic")
    if error_code == 3:
        console.log(f" ─── [red]{text} ", style="italic")
    if error_code == 2:
        console.log(f" ─── [yellow]{text} ", style="italic")
    if error_code == 1:
        console.log(f" ─── [green]{text} ", style="italic")
    logging.info(text)


def log_success(text, e=None):
    text = "✔ " + text
    log_mini_task(text, text2=e, error_code=1)


def print_success(text, e=None):
    text = "✔ " + text
    console.print(text, style="bold green")


def log_message(text, e=None):
    log_mini_task(text, text2=e, error_code=0)


def log_warning(text, e=None):
    text = "✘ WARNING: " + text
    log(text)


def log_error(text, e=None, will_exit=False, will_print=False):
    text = "█ ✘ ERROR: " + text
    if will_print:
        print(f"{text}")
    log(text)
    if will_exit:
        print(f"{text}")
        exit()
    else:
        confirm("Would you like to continue?")


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def tab(df, tbformat="heavy_grid"):
    print(tabulate.tabulate(df, headers="keys", tablefmt=tbformat, showindex=False))


def confirm(prompt):
    return True
    # if not inquirer.confirm(prompt).execute():
    #     rprint("Exiting")
    #     exit()
    # else:
    #     return True


#
# ▁ ▂ ▃ ▄ ▅ ▆ ▇ █ ▉ ▊ ▋
# ▌ ▍ ▎ ▏ ▐ ░ ▒ ▓ ▔
# ▕ ▖ ▗ ▘ ▙ ▚ ▛ ▜ ▝ ▞ ▟
# ─ ━ │ ┃ ┄ ┅ ┆ ┇ ┈ ┉ ┊ ┋
# ┌ ┍ ┎ ┏ ┐ ┑ ┒ ┓ └ ┕ ┖ ┗
# ┘ ┙ ┚ ┛ ├ ┝ ┞ ┟ ┠ ┡ ┢ ┣


### styles

# colors here https://rich.readthedocs.io/en/stable/appendix/colors.html
# medium_violet_red
# medium_purple1
# dark_orange
# gold1
# turquoise2
# navajo_white1
# grey93
# light_steel_blue1

title_style = Style(color="navajo_white1", bold=True, encircle=True)
h1_style = Style(color="navajo_white1", bold=True)
h2_style = Style(color="navajo_white1")
h3_style = Style(color="navajo_white1", dim=True)
inverted_style = Style(color="black", bold=True, bgcolor="navajo_white1")


def hr():
    print(" ")
    rich.print(Rule(style=h2_style))
    print(" ")


def title(m):
    m = "   " + m.upper() + "   "
    m = rich.console.Text(m, style=inverted_style)
    rich.print("\n")
    rich.print(Rule(title=m, characters=" ", style=title_style))


def h1(m):
    m = rich.console.Text(m.upper(), style=h1_style)
    rich.print(Rule(title=m, characters="━", style=h1_style))


def h2(m):
    m = rich.console.Text(m.upper(), style=h2_style)
    rich.print(Rule(title=m, characters="─", style=h2_style))


def h3(m):
    m = rich.console.Text(m.upper(), style=h3_style)
    rich.print(Rule(title=m, characters="┄", style=h3_style))


def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except ValueError as e:
        return False


def coerce_json_decode(json_string) -> dict | bool:
    """
    Coersive JSON decode (no LLMs); removes LLM-formatting and attempts to decode.
    If standard JSON fails to decode, will attempt with dirtyjson and then a sanitize function.
    will either return a dict from the passed string or if all fail, will log an error
    and then return False.
    :param json_string: str
    :return: dict | bool
    """
    import dirtyjson
    import re
    from ofunctions.json_sanitize import json_sanitize as sanitize_json

    # first check that it is not a dict; if it is a dict, log a warning and return it as dict
    if isinstance(json_string, dict):
        log_warning("JSON string is already a dict; returning as a dict.")
        return json_string

    # attempt to stingify
    try:
        json_string = str(json_string)
    except Exception as e:
        log_error(f"Unable to coerce to string. Exception: {str(e)[:100]}.")
        return False

    # ------ Remove common LLM formatting errors

    # basic formatting
    try:
        # Remove leading/trailing whitespace
        json_string = json_string.strip()
        # Remove markdown code block delimiters
        json_string = re.sub(
            r"^```\s*json\s*\n|```\s*$", "", json_string, flags=re.MULTILINE
        )
        # Remove leading whitespace before opening brackets or quotes
        json_string = re.sub(r'(?m)^(\s*["{[])', r"\1", json_string)
    except Exception as e:
        log_warning(f"Basic JSON formatting error. Exception: {str(e)[:100]}.")
        log(f"\n {json_string[:150]}... (truncated) ... {json_string[-150:]}")

    try:
        # Attempt to parse with standard JSON decoder
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        # Log a warning if standard JSON parsing fails
        log_warning(f"JSON decode error \n {e} \n → will attempt with dirtyjson")
    try:
        # Attempt to parse with dirtyjson if standard JSON fails
        return dirtyjson.loads(json_string)
    except Exception as e:
        # Log an error if both parsing attempts fail
        log_warning(f"JSON decode using dirtyjson failed. Exception: {str(e)[:100]}.")
        log(f"\n {json_string[:150]}" f"... (truncated) ... {json_string[-150:]}")
    try:
        # Attempt to sanitize JSON if dirtyjson fails
        sanitized = sanitize_json(json_string)
        return json.loads(sanitized)
    except Exception as e:
        # Log an error if both parsing attempts fail
        log_error(f"JSON decode using santize failed. Exception: {str(e)[:100]}.")
        log(f"\n {json_string[:150]}" f"... (truncated) ... {json_string[-150:]}")
        return False


def coerce_to_valid_json(json_string: str, error_if_unable: bool = False) -> str | bool:
    obj = coerce_json_decode(json_string)
    if obj:
        return json.dumps(obj)
    else:
        if error_if_unable:
            log_error("Unable to coerce to valid JSON")
            return False
        else:
            return json_string


if __name__ == "__main__":
    print("hello world")
