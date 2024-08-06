import re
from pathlib import Path
import shutil

NON_OBFUSCATED_PATH = Path(__file__).parent.parent / "waiting_for_a_flag"
OBFUSCATED_PATH = Path(__file__).parent.parent / "waiting_for_a_flag_obfuscated"

EXCLUSIONS: set[str] = {"x", "y", "z", "reset"}


def add_replacement(replacements: dict[str, str], old: str, new: str) -> bool:
    if old in EXCLUSIONS:
        return False

    if old in replacements:
        return True

    replacements[old] = new
    return True


def obfuscate(script: str) -> str:
    result = []
    replacements = {}
    in_enum = False
    i = 0
    for line in script.split("\n"):
        if line.startswith("enum {"):
            in_enum = True
            continue

        if in_enum:
            if line.startswith("}"):
                in_enum = False
                continue

            x = line.strip().strip(",").split("=")
            if add_replacement(replacements, x[0].strip(), x[1].strip()):
                continue

        if line.startswith("const "):
            x = line.strip().split("=")
            if add_replacement(replacements, x[0].split()[-1].strip(), x[1].strip()):
                continue

        if line.startswith("func "):
            if not line.startswith("func _"):
                if add_replacement(replacements, line.split("(")[0].split()[-1], f"beckett{i}"):
                    i += 1

            for parameter in line.split("(")[1].split(")")[0].split(","):
                parameter = parameter.split(":")[0].strip()

                if parameter == "":
                    continue

                if parameter not in replacements:
                    if add_replacement(replacements, parameter, f"beckett{i}"):
                        i += 1

        if line.strip().startswith("var "):
            if add_replacement(replacements, line.split("=")[0].strip().split("var")[1].strip().split()[0].split(":")[0].strip(), f"beckett{i}"):
                i += 1

        if line.strip().startswith("for "):
            if add_replacement(replacements, line.split("for")[1].strip().split()[0].strip(), f"beckett{i}"):
                i += 1

        if line.strip() == "":
            continue

        for k, v in replacements.items():
            line = re.sub(rf"\b{k}\b", v, line)

        result.append(line)

    return "\n".join(result)


def main() -> None:
    shutil.copytree(NON_OBFUSCATED_PATH, OBFUSCATED_PATH, dirs_exist_ok=True)
    shutil.rmtree(OBFUSCATED_PATH / ".godot")

    for file in ("main.gd", "camera.gd"):
        (OBFUSCATED_PATH / file).write_text(obfuscate((OBFUSCATED_PATH / file).read_text()))


if __name__ == "__main__":
    main()
