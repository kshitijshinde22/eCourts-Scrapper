import argparse
from scraper import ECourtsScraper
from datetime import datetime, timedelta

def main():
    parser = argparse.ArgumentParser(description="eCourts Cause List Scraper")
    parser.add_argument("--state", required=True)
    parser.add_argument("--district", required=True)
    parser.add_argument("--complex", required=True)
    parser.add_argument("--court", help="Optional, single court code")
    parser.add_argument("--date", help="DD/MM/YYYY or today/tomorrow", default="today")
    parser.add_argument("--all", action="store_true", help="Download all courts in complex")
    args = parser.parse_args()

    scraper = ECourtsScraper(headless=True)

    if args.date.lower() == "today":
        date_str = datetime.today().strftime("%d/%m/%Y")
    elif args.date.lower() == "tomorrow":
        date_str = (datetime.today() + timedelta(days=1)).strftime("%d/%m/%Y")
    else:
        date_str = args.date

    if args.all:
        results = scraper.download_all_courts(args.state, args.district, args.complex, date_str)
        for r in results:
            print(r)
    else:
        if not args.court:
            print("Please provide --court argument or use --all")
        else:
            res = scraper.download_cause_list(args.state, args.district, args.complex, args.court, date_str)
            print(res)

    scraper.close()

if __name__ == "__main__":
    main()
