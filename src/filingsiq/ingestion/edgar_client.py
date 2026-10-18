"""Fetch 10-K filings from EDGAR via edgartools.

NOTE: edgartools' API evolves; if an attribute name below has changed,
check the library docs and adjust. Keep this module as the only place
that touches the library so changes stay local.
"""
from dataclasses import dataclass

from edgar import Company, set_identity

from filingsiq.config import settings


@dataclass
class RawFiling:
    accession_no: str
    ticker: str
    form_type: str
    fiscal_year: int | None
    filed_at: str
    url: str
    html: str


def fetch_10ks(ticker: str, years: int = 3) -> list[RawFiling]:
    if not settings.sec_user_agent:
        raise RuntimeError("Set SEC_USER_AGENT in .env (SEC requires it).")
    set_identity(settings.sec_user_agent)

    filings = Company(ticker).get_filings(form="10-K").latest(years)
    if not hasattr(filings, "__iter__"):
        filings = [filings]

    out = []
    for f in filings:
        period = str(getattr(f, "period_of_report", "") or "")
        out.append(
            RawFiling(
                accession_no=f.accession_no,
                ticker=ticker,
                form_type="10-K",
                fiscal_year=int(period[:4]) if period[:4].isdigit() else None,
                filed_at=str(f.filing_date),
                url=getattr(f, "filing_url", "") or "",
                html=f.html() or "",
            )
        )
    return out
