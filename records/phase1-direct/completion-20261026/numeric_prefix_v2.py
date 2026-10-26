"""Repair only the stale Prefix_Value selector; retain v1's zero-check failure."""
import json
import sys
import numeric_isolated_v1 as driver


def main():
    recipe_path = driver.CANDIDATE / "recipe.json"
    if driver.digest(recipe_path) != driver.RECIPE_HASH:
        raise RuntimeError("reviewed recipe changed")
    recipe = json.loads(recipe_path.read_text())
    manifest_path = driver.CANDIDATE / "private-dependency-sources.json"
    if driver.digest(manifest_path) != recipe["private_dependency_manifest_sha256"]:
        raise RuntimeError("dependency manifest changed")
    manifest = json.loads(manifest_path.read_text())
    item = recipe["targets"][1]
    if item["name"] != "prefix_value" or item["argv"][-1] != "--limit-subp=resource_quantities.ads:79":
        raise RuntimeError("unexpected original selector")
    item["argv"][-1] = "--limit-subp=resource_quantities.ads:78"
    driver.OUT = driver.BASE / "numeric-prefix-v2"
    driver.OUT.mkdir(exist_ok=False)
    passed, _ = driver.target(recipe, manifest, item)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
