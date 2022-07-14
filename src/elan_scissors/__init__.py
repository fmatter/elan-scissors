"""Top-level package for elan-scissors."""
import logging
import sys
from pathlib import Path
from xml.etree import ElementTree
import colorlog
from pydub import AudioSegment
from slugify import slugify


handler = colorlog.StreamHandler(None)
handler.setFormatter(
    colorlog.ColoredFormatter("%(log_color)s%(levelname)-7s%(reset)s %(message)s")
)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.propagate = True
log.addHandler(handler)

__author__ = "Florian Matter"
__email__ = "florianmatter@gmail.com"
__version__ = "0.0.1"


def get_slice(audio, target_file, start, end, export_format="wav"):
    if not Path(target_file).is_file():
        segment = audio[start:end]
        segment.export(target_file, format=export_format)
    else:
        log.debug(f"File {target_file} exists")


def load_file(file_path, audio_format="wav"):
    if audio_format == "wav":
        return AudioSegment.from_wav(file_path)
    log.error(f"{audio_format} files are not yet supported.")
    sys.exit()


def process_file(filename, audio_file, **kwargs):
    if Path(filename).suffix == ".flextext":
        from_flextext(flextext_file=filename, audio_file=audio_file, **kwargs)
    log.error(f"{Path(filename).suffix} are not yet supported.")
    sys.exit()


def get_text_abbr(text):
    for item in text.iter("item"):
        if item.attrib["type"] == "title-abbreviation":
            return item.text
    return None


def from_flextext(
    flextext_file,
    audio_file,
    out_dir=".",
    text_abbr=None,
    id_func=None,
    slugify_abbr=False,
    export_format="wav",
):  # pylint: disable=too-many-arguments,too-many-locals
    """Args:
    flextext_file (str): Path to a .flextext file.
    audio_file (str): Path to an audio file, likely .wav.
    out_dir (str): Path to the folder where snippets are exported to (default: ``.``).
    text_abbr: What to look for in ``title-abbreviation`` field. If empty, the first text in the file will be used.
    id_func: If you want something other than the FLEx ``segnum`` field.
    slugify_abbr: Whether to slugify text abbreviations (default: ``False``).
    export_format (str): The format to export snippets to (default: ``wav``).

Returns:
    None"""
    log.debug(flextext_file)
    log.debug(audio_file)
    out_dir = Path(out_dir)
    if not id_func:

        def id_func(phrase, abbr, sep="-", backup_no=1):
            for item in phrase.iter("item"):
                if item.attrib["type"] == "segnum":
                    return abbr + sep + item.text
            return f"{abbr}{sep}{backup_no}"

    if not Path(flextext_file).is_file():
        raise ValueError("Please provide a path to a valid source file (.flextext)")

    log.debug("Loading XML")
    tree = ElementTree.parse(flextext_file)
    log.debug("Iterating texts")
    for text in tree.iter("interlinear-text"):
        good = False
        if text_abbr:
            title_abbr = get_text_abbr(text)
            log.debug(title_abbr)
            if title_abbr == text_abbr:
                log.debug(f"Hit: {text_abbr}")
                good = True
            elif not text_abbr:
                log.warning("Found text with no title-abbreviation.")
        else:
            log.info(f"Parsing file {audio_file}, using first text in {flextext_file}")
            good = True
            text_abbr = get_text_abbr(list(tree.iter("interlinear-text"))[0])
        if slugify_abbr:
            text_abbr = slugify(text_abbr)
        if good:
            log.debug(f"{text_abbr}: {audio_file}")
            if not Path(audio_file).is_file():
                raise ValueError("Please provide a path to a valid source file (.wav)")
            audio = load_file(audio_file)
            for i, phrase in enumerate(text.iter("phrase")):
                phrase_id = id_func(phrase, text_abbr, backup_no=i)
                if "begin-time-offset" not in phrase.attrib:
                    raise ValueError(
                        f"Phrase {phrase_id} in {text_abbr} in {flextext_file} has no [begin-time-offset] value."
                    )
                start = int(phrase.attrib["begin-time-offset"])
                end = int(phrase.attrib["end-time-offset"])
                get_slice(
                    audio=audio,
                    target_file=out_dir / f"{phrase_id}.{export_format}",
                    start=start,
                    end=end,
                    export_format=export_format,
                )
            sys.exit()
    log.error(f"No text with abbreviation {text_abbr} found in file {flextext_file}")
