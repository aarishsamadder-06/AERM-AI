import hashlib

from ..schemas import AnalysisResponse, Product, RoutineStep, SkinFinding

SIMULATION_NOTICE = (
    "Simulated Phase 1 result for education only — not a medical diagnosis or a substitute "
    "for professional dermatology advice."
)

PRODUCTS = [
    Product(
        id="barrier-cleanser",
        name="Barrier Balance Cleanser",
        category="cleanser",
        brand="AERM Lab",
        price_inr=699,
        ingredients=["ceramides", "glycerin", "panthenol"],
        concerns=["dryness", "sensitivity", "redness"],
        why="Ceramides and glycerin support a comfortable, hydrated cleanse without over-stripping.",
        usage="Use a small amount morning and evening, then rinse with lukewarm water.",
        sample_data=True, source="AERM Phase 1 sample catalogue", fragrance_free=True, availability="in_stock",
    ),
    Product(
        id="azelaic-serum",
        name="Calm + Clear Serum",
        category="serum",
        brand="AERM Lab",
        price_inr=899,
        ingredients=["azelaic acid", "niacinamide", "allantoin"],
        concerns=["acne", "redness", "dark_spots", "texture"],
        why="Azelaic acid and niacinamide are matched to the simulated concerns while allantoin helps keep the routine gentle.",
        usage="Patch test first; apply 2–3 evenings per week before moisturiser.",
        sample_data=True, source="AERM Phase 1 sample catalogue", fragrance_free=True, availability="in_stock",
    ),
    Product(
        id="hydrating-cream",
        name="Cloud Veil Moisturiser",
        category="moisturizer",
        brand="AERM Lab",
        price_inr=799,
        ingredients=["squalane", "beta-glucan", "hyaluronic acid"],
        concerns=["dryness", "sensitivity", "redness", "texture"],
        why="A simple humectant-and-emollient blend helps replenish moisture and reduce the feel of tightness.",
        usage="Apply after cleansing, morning and evening, adjusting to comfort.",
        sample_data=True, source="AERM Phase 1 sample catalogue", fragrance_free=True, availability="limited",
    ),
    Product(
        id="mineral-spf",
        name="Daily Mineral SPF 30",
        category="sunscreen",
        brand="AERM Lab",
        price_inr=999,
        ingredients=["zinc oxide", "vitamin E"],
        concerns=["dark_spots", "redness", "sensitivity"],
        why="Daily broad-spectrum protection is a foundational step when uneven tone or visible redness is a concern.",
        usage="Apply generously as the last morning step and reapply during extended outdoor time.",
        sample_data=True, source="AERM Phase 1 sample catalogue", fragrance_free=True, availability="in_stock",
    ),
]

# Catalogue entries are deliberately conservative: established brand names are only
# used where the product/ingredient information is reasonably stable; the rest are
# explicitly marked as AERM sample data.
_CATALOGUE = [
    ("gentle-gel-cleanser", "Gentle Gel Cleanser", "Simple", "cleanser", 549, ["glycerin", "panthenol"], ["sensitivity", "dryness"]),
    ("hydrating-cleanser", "Hydrating Facial Cleanser", "CeraVe", "cleanser", 1199, ["ceramides", "hyaluronic acid"], ["dryness", "sensitivity"]),
    ("foaming-cleanser", "Foaming Facial Cleanser", "CeraVe", "cleanser", 1099, ["niacinamide", "ceramides"], ["acne", "texture"]),
    ("low-ph-cleanser", "Low pH Good Morning Gel Cleanser", "COSRX", "cleanser", 850, ["tea tree", "betaine"], ["acne", "texture"]),
    ("oat-cleanser", "Oat Calm Cleanser", "AERM sample", "cleanser", 499, ["oat", "glycerin"], ["redness", "sensitivity"]),
    ("milky-cleanser", "Milky Comfort Cleanser", "AERM sample", "cleanser", 599, ["squalane", "allantoin"], ["dryness", "redness"]),
    ("barrier-cleanser-plus", "Barrier Rescue Cleanser", "AERM sample", "cleanser", 699, ["ceramides", "cholesterol"], ["dryness", "sensitivity"]),
    ("daily-moisturizer", "Daily Moisturizing Lotion", "CeraVe", "moisturizer", 1399, ["ceramides", "hyaluronic acid"], ["dryness", "sensitivity"]),
    ("simple-light-moisturizer", "Hydrating Light Moisturiser", "Simple", "moisturizer", 575, ["glycerin", "vitamin B5"], ["dryness", "redness"]),
    ("snail-cream", "Advanced Snail 92 All in One Cream", "COSRX", "moisturizer", 1450, ["snail mucin", "hyaluronic acid"], ["dryness", "redness"]),
    ("gel-cream", "Water Bank Blue Hyaluronic Gel Moisturizer", "Laneige", "moisturizer", 2500, ["hyaluronic acid", "squalane"], ["dryness", "texture"]),
    ("barrier-balm", "Barrier Cloud Balm", "AERM sample", "moisturizer", 749, ["squalane", "beta-glucan"], ["dryness", "sensitivity"]),
    ("calm-cream", "Calm Skin Cream", "AERM sample", "moisturizer", 649, ["colloidal oatmeal", "allantoin"], ["redness", "sensitivity"]),
    ("night-cream", "Overnight Comfort Cream", "AERM sample", "moisturizer", 899, ["ceramides", "panthenol"], ["dryness", "redness"]),
    ("anthelios", "Anthelios UVmune SPF50+", "La Roche-Posay", "sunscreen", 1899, ["mexoryl", "glycerin"], ["redness", "dark_spots"]),
    ("biore-spf", "UV Aqua Rich Watery Essence SPF50+", "Bioré", "sunscreen", 1399, ["hyaluronic acid", "royal jelly"], ["dark_spots", "texture"]),
    ("minimalist-spf", "Light Fluid SPF 50", "Minimalist", "sunscreen", 599, ["uv filters", "vitamin E"], ["dark_spots", "redness"]),
    ("mineral-spf-50", "Mineral Shield SPF 50", "AERM sample", "sunscreen", 899, ["zinc oxide", "vitamin E"], ["redness", "sensitivity"]),
    ("tinted-spf", "Everyday Tinted SPF 40", "AERM sample", "sunscreen", 799, ["iron oxides", "zinc oxide"], ["dark_spots", "redness"]),
    ("daily-spf-gel", "Daily Shield Gel SPF 50", "AERM sample", "sunscreen", 699, ["niacinamide", "uv filters"], ["acne", "dark_spots"]),
    ("niacinamide", "Niacinamide 10% + Zinc 1%", "The Ordinary", "serum", 750, ["niacinamide", "zinc PCA"], ["acne", "texture"]),
    ("azelaic-acid", "Azelaic Acid 10%", "The Ordinary", "serum", 1050, ["azelaic acid", "squalane"], ["acne", "redness", "dark_spots"]),
    ("snail-mucin", "Advanced Snail 96 Mucin Power Essence", "COSRX", "serum", 1250, ["snail mucin", "betaine"], ["dryness", "redness"]),
    ("hyaluronic-serum", "Hyaluronic Acid 2% + B5", "The Ordinary", "serum", 850, ["hyaluronic acid", "panthenol"], ["dryness", "sensitivity"]),
    ("vitamin-c", "10% Vitamin C + E + Ferulic", "Minimalist", "serum", 699, ["vitamin C", "ferulic acid"], ["dark_spots", "texture"]),
    ("tranexamic", "Tranexamic 3% Serum", "Minimalist", "serum", 699, ["tranexamic acid", "niacinamide"], ["dark_spots", "redness"]),
    ("calm-serum", "Calm Barrier Serum", "AERM sample", "serum", 799, ["beta-glucan", "allantoin"], ["redness", "sensitivity"]),
    ("retinal-serum", "Beginner Retinal Serum", "AERM sample", "serum", 999, ["retinal", "ceramides"], ["texture", "dark_spots"]),
]
for product_id, name, brand, category, price, ingredients, concerns in _CATALOGUE:
    PRODUCTS.append(Product(
        id=product_id, name=name, category=category, brand=brand, price_inr=price,
        ingredients=ingredients, concerns=concerns,
        why=f"Catalogue match for {', '.join(concerns)} with {', '.join(ingredients)}.",
        match_explanation=f"Selected because it supports {', '.join(concerns)}.",
        usage="Patch test first; introduce one new product at a time and follow the label.",
        sample_data=brand == "AERM sample", source="AERM curated catalogue (verify current retailer listing)",
        fragrance_free=True, availability="in_stock",
    ))


def filter_catalogue(category=None, brand=None, budget_inr=None, ingredient=None, fragrance_free=False, sort="match", concerns=None):
    products = [p for p in PRODUCTS if
        (not category or p.category == category) and
        (not brand or p.brand.lower() == brand.lower()) and
        (budget_inr is None or p.price_inr <= budget_inr) and
        (not ingredient or any(ingredient.lower() in item.lower() for item in p.ingredients)) and
        (not fragrance_free or p.fragrance_free)]
    wanted = set(concerns or [])
    if sort == "price_asc":
        return sorted(products, key=lambda p: (p.price_inr, p.name))
    if sort == "price_desc":
        return sorted(products, key=lambda p: (-p.price_inr, p.name))
    if sort == "name":
        return sorted(products, key=lambda p: p.name)
    return sorted(products, key=lambda p: (-len(wanted.intersection(p.concerns)), p.price_inr, p.name))


def match_products(
    concerns: list[str],
    budget_inr: int | None = None,
    fragrance_free: bool = False,
    preferred_ingredients: list[str] | None = None,
    limit: int = 3,
) -> tuple[list[Product], list[RoutineStep], list[str], list[str]]:
    wanted = set(concerns)
    preferred = {ingredient.lower() for ingredient in (preferred_ingredients or [])}
    filtered = [
        product for product in PRODUCTS
        if (budget_inr is None or product.price_inr <= budget_inr)
        and (not fragrance_free or product.fragrance_free)
    ]
    if not filtered:
        filtered = [product for product in PRODUCTS if not fragrance_free or product.fragrance_free]
    ranked = sorted(
        filtered,
        key=lambda product: (
            len(wanted.intersection(product.concerns)),
            len(preferred.intersection({item.lower() for item in product.ingredients})),
            -product.price_inr,
            product.id,
        ),
        reverse=True,
    )
    selected = ranked[:limit]
    ingredients = sorted({item for product in selected for item in product.ingredients if not preferred or item.lower() in preferred})
    if not ingredients:
        ingredients = sorted({item for product in selected for item in product.ingredients})[:5]
    routine = [
        RoutineStep(time="morning", step="Protect", action="Cleanse, moisturise, and apply SPF.", rationale="A simple barrier-first morning routine supports consistency and daily sun protection."),
        RoutineStep(time="evening", step="Restore", action="Cleanse, use one matched treatment if appropriate, then moisturise.", rationale="Introducing one active at a time makes it easier to observe comfort and response."),
    ]
    explanations = [f"{product.name} matches {len(wanted.intersection(product.concerns))} selected concern(s) at ₹{product.price_inr}." for product in selected]
    return selected, routine, ingredients, explanations


def simulate_analysis(
    images: list[tuple[str, bytes]],
    budget_inr: int | None = None,
    fragrance_free: bool = False,
) -> AnalysisResponse:
    digest = hashlib.sha256(
        b"".join(name.encode("utf-8") + b"\0" + content for name, content in images)
    ).digest()
    options = [
        ("Calm baseline", "The submitted views look broadly calm, with a few routine-level signals to monitor.", "low", ["dryness", "sensitivity"]),
        ("Texture + congestion signals", "The simulated read noticed texture and congestion patterns worth addressing gently.", "medium", ["acne", "texture"]),
        ("Uneven tone signals", "The simulated read noticed visible tone variation; consistent barrier care and sun protection are sensible next steps.", "medium", ["dark_spots", "redness"]),
    ]
    label, summary, severity, concerns = options[digest[0] % len(options)]
    confidence = round(0.74 + digest[1] / 2550, 2)
    return AnalysisResponse(
        finding=SkinFinding(label=label, confidence=confidence, severity=severity, summary=summary),
        observations=[
            "Front, left, and right views were compared in memory for consistent visible patterns.",
            "Lighting and framing can change how skin texture and tone appear, so treat this as a starting point.",
            SIMULATION_NOTICE,
        ],
        recommendations=[
            "Keep the routine simple for the next 7 days: cleanse, moisturise, and use SPF in the morning.",
            "Introduce only one new active at a time and patch test before applying it broadly.",
            "Stop if a product stings persistently, and speak with a qualified clinician for painful or worsening symptoms.",
        ],
        products=match_products(concerns, budget_inr=budget_inr, fragrance_free=fragrance_free)[0],
        views=["front", "left", "right"],
        detected_concerns=concerns,
        matched_ingredients=match_products(concerns, budget_inr=budget_inr, fragrance_free=fragrance_free)[2],
        rationale=[
            "The simulated concern set is selected deterministically from the submitted image bytes.",
            "Product matches prioritize concern overlap, then respect the supplied budget and fragrance preference.",
        ],
        routine=match_products(concerns, budget_inr=budget_inr, fragrance_free=fragrance_free)[1],
        simulation_notice=SIMULATION_NOTICE,
    )
