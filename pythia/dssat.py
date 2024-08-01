import logging
import multiprocessing as mp
import os
import subprocess

from typing import List
from multiprocessing.pool import Pool
from pythia.plugin import PluginManager
from pythia.plugin.hooks import PostRunPixelFailedHookPayload, PostRunPixelSuccessHookPayload, PostRunAllHookPayload

async_error = False


def _run_dssat(details, config, plugins: PluginManager) -> (str, str, bytes, bytes, int):
    logging.debug("Current WD: {}".format(os.getcwd()))
    run_mode = "A"
    if "run_mode" in config["dssat"]:
        run_mode = config["dssat"]["run_mode"].upper()
    command_string = "cd {} && {} {} {}".format(
        details["dir"], config["dssat"]["executable"], run_mode, details["file"]
    )
    # print(".", end="", flush=True)
    dssat = subprocess.Popen(
        command_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = dssat.communicate()
    # print("+", end="", flush=True)

    error_count = len(out.decode().split("\n")) - 1

    if error_count > 0:
        plugins.notify_hook(PostRunPixelFailedHookPayload(details, out, err, dssat.returncode))
    else:
        plugins.notify_hook(PostRunPixelSuccessHookPayload(details, out, err, dssat.returncode))

    return details["dir"], details["file"], out, err, dssat.returncode


def _generate_run_list(config) -> List[{"dir": str, "file": str}]:
    runlist = []
    for root, _, files in os.walk(config.get("workDir", "."), topdown=False):
        batch_mode = config["dssat"].get("run_mode", "A") in {
            "B",
            "E",
            "F",
            "L",
            "N",
            "Q",
            "S",
            "T",
            "Y",
        }
        target = None
        if batch_mode:
            target = config["dssat"].get("batch_file", None)
        else:
            target = config["dssat"].get("filex", None)
        for name in files:
            if target is not None:
                if name == target:
                    runlist.append({"dir": root, "file": name})
            else:
                if batch_mode:
                    if name.upper().startswith("DSSBATCH"):
                        runlist.append({"dir": root, "file": name})
                else:
                    if name.upper().endswith("X"):
                        runlist.append({"dir": root, "file": name})
    return runlist


def display_async(details):
    loc, xfile, out, error, retcode = details
    error_count = len(out.decode().split("\n")) - 1
    if error_count > 0:
        logging.warning(
            "Check the DSSAT summary file in %s. %d failures occured\n%s",
            loc,
            error_count,
            out.decode()[:-1],
        )
        print("X", end="", flush=True)
        async_error = True
    else:
        print(".", end="", flush=True)


def silent_async(details):
    loc, xfile, out, error, retcode = details
    error_count = len(out.decode().split("\n")) - 1
    if error_count > 0:
        logging.warning(
            "Check the DSSAT summary file in %s. %d failures occured\n%s",
            loc,
            error_count,
            out.decode()[:-1],
        )
        async_error = True


def execute(config, plugins: PluginManager):
    pool_size = config.get("cores", mp.cpu_count())
    run_list = _generate_run_list(config)
    with Pool(processes=pool_size) as pool:
        for details in run_list:  # _generate_run_list(config):
            if config["silence"]:
                pool.apply_async(_run_dssat, (details, config, plugins), callback=silent_async)
            else:
                pool.apply_async(_run_dssat, (details, config, plugins), callback=display_async)
        pool.close()
        pool.join()

    if async_error:
        print(
            "\nOne or more simulations had failures. Please check the pythia log for more details"
        )

    plugins.notify_hook(PostRunAllHookPayload(run_list))
