import sys
from gnosis_scan_api import get_block_range

def main() -> None:

    year = int(sys.argv[1])
    month = int(sys.argv[2])
    day = int(sys.argv[3])
    print(get_block_range(year,month,day))


if __name__ == "__main__":
    # sleep time can be set here in seconds
    main()