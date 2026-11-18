"""Build APA 7 in-text citations with plain Python rules. No AI needed.

Citations follow fixed rules, so code gets them right every time. A small
language model is better used for explaining, not formatting.
"""

from dataclasses import dataclass, field
import re

LOCATOR_TYPES = ("none", "page", "paragraph", "timestamp")
MAX_AUTHORS = 20


class CitationError(ValueError):
    """A student-facing explanation of what to fix in the form."""


@dataclass
class Citation:
    parenthetical: str
    narrative: str
    placement: str
    notes: list = field(default_factory=list)


def clean_authors(raw):
    """Split 'Rivera, Chen, and Patel' or 'Rivera; Chen & Patel' into surnames.

    The word "and" only counts as a separator after a comma, so organization
    names such as "Department of Health and Human Services" stay whole.
    """
    names = re.split(r"\s*(?:[,;&\n])\s*", raw.strip())
    names = [re.sub(r"^(?:and|&)\s+", "", name, flags=re.IGNORECASE) for name in names]
    names = [" ".join(name.split()) for name in names if name.strip()]
    if not names:
        raise CitationError("Enter at least one author surname or organization name.")
    if len(names) > MAX_AUTHORS:
        raise CitationError(f"Enter no more than {MAX_AUTHORS} authors.")
    if any(len(name) > 120 for name in names):
        raise CitationError("Each author name must be 120 characters or fewer.")
    return names


def clean_year(raw):
    year = raw.strip().lower().replace(" ", "")
    if year in ("nd", "n.d", "n.d."):
        return "n.d."
    if re.fullmatch(r"\d{4}[a-z]?", year):
        return year
    raise CitationError("Enter a 4-digit year such as 2024 (or 2024a), or n.d. for no date.")


def format_locator(kind, raw):
    value = raw.strip()
    if kind not in LOCATOR_TYPES:
        raise CitationError("Choose a locator type.")
    if kind == "none" or not value:
        return ""
    if len(value) > 40:
        raise CitationError("Keep the locator to 40 characters or fewer.")
    if kind == "page":
        pages = re.split(r"\s*[-–—]\s*", value)
        if len(pages) == 2 and all(pages):
            return f"pp. {pages[0]}–{pages[1]}"  # en dash for a range
        return f"p. {value}"
    if kind == "paragraph":
        return f"para. {value}"
    return value  # timestamp, e.g. 12:34


def author_text(names, joiner):
    """APA 7: one or two authors are both named; three or more use et al."""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} {joiner} {names[1]}"
    return f"{names[0]} et al."


def build_citation(authors, year, locator_kind="none", locator="", quote_words=None):
    names = clean_authors(authors)
    year = clean_year(year)
    locator_text = format_locator(locator_kind, locator)
    notes = []

    parenthetical = f"({author_text(names, '&')}, {year}"
    parenthetical += f", {locator_text})" if locator_text else ")"
    narrative = f"{author_text(names, 'and')} ({year})"

    if quote_words is None:
        placement = ("Paraphrase: put the citation beside the borrowed idea. "
                     "A page number is optional unless your instructor requires one.")
    elif quote_words < 1 or quote_words > 2000:
        raise CitationError("Enter a quote length between 1 and 2,000 words, or leave it blank.")
    elif quote_words >= 40:
        placement = (f"Block quote ({quote_words} words is 40 or more): start it on a new line, "
                     "indent the whole block 0.5 inch, keep it double-spaced, and leave out quotation "
                     f"marks. Put {parenthetical} after the block's final punctuation, with no period after it.")
    else:
        placement = (f"Short quote ({quote_words} words is fewer than 40): keep it in your sentence inside "
                     f"quotation marks, then add {parenthetical} before the sentence's period.")

    if quote_words is not None:
        if not locator_text:
            notes.append("A direct quote needs a page number or another locator, such as a paragraph "
                         "number or timestamp.")
        elif quote_words >= 40:
            narrative += f" … [block quote, no quotation marks] ({locator_text})"
        else:
            narrative += f" … “quoted words” ({locator_text})."
    if len(names) >= 3:
        notes.append("Three or more authors use et al. from the first citation. If two of your sources "
                     "would shorten to the same et al. citation, add surnames until they differ.")
    if year == "n.d.":
        notes.append("n.d. means no date. Check the source for a date before you use it.")
    return Citation(parenthetical, narrative, placement, notes)
