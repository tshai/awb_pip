# my-package-utils

Reusable standalone utilities copied from `appBuilder` into `my_package` (copied, not moved).

## Install from private GitHub repo

```bash
python -m pip install "my-package-utils @ git+https://YOUR_PRIVATE_REPO_URL"
```

## Example usage

```python
from my_package import validate_file_name, extract_json_after_think

ok, message = validate_file_name("about.html")
data = extract_json_after_think("```json\n{\"ok\": true}\n```")
```
