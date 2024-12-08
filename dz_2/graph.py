import subprocess
import argparse


def get_commit_dependencies(repo_path, branch_name):
    """Получить зависимости коммитов для ветки."""
    cmd = ["git", "-C", repo_path, "log", branch_name, "--pretty=format:%H %P"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    dependencies = {}
    for line in result.stdout.strip().split("\n"):
        commit, *parents = line.split()
        dependencies[commit] = parents
    return dependencies


def generate_mermaid_graph(dependencies):
    """Создать Mermaid-описание графа."""
    lines = ["graph TD"]
    for commit, parents in dependencies.items():
        for parent in parents:
            lines.append(f"  {parent} --> {commit}")
    return "\n".join(lines)


def save_mermaid_to_file(graph_data, output_path):
    """Сохранить Mermaid-описание в файл."""
    with open(output_path, "w") as file:
        file.write(graph_data)


def generate_graph_image(visualizer_path, mermaid_file, output_file):
    """Сгенерировать изображение графа."""
    cmd = [visualizer_path, "-i", mermaid_file, "-o", output_file]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Git dependency graph visualizer.")
    parser.add_argument("--visualizer-path", required=True, help="Path to the graph visualizer (e.g., mmdc).")
    parser.add_argument("--repo-path", required=True, help="Path to the Git repository.")
    parser.add_argument("--output-file", required=True, help="Path to the output PNG file.")
    parser.add_argument("--branch-name", required=True, help="Name of the branch to analyze.")
    args = parser.parse_args()

    # Получение зависимостей
    dependencies = get_commit_dependencies(args.repo_path, args.branch_name)

    # Генерация Mermaid-описания
    mermaid_graph = generate_mermaid_graph(dependencies)
    mermaid_file = "graph.mmd"
    save_mermaid_to_file(mermaid_graph, mermaid_file)

    # Генерация изображения
    generate_graph_image(args.visualizer_path, mermaid_file, args.output_file)
    print(f"Graph successfully saved to {args.output_file}")


if __name__ == "__main__":
    main()
