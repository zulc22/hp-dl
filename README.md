# hp-dl

This is a command-line utility designed to archive all drivers available
for a particular computer, from [HP's official support site][1].

[1]: https://support.hp.com/us-en/drivers

HP's website does allow you to download drivers in bulk, but offers nothing
helpful that exports metadata. You just get a table with driver names and
filenames and a bunch of sp?????.exe files dropped in your Downloads folder,

but it's kind of terrible for the sake of archiving, because then you have to
manually rename every single one of those drivers; and you don't even get the
additional information provided by the individual driver download pages.

This program, as it is now, allows you to specify an ID to a particular HP
system (it's the number at the end of all the support URLs), and download
all available drivers.

In the future I would like to add HTML output that allows you to read all
the metadata, so that you could make an archive of drivers and see all
applicable information like the original site does.

```
% hp-dl --help
Usage: hp-dl [OPTIONS] COMPUTER_ID

  Download an archive of all drivers for an HP computer.

  <computer_id> shows up at the end of the support URLs on HP's website, e.g.
  the 4065899 in the URL 'https://support.hp.com/us-en/product/details/hp-
  compaq-8000-elite-ultra-slim-pc/4065899'.

Options:
  -o, --output-dir DIRECTORY
  -O, --include-out-of-date
  --help                      Show this message and exit.
```