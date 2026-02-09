# 🚀 Fork Enhancements

## What's New in This Fork

This fork adds **Advanced Keyword Filtering** to the original Vinted-Notifications application, solving the problem of receiving too many irrelevant notifications.

### The Problem

When monitoring Vinted searches like "Rithum Switch", you might receive notifications for items that:
- ❌ Only contain one of the words ("Switch" but not "Rithum")
- ❌ Don't contain any of your search terms at all
- ❌ Are recommended by Vinted's algorithm but don't match your criteria

This happens because Vinted's API sometimes returns personalized or related items that don't exactly match your search query.

### The Solution

This fork adds **required words filtering** that checks both the title AND description of each item before sending a notification.

## 🎯 Key Features

### 1. Required Words Filter

Specify words that **must** be present in either the title or description:

```python
required_words = "rithum|||switch"  # Both words required
```

- ✅ All specified words must be present
- ✅ Words can be in title OR description
- ✅ Case-insensitive matching
- ✅ Works alongside existing filters (banwords, country allowlist)

### 2. Description Field Support

Items now include description data:
- Extracted from Vinted's API
- Available for filtering
- Fallback to empty string if not available

### 3. Flexible Configuration

Set required words per query:
- Different filters for different searches
- Optional (leave empty to allow all items)
- Easy to update via database or API

## 📊 Comparison

| Feature | Original | This Fork |
|---------|----------|-----------|
| Monitors Vinted searches | ✅ | ✅ |
| Telegram notifications | ✅ | ✅ |
| RSS feed | ✅ | ✅ |
| Country filtering | ✅ | ✅ |
| Banwords (negative filter) | ✅ | ✅ |
| **Required words (positive filter)** | ❌ | ✅ NEW |
| **Description field filtering** | ❌ | ✅ NEW |
| **Per-query keyword rules** | ❌ | ✅ NEW |

## 🔧 Technical Changes

### Modified Files

1. **`pyVintedVN/items/item.py`**
   - Added `description` field to Item class
   - Extracts description from API response

2. **`core.py`**
   - Added `contains_required_words()` function
   - Updated `clear_item_queue()` to apply required words filter
   - Updated `process_query()` to accept required_words parameter

3. **`db.py`**
   - Added `get_required_words()` function
   - Updated `add_query_to_db()` to support required_words
   - Updated `update_query_in_db()` to support required_words
   - Updated `get_queries()` to include required_words

4. **`initial_db.sql`**
   - Added `required_words` column to queries table

5. **`migrations/1.0.5.4_1.0.5.5.sql`**
   - Migration to add required_words column to existing databases

### New Files

1. **`ADVANCED_FILTERING.md`**
   - Comprehensive guide on using the required words filter
   - Examples and best practices
   - Troubleshooting tips

2. **`INSTALLATION.md`**
   - Step-by-step installation guide
   - Configuration instructions
   - Running in background (systemd/screen/tmux)

3. **`FORK_CHANGES.md`** (this file)
   - Summary of changes
   - Migration guide

## 📈 Usage Example

### Before (Original)

```python
# Add query
core.process_query(
    query="https://www.vinted.nl/catalog?search_text=rithum+switch&order=newest_first",
    name="Rithum Switch"
)

# Problem: Receives notifications for ALL items Vinted returns,
# including "Nintendo Switch", "Apple Products", etc.
```

### After (This Fork)

```python
# Add query with required words
core.process_query(
    query="https://www.vinted.nl/catalog?search_text=rithum+switch&order=newest_first",
    name="Rithum Switch",
    required_words="rithum|||switch"  # Both words must be present
)

# Result: Only receives notifications for items containing BOTH
# "rithum" AND "switch" in title or description
```

## 🚀 Getting Started

### For New Users

Follow the [INSTALLATION.md](./INSTALLATION.md) guide for complete setup instructions.

Quick start:
```bash
# Clone this fork
git clone https://github.com/YOUR_USERNAME/Vinted-Notifications.git
cd Vinted-Notifications

# Install dependencies
pip install -r requirements.txt

# Run
python vinted_notifications.py
```

### For Existing Users (Upgrading from Original)

1. **Backup your database:**
   ```bash
   cp data/vinted_notifications.db data/vinted_notifications.db.backup
   ```

2. **Switch to this fork:**
   ```bash
   git remote add fork https://github.com/YOUR_USERNAME/Vinted-Notifications.git
   git fetch fork
   git checkout fork/main
   ```

3. **Run to apply migrations:**
   ```bash
   python vinted_notifications.py
   ```

   The new `required_words` column will be added automatically.

4. **Add required words to your existing queries:**
   ```bash
   sqlite3 data/vinted_notifications.db

   # Update queries
   UPDATE queries SET required_words = 'rithum|||switch' WHERE id = 1;
   UPDATE queries SET required_words = 'apple|||magic|||mouse' WHERE id = 2;

   .exit
   ```

## 📚 Documentation

- **[ADVANCED_FILTERING.md](./ADVANCED_FILTERING.md)** - Complete filtering guide with examples
- **[INSTALLATION.md](./INSTALLATION.md)** - Installation and configuration
- **[README.md](./README.md)** - Original project documentation

## 🤝 Contributing

Want to contribute? Here's how:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Known Issues

None currently! If you find a bug, please open an issue.

## 📝 Future Enhancements

Potential improvements:
- [ ] Web UI support for required_words field
- [ ] Regex pattern matching
- [ ] Phrase matching (exact phrases with spaces)
- [ ] OR logic between word groups
- [ ] Minimum word count requirement
- [ ] Integration with AI for intelligent filtering

## 🙏 Credits

- **Original Project:** [Vinted-Notifications](https://github.com/Fuyucch1/Vinted-Notifications) by Fuyucch1
- **Fork Author:** [Your GitHub Username]
- **Inspiration:** Community feedback about too many irrelevant notifications

## 📄 License

Same as the original project - see [LICENSE](./LICENSE) file.

---

**Questions?** Open an issue or check the [documentation](./ADVANCED_FILTERING.md)!

**Happy deal hunting!** 🎉
