# Advanced Filtering Guide

## Overview

This fork adds **required words filtering** to ensure you only receive notifications for items that match specific keywords in their title or description.

## How It Works

### The Problem

Vinted's API sometimes returns items that don't match your exact search terms due to:
- Personalization algorithms
- "Related items" recommendations
- Broader matching to show more results

### The Solution

The advanced filter checks **both the title AND description** of each item to ensure all your required keywords are present before sending a notification.

## Filter Logic

For each required word:
- ✅ Must appear in **either** the title **OR** the description
- ✅ Case-insensitive matching (e.g., "Switch" matches "switch")
- ✅ Partial word matching (e.g., "nintendo" matches "Nintendo")

**All required words must be found for the notification to be sent.**

### Example: "Rithum Switch" Query

**Required Words:** `rithum|||switch`

| Item Title | Item Description | Match? | Reason |
|------------|------------------|--------|---------|
| "Rithum Switch Console" | "Brand new" | ✅ Yes | Both words in title |
| "Nintendo Switch" | "By Rithum brand" | ✅ Yes | "switch" in title, "rithum" in description |
| "Magic Mouse" | "Great condition" | ❌ No | Neither word found |
| "Nintendo Switch" | "Great condition" | ❌ No | Only "switch" found, missing "rithum" |
| "Rithum Keyboard" | "USB switch included" | ✅ Yes | "rithum" in title, "switch" in description |

## Configuration

### Adding a Query with Required Words

When adding a new query, you need to specify the required words.

#### Option 1: Using Python Directly

```python
import core

# Add query with required words
core.process_query(
    query="https://www.vinted.nl/catalog?search_text=rithum+switch&order=newest_first",
    name="Rithum Switch",
    required_words="rithum|||switch"  # All words required (AND logic)
)
```

#### Option 2: Modifying the Database Directly

1. Run the application once to create the database
2. Open the database with a SQLite browser
3. Update the `queries` table:

```sql
UPDATE queries
SET required_words = 'rithum|||switch'
WHERE query_name = 'Rithum Switch';
```

#### Option 3: Using the Web UI (if available)

The web UI may need to be updated to support the `required_words` field. Check the web interface for a "Required Words" input field when adding or editing queries.

### Word Separator

Required words are separated by **three pipe characters: `|||`**

Examples:
- Single word: `nintendo`
- Two words: `nintendo|||switch`
- Three words: `apple|||magic|||mouse`
- Four words: `word1|||word2|||word3|||word4`

### Tips for Effective Filtering

1. **Use specific terms**: More specific words = fewer false positives
   - ❌ Bad: `mouse` (too generic)
   - ✅ Good: `magic|||mouse` (more specific)

2. **Include brand names**: If searching for a specific brand
   - Example: `apple|||airpods|||pro`

3. **Combine with search_text**: Use Vinted's search to narrow results, then use required_words to filter further
   - Vinted search: `search_text=rithum+switch`
   - Required words: `rithum|||switch`

4. **Don't over-filter**: Too many required words might miss valid items
   - ❌ Bad: `nintendo|||switch|||oled|||red|||new|||boxed` (too restrictive)
   - ✅ Good: `nintendo|||switch` (broader, catches more variants)

## Compatibility with Other Filters

Required words work **alongside** existing filters:

1. **Newness Filter** (default: 20 minutes)
   - Items must be recently listed
2. **Country Allowlist**
   - Only sellers from specific countries
3. **Banwords Filter**
   - Exclude items containing unwanted words
4. **Required Words Filter** ⭐ NEW
   - Include only items with all required words

**Filter Order:**
```
Item received from Vinted
  ↓
Is it new? (< 20 min old)
  ↓
Already seen before?
  ↓
Seller country allowed?
  ↓
Contains banwords? (EXCLUDE if yes)
  ↓
Contains all required words? (INCLUDE only if yes) ⭐ NEW
  ↓
Send notification ✅
```

## Running Your Forked Application

See [INSTALLATION.md](./INSTALLATION.md) for detailed setup instructions.

## API Changes

### Updated Functions

#### `core.process_query(query, name=None, required_words="")`
- **New parameter:** `required_words` - Words separated by `|||`
- Returns: `(message, is_new_query)`

#### `db.add_query_to_db(query, name=None, required_words="")`
- **New parameter:** `required_words` - Words separated by `|||`

#### `db.update_query_in_db(query_id, query, name, required_words="")`
- **New parameter:** `required_words` - Words separated by `|||`

#### `db.get_required_words(query_id)`
- **New function:** Returns the required_words string for a query

### Database Schema Changes

#### `queries` table
- **New column:** `required_words TEXT DEFAULT ''`

## Troubleshooting

### Not Receiving Any Notifications

1. **Check your required_words**: Are they spelled correctly?
   ```sql
   SELECT id, query_name, required_words FROM queries;
   ```

2. **Test without required_words**: Temporarily clear the filter
   ```sql
   UPDATE queries SET required_words = '' WHERE id = 1;
   ```

3. **Check logs**: Look for items being filtered out
   ```bash
   tail -f logs/vinted_notifications.log
   ```

### Receiving Wrong Items

1. **Verify Vinted's search is correct**: Test the URL in a browser
2. **Add more specific required words**: Narrow down the matches
3. **Use banwords**: Exclude unwanted terms
   ```sql
   UPDATE parameters SET value = 'replica|||fake|||broken' WHERE key = 'banwords';
   ```

### Items Missing Description

Some items on Vinted may not have descriptions. In this case:
- Only the **title** will be checked
- Items without descriptions can still match if all required words are in the title

## Examples

### Example 1: Apple Products Only

```python
core.process_query(
    query="https://www.vinted.nl/catalog?search_text=magic+mouse&order=newest_first",
    name="Apple Magic Mouse",
    required_words="apple|||magic|||mouse"  # All three words required
)
```

### Example 2: Nintendo Switch OLED

```python
core.process_query(
    query="https://www.vinted.nl/catalog?search_text=nintendo+switch&order=newest_first",
    name="Nintendo Switch OLED",
    required_words="nintendo|||switch|||oled"  # Ensures OLED model
)
```

### Example 3: Specific Brand

```python
core.process_query(
    query="https://www.vinted.nl/catalog?search_text=headphones&order=newest_first",
    name="Sony WH-1000XM4",
    required_words="sony|||wh-1000xm4"  # Brand and model
)
```

## Contributing

Found a bug or have a suggestion? Please open an issue on GitHub!

## License

Same as the original Vinted-Notifications project.
