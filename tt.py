import re
import sys

def parse_to_mermaid(file_path):
    nodes = set()
    edges = []

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()

            hub_match = re.match(r"(start_hub|hub|end_hub):\s+([a-zA-Z0-9_]+)", line)
            if hub_match:
                node_name = hub_match.group(2)
                nodes.add(node_name)

            conn_match = re.match(r"connection:\s+([a-zA-Z0-9_]+)-([a-zA-Z0-9_]+)", line)
            if conn_match:
                src, dst = conn_match.groups()
                edges.append((src, dst))

    mermaid = ["graph LR"]

    for node in sorted(nodes):
        mermaid.append(f'    {node}["{node}"]')

    for src, dst in edges:
        mermaid.append(f"    {src} --> {dst}")

    return "\n".join(mermaid)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    mermaid_output = parse_to_mermaid(input_file)
    print(mermaid_output)


if __name__ == "__main__":
    main()