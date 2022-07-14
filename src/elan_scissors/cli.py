"""Console script for elan-scissors."""
import sys
import click
# https://stackoverflow.com/questions/52053491/a-command-without-name-in-click
from click_default_group import DefaultGroup
from elan_scissors import process_file


@click.group(cls=DefaultGroup, default="convert", default_if_no_args=True)
def main():
    pass


@main.command()
@click.argument("src")
@click.argument("target")
@click.option(
    "-a",
    "--text-abbr",
    default=None,
    help="Text abbreviation / ID to be used; if empty, the first text will be used.",
)
@click.option("-o", "--out-dir", default=".", help="Where to export audio snippets to.")
@click.option("-f", "--export-format", default="wav", help="Exported audio format.")
@click.option("-s", "--slugify", default=False, help="Slugify filenames.")
def convert(
    src, target, out_dir, text_abbr, export_format, slugify
):  # pylint: disable=too-many-arguments
    """Extract audio snippets from audio file <TARGET> based on file with time codes <SRC>."""
    process_file(
        filename=src,
        audio_file=target,
        out_dir=out_dir,
        text_abbr=text_abbr,
        export_format=export_format,
        slugify_abbr=slugify,
    )


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
