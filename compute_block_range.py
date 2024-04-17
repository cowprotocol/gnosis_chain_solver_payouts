import sys
from gnosis_scan_api import get_block_range

def main() -> None:

    year = int(sys.argv[1])
    month = int(sys.argv[2])
    day = int(sys.argv[3])
    start_block, end_block = get_block_range(year,month,day)
    print("Start block: " + str(start_block))
    print("End block: " + str(end_block))

if __name__ == "__main__":
    main()