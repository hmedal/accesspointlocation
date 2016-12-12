import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read filenames.')
    parser.add_argument('-d', '--dat', help='the data file', default = "../dat/accessPointData.txt")
    args = parser.parse_args()
    dataFile = args.dat
    
