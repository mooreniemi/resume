#!/usr/bin/env python3
"""Convert moderncv LaTeX resume to Markdown."""
import re
import sys


def strip_latex(s):
    s = re.sub(r"\\textsc\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\href\{([^}]*)\}\{([^}]*)\}", r"[\2](\1)", s)
    s = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", s)
    s = re.sub(r"\\textit\{([^}]*)\}", r"*\1*", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"*\1*", s)
    s = s.replace("\\&", "&")
    s = s.replace("\\%", "%")
    s = s.replace("\\#", "#")
    s = s.replace("\\_", "_")
    s = s.replace("~", " ")
    s = re.sub(r"\{\\[a-z]+\s+([^}]*)\}", r"\1", s)
    return s.strip()


def parse_braces(line, start=0):
    """Extract top-level brace groups from a line starting at `start`."""
    groups = []
    i = start
    while i < len(line):
        if line[i] == "{":
            depth = 1
            j = i + 1
            while j < len(line) and depth > 0:
                if line[j] == "{":
                    depth += 1
                elif line[j] == "}":
                    depth -= 1
                j += 1
            groups.append(line[i + 1 : j - 1])
            i = j
        else:
            i += 1
    return groups


def convert(tex_path):
    with open(tex_path) as f:
        lines = f.readlines()

    md = []
    name = ""
    title = ""
    contact = []

    for raw in lines:
        line = raw.strip()

        if line.startswith("%"):
            continue

        if line.startswith("\\firstname{"):
            name = parse_braces(line)[0]
        elif line.startswith("\\familyname{"):
            name += " " + parse_braces(line)[0]
        elif line.startswith("\\title{"):
            title = strip_latex(parse_braces(line)[0])
        elif line.startswith("\\address{"):
            parts = [p for p in parse_braces(line) if p]
            if parts:
                contact.append(" ".join(parts))
        elif line.startswith("\\mobile{"):
            contact.append(parse_braces(line)[0])
        elif line.startswith("\\email{"):
            email = parse_braces(line)[0]
            contact.append(f"[{email}](mailto:{email})")
        elif line.startswith("\\extrainfo{"):
            url = parse_braces(line)[0]
            if url.startswith("http"):
                contact.append(f"[{url}]({url})")
            else:
                contact.append(url)

        elif line.startswith("\\section{"):
            section = strip_latex(parse_braces(line)[0])
            md.append(f"\n## {section}\n")

        elif line.startswith("\\cventry{"):
            args = parse_braces(line)
            # {dates}{title}{org}{location}{grade}{description}
            dates = strip_latex(args[0]) if len(args) > 0 else ""
            job_title = strip_latex(args[1]) if len(args) > 1 else ""
            org = strip_latex(args[2]) if len(args) > 2 else ""
            location = strip_latex(args[3]) if len(args) > 3 else ""
            description = strip_latex(args[5]) if len(args) > 5 else ""

            header = f"### {job_title}"
            if org:
                header += f" | {org}"
            meta_parts = [p for p in [dates, location] if p]
            meta = " | ".join(meta_parts)

            md.append(header)
            if meta:
                md.append(f"*{meta}*\n")
            if description:
                md.append(f"{description}\n")

        elif line.startswith("\\cvitem"):
            args = parse_braces(line)
            label = strip_latex(args[0]) if len(args) > 0 else ""
            text = strip_latex(args[1]) if len(args) > 1 else ""
            if text:
                if label:
                    md.append(f"- **{label}:** {text}")
                else:
                    md.append(f"- {text}")

    header_lines = [f"# {name}"]
    if title:
        header_lines.append(f"**{title}**\n")
    if contact:
        header_lines.append(" | ".join(contact) + "\n")
    header_lines.append("---\n")

    return "\n".join(header_lines + md) + "\n"


if __name__ == "__main__":
    tex_file = sys.argv[1] if len(sys.argv) > 1 else "resume.tex"
    print(convert(tex_file), end="")
