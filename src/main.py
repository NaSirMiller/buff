from dotenv import load_dotenv
from getpass import getpass
from logger_setup import set_logger, get_logger
from models.sql_client import SQLClient
import os


def main():
    set_logger()
    logger = get_logger(name=__name__)
    load_dotenv()

    # Intialize SQL connection
    sql_client: SQLClient = SQLClient(
        server=os.getenv("SQLSERVER_SERVER"),
        database=os.getenv("SQLSERVER_DATABASE"),
        username=os.getenv("SQLSERVER_USER"),
        password=getpass("Enter SQL password: "),
        driver=os.getenv("SQLSERVER_DRIVER"),
    )

    sql_client.close()

    logger.info("Closing script...")


if __name__ == "__main__":
    main()
