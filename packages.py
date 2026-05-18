# packages.py
# Format: "ID": ("Brand/Type", sheets_per_roll, rolls_per_pack)

package_sizes = {
    # Charmin Ultra Soft/Strong (2-ply)
    "1": ("Charmin Mega (240s)", 240, 6),
    "2": ("Charmin Mega (240s)", 240, 12),
    "3": ("Charmin Mega (240s)", 240, 18),
    "4": ("Charmin Super Mega (360s)", 360, 6),
    "5": ("Charmin Super Mega (360s)", 360, 12),
    "6": ("Charmin Super Mega (360s)", 360, 18),

    # Cottonelle Ultra (2-ply)
    "10": ("Cottonelle Mega (284s)", 284, 6),
    "11": ("Cottonelle Mega (284s)", 284, 12),
    "12": ("Cottonelle Family Mega (325s)", 325, 6),
    "13": ("Cottonelle Family Mega (325s)", 325, 18),

    # Quilted Northern (2-ply / 3-ply)
    "20": ("Quilted Northern Mega (2-ply)", 255, 12),
    "21": ("Quilted Northern Mega (3-ply)", 164, 12),

    # Store Brands (High Volume 2-ply)
    "30": ("Kirkland (Costco) 2-ply", 380, 30),
    "31": ("Member's Mark (Sam's) 2-ply", 235, 45)
}