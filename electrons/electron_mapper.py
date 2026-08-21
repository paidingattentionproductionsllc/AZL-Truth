# AZL Electron Query Mapper
# Usage: python electron_mapper.py <electron_number>

import sys
from azl_electrons import electron_to_azl

if __name__ == "__main__":
    if len(sys.argv)!= 2:
        print("Usage: python electron_mapper.py <electron_number>")
        sys.exit(1)
    
    e_num = sys.argv[1]
    result = electron_to_azl(e_num)
    print(json.dumps(result, indent=2))
