"""
Package Loading System Simulator
================================
Simulates a package loading system where each package can carry a maximum of 20 kg.
Items are added with weights ranging from 1 to 10 kg.
"""

def get_positive_integer(prompt):
    """Get a positive integer from user with error handling."""
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("Error: Please enter a positive number.")
                continue
            return value
        except ValueError:
            print("Error: Invalid input. Please enter a valid integer.")


def get_item_weight():
    """Get item weight from user with error handling."""
    while True:
        try:
            weight = int(input("Enter the weight of the item (1-10 kg, or 0 to terminate): "))
            
            # Check for termination signal
            if weight == 0:
                return 0
            
            # Validate weight range
            if weight < 1 or weight > 10:
                print("Error: Weight must be between 1 and 10 kg (or 0 to terminate).")
                continue
            
            return weight
        except ValueError:
            print("Error: Invalid input. Please enter a valid integer.")


def main():
    """Main function to run the package loading simulation."""
    
    MAX_PACKAGE_WEIGHT = 20
    
    print("=" * 50)
    print("       PACKAGE LOADING SYSTEM SIMULATOR")
    print("=" * 50)
    print(f"\nMaximum package capacity: {MAX_PACKAGE_WEIGHT} kg")
    print("Item weight range: 1-10 kg")
    print("Enter 0 to terminate early\n")
    
    # Get maximum number of items
    max_items = get_positive_integer("Enter the maximum number of items to be shipped: ")
    
    # Initialize tracking variables
    packages_sent = 0
    total_weight_sent = 0
    current_package_weight = 0
    items_processed = 0
    
    # Track unused capacity per package for finding the max
    package_unused_capacities = []  # List of (package_number, unused_capacity)
    
    print("\n" + "-" * 50)
    print("Start entering item weights:")
    print("-" * 50)
    
    # Process items
    for i in range(max_items):
        weight = get_item_weight()
        
        # Check for termination signal
        if weight == 0:
            print("\nTermination signal received (weight = 0).")
            break
        
        # Check if adding this item would exceed package limit
        if current_package_weight + weight > MAX_PACKAGE_WEIGHT:
            # Send current package
            packages_sent += 1
            unused = MAX_PACKAGE_WEIGHT - current_package_weight
            package_unused_capacities.append((packages_sent, unused))
            total_weight_sent += current_package_weight
            
            print(f"  >> Package {packages_sent} sent! Weight: {current_package_weight} kg, "
                  f"Unused capacity: {unused} kg")
            
            # Start new package with current item
            current_package_weight = weight
        else:
            # Add item to current package
            current_package_weight += weight
        
        items_processed += 1
        print(f"  Item {items_processed} ({weight} kg) added. "
              f"Current package weight: {current_package_weight} kg")
    
    # Send the last package if it has items
    if current_package_weight > 0:
        packages_sent += 1
        unused = MAX_PACKAGE_WEIGHT - current_package_weight
        package_unused_capacities.append((packages_sent, unused))
        total_weight_sent += current_package_weight
        
        print(f"  >> Package {packages_sent} sent! Weight: {current_package_weight} kg, "
              f"Unused capacity: {unused} kg")
    
    # Calculate totals
    total_unused_capacity = (packages_sent * MAX_PACKAGE_WEIGHT) - total_weight_sent
    
    # Find package with most unused capacity
    if package_unused_capacities:
        max_unused_package = max(package_unused_capacities, key=lambda x: x[1])
        max_unused_package_num = max_unused_package[0]
        max_unused_capacity = max_unused_package[1]
    else:
        max_unused_package_num = 0
        max_unused_capacity = 0
    
    # Display final results
    print("\n" + "=" * 50)
    print("              FINAL SUMMARY")
    print("=" * 50)
    print(f"\nNumber of packages sent:      {packages_sent}")
    print(f"Total weight of packages:     {total_weight_sent} kg")
    print(f"Total unused capacity:        {total_unused_capacity} kg")
    
    if packages_sent > 0:
        print(f"\nPackage with most unused capacity:")
        print(f"  Package #{max_unused_package_num} with {max_unused_capacity} kg unused")
    else:
        print("\nNo packages were sent.")
    
    print("\n" + "=" * 50)
    print("Thank you for using the Package Loading System!")
    print("=" * 50)


if __name__ == "__main__":
    main()
