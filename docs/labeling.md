## Why this exists
Level 1 needs a target to predict. I chose to classify each food into a food group.
/// The source API has NO food-group field. This label is self-build, not source’s data.

## The groups
   7 real groups plus one catch-all:
   - Meat & fish
   - Fruit & veg
   - Dairy & eggs
   - Grains & bread
   - Sweets
   - Fats & oils
   - Other   (the catch-all, see below)

## The rule (label_foods.py)
Each group owns a list of keywords. A food name is split into whole words, then
matched against the keyword lists in a fixed order.
/// FIRST match wins. The order of the rules is the collision priority. 
Example: a chocolate milk drink hits Sweets before Dairy because Sweets is listed first.
 /// Matching is WHOLE-WORD, not substring. This stops boiled from matching oil.
/// Plurals are strict: bean does not match beans, so both forms are listed.

## The Other catch-all
/// 793 of 2575 foods (about 31%) land in Other.
/// Other holds real miscellany: beverages, condiments, composite dishes.
/// I do NOT chase Other to zero. That would mean inventing fake categories.

## Final counts (2575 total)
Other            793
Meat & fish      553
Fruit & veg      365
Dairy & eggs     331
Grains & bread   247
Sweets           205
Fats & oils       81

/# label_foods.py writes food_groups.csv: two columns, nummer and food_group
/# The join key back to foods.csv is nummer.