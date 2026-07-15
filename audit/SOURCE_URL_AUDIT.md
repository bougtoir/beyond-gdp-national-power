# Source URL and Fabrication Audit

Checked: 2026-07-15

## Scope

The audit scanned the URL fields in `case_source_catalog.csv`, covering the
case-level polity, closure, outcome, and patron sources used to generate the
480-row field-level supplement.

## URL scan

- Unique URLs: 140
- HTTP 200: 38
- HTTP 202: 1
- HTTP 308: 1
- HTTP 403: 94
- HTTP 405: 2
- HTTP 500: 2
- TLS verification errors in the local Python client: 2

The high 403 count is dominated by Britannica and publisher platforms that
block automated clients. A 403, 405, TLS error, or temporary 500 response does
not by itself show that a source is false. The audit therefore distinguished
resolver/access behavior from bibliographic existence.

## Corrections made

- Replaced an unregistered Italian journal DOI string with the University of
  Padua repository record for the exact article:
  `https://www.research.unipd.it/handle/11577/3412606`.
- Replaced a retired U.S. Embassy page with the U.S. Department of State
  historical document recording signature of the 1960 U.S.-Japan security
  treaty:
  `https://history.state.gov/historicaldocuments/frus1958-60v18/d130`.
- Replaced a chapter DOI link that returned 404 at the resolver with the
  Google Books record for the containing scholarly volume:
  `https://books.google.com/books?id=RJ8uGmLb_RcC`.

## Remaining access exceptions

- The handle for *Sparta, Lakonia and the sea* returned HTTP 500 during the
  scan, but the title, handle, thesis description, and publication record were
  independently returned by web search.
- The DOI for the German autarky article returned HTTP 500 at the publisher
  destination, but Crossref returned matching title metadata for
  `10.7868/s3034600225010143`.
- Two Brill pages returned 405 to the automated GET request.
- Two DOI destinations produced local certificate-chain errors. These are
  recorded as access failures, not as successful content verification.

## Fabrication assessment

No catalog entry reviewed in this pass was identified as a definitely invented
publication or fabricated DOI. This finding is narrower than full source
validation:

- Automated accessibility is not proof that an excerpt or coding conclusion is
  correct.
- General reference overviews are reused for polity chronology and do not
  independently validate every project classification.
- The supplement explicitly marks unsupported, contested, contradicted, and
  legacy absence codings rather than converting inaccessible evidence into a
  positive verification claim.
- A complete scholarly validation would require a subject-matter reviewer to
  compare every excerpt and coding decision against the full publication.

No crowd-sourced encyclopedia URL, title, or excerpt is included in the public
source catalog or generated supplement.
