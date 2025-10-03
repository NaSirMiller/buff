from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import requests
from typing import Any

from buff.logger_setup import get_logger

logger = get_logger(name=__name__)


ACS5_URL: str = "https://www.census.gov/data/developers/data-sets/acs-5year.html"
ACS1_URL: str = "https://www.census.gov/data/developers/data-sets/acs-1year.html"

app = FastAPI(title="Census API server")


def get_html(url: str) -> str:
    response = requests.get(url)
    status_code: int = response.status_code
    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail=f"Request at {url} failed with status code={status_code}.",
        )
    return response.text


@app.get("/years_available/{acs_id}")
def read_years_available(acs_id: int = 1) -> list[int]:
    """
    Provides the list of years available for a given survey type. Gets the list from the documentation for the ACS1 and ACS5 surveys such that whenever the years surveyed are changed, this can be utilized for a dynamic retrieval of the years you may use.

    Args:
        acs_id (int, optional): The survey identifier, either 1 or 5. Defaults to 1.

    Returns:
        list[int]: Years the specific acs survey can be retrieved for
    """
    acs_html: str
    match acs_id:
        case 1:
            acs_html = get_html(url=ACS1_URL)
        case 5:
            acs_html = get_html(url=ACS5_URL)
        case _:
            raise HTTPException(
                status_code=404,
                detail=f"Invalid acs_id provided. Expected one of 1 or 5, got {acs_id}",
            )
    soup = BeautifulSoup(acs_html, "html.parser")
    headers: list = soup.find_all(["h1"])
    if headers is None:
        raise HTTPException(
            status_code=404,
            detail="There are no h1-headers with found on requested page.",
        )
    matches: list[Any]
    lower_bound: int
    upper_bound: int
    for header in headers:
        matches = re.findall(r"\((.*?)\)", header.get_text())
        print(matches)
        for match in matches:
            try:
                years = match.split("-")
                print(years)
                lower_bound, upper_bound = int(years[0].strip()), int(years[1].strip())
                break  # Only one header with necessary values as of 10/03/2025
            except Exception as e:
                logger.info(
                    f"For matches={matches}, cannot convert to starting and ending year."
                )
    available_years: list[str] = list(range(lower_bound, upper_bound + 1))
    return available_years
