import argparse

#test

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read filenames.')
    parser.add_argument('-d', '--dat', help='the data file', default = "../dat/accessPointData.txt")
    parser.add_argument('-p', '--params', help='the parameters file', default="../dat/params.json")
    args = parser.parse_args()
    dataFile = args.dat
    paramsFile = args.params
    
