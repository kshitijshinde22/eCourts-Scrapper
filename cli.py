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
    date_str = datetime.today().strftime("%d/%m/%Y") if args.date=="today" else (datetime.today() + timedelta(days=1)).strftime("%d/%m/%Y")
    
    if args.all:
        courts = scraper.get_courts(args.complex)
        for name, code in courts.items():
            print(f"Downloading {name}...")
            res = scraper.download_cause_list(args.state, args.district, args.complex, code, date_str)
            print(res)
    else:
        res = scraper.download_cause_list(args.state, args.district, args.complex, args.court, date_str)
        print(res)

    scraper.close()

if __name__ == "__main__":
    main()
