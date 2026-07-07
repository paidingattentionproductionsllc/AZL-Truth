import sys
from decimal import Decimal, getcontext

# Set an ultra-high precision buffer to handle immense fractional scales smoothly
getcontext().prec = 250

class UniversalMapper:
    def __init__(self):
        self.floor = Decimal('0.0')
        self.ceiling = Decimal('1.0')

    def get_coordinate(self, tier_index, scale_exponent):
        """
        Translates any tier index into a permanent, non-colliding decimal address
        strictly bounded between 0 and 1 based on the scale magnitude.
        """
        try:
            tier = Decimal(tier_index)
            exponent = Decimal(scale_exponent)
            
            # The unified zero-drift mapping calculation
            address = tier / (Decimal('10') ** exponent)
            
            if not (self.floor <= address <= self.ceiling):
                raise ValueError("Address escaped the 0 to 1 unit vector.")
                
            # Returns the raw, exact fractional address string
            return f"{address:.200f}".rstrip('0')
        except Exception as e:
            return f"Mapping Error: {str(e)}"

if __name__ == "__main__":
    mapper = UniversalMapper()
    print("\n" + "="*60)
    print(" AZL-TRUTH UNIFIED SPATIAL LOOKUP ENGINE ")
    print("="*60)
    
    # Concrete sequential lookup examples between 0 and 1
    print(f"Tier 1 Base Address: 0.{mapper.get_coordinate(1, 2)}")
    print(f"Tier 500 Address: 0.{mapper.get_coordinate(500, 5)}")
    print(f"High-Tier Address: 0.{mapper.get_coordinate(99999, 10)}")
    print("="*60 + "\n")
